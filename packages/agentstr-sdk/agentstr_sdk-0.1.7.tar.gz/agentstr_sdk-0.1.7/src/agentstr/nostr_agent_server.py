import threading
import json
import time
from typing import Any, List, Callable
from pynostr.event import Event
import requests
from agentstr.a2a import AgentCard, ChatInput, agent_router_v2, RouterResponse
from agentstr.nostr_client import NostrClient
from pydantic import BaseModel


class NoteFilters(BaseModel):
    """Filters for Nostr notes."""

    nostr_pubkeys: list[str] | None = None
    nostr_tags: list[str] | None = None
    followers_only: bool = True  # Not implemented
    following_only: bool = False  # Not implemented


class NostrAgentServer:
    """A server that integrates an external agent with Nostr, handling direct messages.

    This server communicates with an external agent (e.g., a chatbot) via an API and
    processes direct messages received over Nostr, with optional payment requirements.
    """
    def __init__(self, nostr_client: NostrClient = None,
                 relays: List[str] = None, private_key: str = None, nwc_str: str = None, agent_url:str = None, chat_url_path: str = '/chat', info_url_path: str = '/info', agent_info: AgentCard = None, agent_callable: Callable[[ChatInput], str] = None,
                 note_filters: NoteFilters = None, router_llm: Any = None):
        """Initialize the agent server. If agent_info and agent_callable are provided, agent_url, chat_url_path, and info_url_path are ignored.

        Args:
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            agent_url: URL of the external agent API (optional).
            chat_url_path: Path to the chat endpoint of the external agent API (optional).
            info_url_path: Path to the info endpoint of the external agent API (optional).
            agent_info: Agent information (optional).
            agent_callable: Callable to handle agent responses (optional).
            note_filters: Filters for listening to Nostr notes (optional).
            router_llm: LLM to use for routing (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.agent_url = agent_url
        self.chat_url_path = chat_url_path
        self.info_url_path = info_url_path
        self.agent_callable = agent_callable or self._chat_http
        self._agent_info = agent_info or self._get_agent_info()
        self.satoshis = self._agent_info.satoshis
        self.note_filters = note_filters
        self.router_llm = router_llm

    def _get_agent_info(self) -> AgentCard:
        """Fetch metadata from the agent API.

        Returns:
            AgentCard containing agent metadata.
        """
        response = requests.get(f"{self.agent_url}{self.info_url_path}", headers={'Content-Type': 'application/json'}).json()
        return AgentCard.model_validate(response)

    def agent_info(self) -> AgentCard:
        """Get the agent's metadata.

        Returns:
            AgentCard containing agent metadata.
        """
        return self._agent_info

    def _chat_http(self, chat_input: ChatInput) -> Any:
        """Send a message to the agent and retrieve the response.

        Args:
            chat_input: The chat input to send to the agent.

        Returns:
            Response from the agent, or an error message.
        """
        request = {'messages': chat_input.messages}
        if chat_input.thread_id:
            request['thread_id'] = chat_input.thread_id
        print(f'Sending request: {json.dumps(request)}')
        response = requests.post(f"{self.agent_url}{self.chat_url_path}", headers={'Content-Type': 'application/json'}, json=request)
        try:
            response.raise_for_status()
            result = response.text.replace('\\n', '\n').strip('"').strip()
        except Exception as e:
            print(f"Error: {e}")
            result = 'Unknown error'
        print(f'Response: {result}')
        return result

    def chat(self, message: str, thread_id: str | None = None) -> Any:
        """Send a message to the agent and retrieve the response.

        Args:
            message: The message to send to the agent.
            thread_id: Optional thread ID for conversation context.

        Returns:
            Response from the agent, or an error message.
        """
        return self.agent_callable(ChatInput(messages=[message], thread_id=thread_id))

    def _handle_paid_invoice(self, event: Event, message: str, invoice: str, router_response: RouterResponse = None):
        """Handle a paid invoice."""
        if router_response:
            skills_used = ', '.join(router_response.skills_used)
            message = f'''I'd like to follow up on our previous exchange:

Your Request:
{message}

Your Response:
{router_response.user_message}

Could you please proceed with the next steps or provide an update on this matter?

Only use the following tools: [{skills_used}]
'''

        print(f'Handling paid invoice')

        def on_success():
            print(f"Payment succeeded for {self.agent_info().name}")
            result = self.chat(message, thread_id=event.pubkey)
            response = str(result)
            print(f'On success response: {response}')
            self.client.send_direct_message_to_pubkey(event.pubkey, response, expect_response=False)


        def on_failure():
            response = "Payment failed. Please try again."
            print(f"On failure response: {response}")
            self.client.send_direct_message_to_pubkey(event.pubkey, response, expect_response=False)

        thr = threading.Thread(
            target=self.client.nwc_client.on_payment_success,
            kwargs={'invoice': invoice, 'callback': on_success, 'timeout': 900, 'unsuccess_callback': on_failure}
        )
        thr.start()


    def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        if message.strip().startswith('{') or message.strip().startswith('['):
            print(f'Ignoring JSON messages')
            return
        elif message.strip().startswith('lnbc') and ' ' not in message.strip():
            print(f'Ignoring lightning invoices')
            return
        message = message.strip()
        invoice = None
        router_response = None
        print(f"Request: {message}")
        try:
            response = None
            cost_sats = None
            if self.router_llm:
                router_response = agent_router_v2(message, self.agent_info(), self.router_llm, thread_id=event.pubkey)
                response = router_response.user_message
                if router_response.can_handle:
                    cost_sats = router_response.cost_sats
                else:
                    self.client.send_direct_message_to_pubkey(event.pubkey, response, expected_response=False)
                    return

            cost_sats = cost_sats or self.satoshis
            print(f'Cost sats: {cost_sats}')
            if cost_sats > 0:
                invoice = self.client.nwc_client.make_invoice(amt=cost_sats, desc=f"Payment for {self.agent_info().name}")
                if response is not None:
                    response = f'{response}\n\nPlease pay {cost_sats} sats: {invoice}'
                else:
                    response = invoice
            else:
                result = self.chat(message, thread_id=event.pubkey)
                response = str(result)
        except Exception as e:
            # print traceback
            import traceback
            print(f'Exception in direct message callback: {e}')
            print(traceback.format_exc())
            response = f'Error in direct message callback: {e}'
        print(f'Response: {response}')
        time.sleep(0.1)
        self.client.send_direct_message_to_pubkey(event.pubkey, response, expect_response=False)
        if invoice:
            print(f'Handling paid invoice')
            self._handle_paid_invoice(event, message, invoice, router_response)


    def _note_callback(self, event: Event):
        """Handle incoming notes that match the filters.
        
        Args:
            event: The Nostr event containing the note.
        """
        try:
            content = event.content
            print(f"Received note from {event.pubkey}: {content}")
            
            router_response = agent_router_v2(content, self.agent_info(), self.router_llm, thread_id=event.pubkey)
            print(f"Router response: {router_response.model_dump()}")

            if router_response.can_handle:
                # Formulate and send direct message to the user
                response = router_response.user_message

                if router_response.cost_sats > 0:
                    invoice = self.client.nwc_client.make_invoice(amt=router_response.cost_sats, desc=f"Payment to {self.agent_info().name}")
                    response = f'{response}\n\nPlease pay {router_response.cost_sats} sats: {invoice}'
                    self._handle_paid_invoice(event, content, invoice, router_response)

                time.sleep(0.1)
                self.client.send_direct_message_to_pubkey(event.pubkey, response)
            
        except Exception as e:
            print(f"Error processing note: {e}")

    def start(self):
        """Start the agent server, updating metadata and listening for direct messages and notes."""
        thr = threading.Thread(
            target=self.client.update_metadata,
            kwargs={'name': 'agent_server', 'display_name': self.agent_info().name, 'about': self.agent_info().model_dump_json()}
        )
        print(f'Updating metadata for {self.client.public_key.bech32()}')
        thr.start()
        time.sleep(1)
        
        # Start note listener if filters are provided (in new thread)
        if self.note_filters is not None:
            print('Starting note listener with filters:', self.note_filters.model_dump())
            thr = threading.Thread(
                target=self.client.note_listener,
                kwargs={
                    'callback': self._note_callback,
                    'pubkeys': self.note_filters.nostr_pubkeys,
                    'tags': self.note_filters.nostr_tags,
                    'followers_only': self.note_filters.followers_only,
                    'following_only': self.note_filters.following_only
                }
            )
            thr.start()
        
        # Start direct message listener
        print(f'Starting message listener for {self.client.public_key.bech32()}')
        self.client.direct_message_listener(callback=self._direct_message_callback)
        
