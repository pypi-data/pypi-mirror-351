import json
import uuid
import time
import threading
from typing import List, Callable
from pydantic import BaseModel
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.utils import get_public_key
from websocket import create_connection
from pynostr.event import Event, EventKind
from pynostr.filters import Filters
from pynostr.key import PrivateKey


class DecryptedMessage(BaseModel):
    event: Event
    message: str


class EventRelay(object):
    def __init__(self, relay: str, private_key: PrivateKey):
        self.relay = relay
        self.private_key = private_key
        self.public_key = self.private_key.public_key if self.private_key else None


    def get_events(self, filters: Filters, limit: int = 10, timeout: int = 30, close_on_eose: bool = True) -> List[Event]:
        limit = filters.limit if filters.limit else limit
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        ws = create_connection(self.relay)
        print(f'Sending subscription: {json.dumps(subscription)}')
        ws.send(json.dumps(subscription))
        t0 = time.time()
        events = []
        found = 0
        while time.time() < t0 + timeout and found < limit:      
            response = ws.recv()
            response = json.loads(response)
            print(f"Received full message in get_events: {response}")
            if (len(response) > 2):
                found += 1
                print(f"Received message {found} in get_event: {response[2]}")
                events.append(Event.from_dict(response[2]))
            else:
                if response[0] == 'EOSE':
                    print('Received EOSE in get_events')
                    if close_on_eose:
                        print('Closing connection on EOSE.')
                        break
                print(f"Invalid event: {response}")
        ws.close()

        return events

    def get_event(self, filters: Filters, timeout: int = 30, close_on_eose: bool = True) -> Event:
        events = self.get_events(filters, limit=1, timeout=timeout, close_on_eose=close_on_eose)
        if len(events) > 0:
            return events[0]
        else:
            return None

    def send_event(self, event: Event):
        if not event.sig:
            event.sign(self.private_key.hex())
        response = None
        ws = create_connection(self.relay)
        message = event.to_message()
        print(f'Sending message: {message}')
        ws.send(message)
        response = ws.recv()
        print(f'Send event response: {response}')
        ws.close()
        return response

    def decrypt_message(self, event: Event) -> DecryptedMessage | None:
        if event and event.has_pubkey_ref(self.public_key.hex()):
            rdm = EncryptedDirectMessage.from_event(event)
            rdm.decrypt(self.private_key.hex(), public_key_hex=event.pubkey)
            print(f"New dm received: {event.date_time()} {rdm.cleartext_content}")
            return DecryptedMessage(
                event=event,
                message=rdm.cleartext_content
            )
        return None

    def receive_message(self, author_pubkey: str, timestamp: int = None, timeout: int = 30) -> DecryptedMessage | None:
        authors = [author_pubkey]
        filters = Filters(authors=authors, kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                            pubkey_refs=[self.public_key.hex()], since=timestamp or get_timestamp(), limit=1)
        event = self.get_event(filters, timeout, close_on_eose=False)
        return self.decrypt_message(event)

    def send_receive_message(self, message: str | dict, recipient_pubkey: str, timeout: int = 30, expect_response: bool = True) -> DecryptedMessage | None:
        recipient = get_public_key(recipient_pubkey)
        dm = EncryptedDirectMessage()

        if isinstance(message, dict):
            message = json.dumps(message)

        dm.encrypt(self.private_key.hex(), cleartext_content=message, recipient_pubkey=recipient.hex())
        dm_event = dm.to_event()

        timestamp = dm_event.created_at
        authors = [recipient.hex()]
        filters = Filters(authors=authors, kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                            pubkey_refs=[self.public_key.hex()], since=timestamp, limit=1)
        self.send_event(dm_event)
        if expect_response:
            response = self.get_event(filters, timeout, close_on_eose=False)
            return self.decrypt_message(response)
        return None

    def event_listener(self, filters: Filters, callback: Callable[[Event], None], timeout: int = 0):
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        print(f'Sending note subscription: {json.dumps(subscription)}')
        t0 = time.time()
        ws = create_connection(self.relay)
        ws.send(json.dumps(subscription))
        while timeout == 0 or time.time() < t0 + timeout:      
            response = ws.recv()
            response = json.loads(response)
            if (len(response) > 2):
                print(f"Received message in event_listener: {response[2]}")
                callback(Event.from_dict(response[2]))
            time.sleep(0.1)
        ws.close()

    def direct_message_listener(self, filters: Filters, callback: Callable[[Event, str], None], timeout: int = 0):
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        print(f'Sending DM subscription: {json.dumps(subscription)}')
        t0 = time.time()
        ws = create_connection(self.relay)
        ws.send(json.dumps(subscription))
        while timeout == 0 or time.time() < t0 + timeout:      
            response = ws.recv()
            response = json.loads(response)
            if (len(response) > 2):
                #print(f"Received message in event_listener: {response[2]}")
                response = Event.from_dict(response[2])
                response = self.decrypt_message(response)
                if response:
                    print(f"New dm received: {response.event.date_time()} {response.message}")
                    callback(response.event, response.message)
            time.sleep(0.1)
        ws.close()