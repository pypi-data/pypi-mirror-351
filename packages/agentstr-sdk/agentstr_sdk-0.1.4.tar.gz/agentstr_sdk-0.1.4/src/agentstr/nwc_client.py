from agentstr.nwc import processNWCstring, tryToPayInvoice, listTx, getBalance, makeInvoice, checkInvoice
from bolt11.decode import decode
import time


class NWCClient(object):
    """
    A client for interacting with Nostr Wallet Connect (NWC) endpoints.
    This class provides methods to manage Lightning Network payments and invoices.

    Args:
        nwc_str (str): The Nostr Wallet Connect connection string.
    """
    def __init__(self, nwc_str: str):
        """
        Initialize the NWC client with a connection string.

        Args:
            nwc_str (str): The Nostr Wallet Connect connection string.
        """
        self.nwc_info = processNWCstring(nwc_str)

    def list_tx(self) -> list:
        """
        List all transactions in the wallet.

        Returns:
            list: A list of transaction objects.
        """
        return listTx(self.nwc_info)['result']['transactions']

    def get_balance(self) -> int:
        """
        Get the current wallet balance in satoshis.

        Returns:
            int: The current wallet balance in satoshis.
        """
        return getBalance(self.nwc_info)['result']['balance']

    def make_invoice(self, amt: int = None, desc: str = None) -> str:
        """
        Create a new Lightning invoice.

        Args:
            amt (int, optional): The amount in satoshis. If not provided, the invoice will be for any amount.
            desc (str, optional): A description for the invoice.

        Returns:
            str: The Lightning invoice string (BOLT11 format).
        """
        return makeInvoice(self.nwc_info, amt=amt, desc=desc)['result']['invoice']

    def check_invoice(self, invoice: str = None, payment_hash: str = None) -> dict:
        """
        Check the status of a Lightning invoice.

        Args:
            invoice (str, optional): The BOLT11 invoice string to check.
            payment_hash (str, optional): The payment hash to check.

        Returns:
            dict: A dictionary containing the invoice status information.
        """
        return checkInvoice(self.nwc_info, invoice=invoice, payment_hash=payment_hash)

    def did_payment_succeed(self, invoice: str = None) -> bool:
        """
        Check if a payment has been successfully settled.

        Args:
            invoice (str, optional): The BOLT11 invoice string to check.

        Returns:
            bool: True if the payment was successfully settled, False otherwise.
        """
        return self.check_invoice(invoice=invoice).get('result', {}).get('settled_at') or 0 > 0

    def try_pay_invoice(self, invoice: str, amt: int = None):
        """
        Attempt to pay a Lightning invoice.

        Args:
            invoice (str): The BOLT11 invoice string to pay.
            amt (int, optional): The amount in satoshis to pay. If not provided, 
                the amount from the invoice will be used.

        Raises:
            RuntimeError: If the provided amount doesn't match the invoice amount,
                         or if no amount is provided and the invoice doesn't specify one.
        """
        decoded = decode(invoice)
        if decoded.amount_msat and amt:
            if decoded.amount_msat != amt * 1000:  # convert to msats
                raise RuntimeError(f'Amount in invoice [{decoded.amount_msat}] does not match amount provided [{amt}]')
        elif not decoded.amount_msat and not amt:
            raise RuntimeError('No amount provided in invoice and no amount provided to pay')
        tryToPayInvoice(self.nwc_info, invoice=invoice, amnt=amt)

    def on_payment_success(self, invoice: str, callback=None, unsuccess_callback=None, timeout: int = 60, interval: int = 5):
        """
        Listen for payment success for a given invoice.

        This method continuously checks for payment success until either the payment
        is confirmed or the timeout is reached.

        Args:
            invoice (str): The BOLT11 invoice string to listen for.
            callback (callable, optional): A function to call when payment succeeds.
            unsuccess_callback (callable, optional): A function to call if payment fails.
            timeout (int, optional): Maximum time to wait in seconds (default: 60).
            interval (int, optional): Time between checks in seconds (default: 5).

        Raises:
            Exception: If the callback function raises an exception.
        """
        start_time = time.time()
        success = False
        while True:
            if self.did_payment_succeed(invoice):
                success = True
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error in callback: {e}")
                        raise e
                break
            if time.time() - start_time > timeout:
                break
            time.sleep(interval)
        if not success:
            if unsuccess_callback:
                unsuccess_callback()


if __name__=='__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    nwc_str = os.getenv('AGENT_NWC_CONN_STR')
    client = NWCClient(nwc_str)
    invoice = client.make_invoice(amt=5, desc='test')
    print(f'Invoice: {invoice}')
    client.on_payment_success(invoice,
                              callback=lambda: print('Payment succeeded'),
                              unsuccess_callback=lambda: print('Payment failed'),
                              timeout=120,)