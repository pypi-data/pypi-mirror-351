import requests
import json
from typing import Any


class SquaredClient:
    """
    Client for interacting with the Squared Inc API.

    This client provides methods to create invoices, verify webhooks,
    and perform other operations with the Squared Inc payment platform.

    Attributes:
        api_key (str): The API key used for authentication with Squared Inc.
        base_url (str): The base URL for the Squared Inc API.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.squaredinc.co/v1"

    def create_invoice(
        self,
        amount: int,
        currency: str,
        title: str = None,
        description: str = None,
        post_paid_text: str = None,
        simulated_invoice: bool = False,
        custom_data: Any = None,
        live_wallet: str = None,
        redirect_url: str = None,
    ):
        """
        Creates a new invoice using the Squared Inc API.

        Args:
            amount (int): The amount to charge in the smallest unit of the currency
                (e.g., cents for USD).
            currency (str): The currency code for the invoice (e.g., 'USD', 'BTC').
            title (str, optional): The title of the invoice. Defaults to None.
            description (str, optional): A description of the invoice. Defaults to None.
            post_paid_text (str, optional): Text to display after payment is complete.
                Defaults to None.
            simulated_invoice (bool, optional): Whether this is a simulated invoice for
                testing. Defaults to False.
            custom_data (Any, optional): Additional custom data to include with the invoice.
                Defaults to None.
            redirect_url (str, optional): URL where to redirect user after payment

        Returns:
            dict: The created invoice data as returned by the API.

        Raises:
            Exception: If the API request fails or returns an error.
        """
        payload = {
            "amount": amount,
            "currency": currency,
            "api_key": self.api_key,
            "title": title,
            "description": description,
            "post_paid_text": post_paid_text,
            "simulated_invoice": simulated_invoice,
            "live_wallet": live_wallet,
            "redirect_url": redirect_url,
        }

        if custom_data is not None:
            payload["custom_data"] = custom_data

        response = requests.post(
            f"{self.base_url}/invoice/create",
            json=payload,
        )
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                raise Exception(error_data)
            except requests.exceptions.JSONDecodeError:
                raise Exception(f"Error: {response.status_code} - {response.text}")

    def verify_webhook(self, webhook: dict, raise_on_invalid: bool = False) -> bool:
        """
        Sends the webhook dict to the /webhook/verify endpoint and returns whether it is verified.

        Args:
            webhook: The webhook payload to verify
            raise_on_invalid: If True, raises an exception when verification fails.
                              If False, returns False when verification fails.

        Returns:
            bool: True if webhook is verified, False otherwise (unless raise_on_invalid is True)

        Raises:
            Exception: If verification fails and raise_on_invalid is True
        """
        # Add API key to the webhook payload
        payload = dict(webhook)
        payload["api_key"] = self.api_key
        response = requests.post(
            f"{self.base_url}/webhook/verify",
            json=payload,
        )
        if response.status_code == 200:
            try:
                data = response.json()
                # The response body is a JSON string inside the 'body' key
                body = json.loads(data.get("body", "{}"))
                verified = data.get("verified", False)
                if not verified and raise_on_invalid:
                    raise Exception("Webhook verification failed")
                return verified
            except (ValueError, KeyError):
                if raise_on_invalid:
                    raise Exception("Malformed response from webhook verify endpoint.")
                return False
        else:
            try:
                error_data = response.json()
                if raise_on_invalid:
                    raise Exception(error_data)
                return False
            except requests.exceptions.JSONDecodeError:
                if raise_on_invalid:
                    raise Exception(f"Error: {response.status_code} - {response.text}")
                return False

    def get_invoice(self, invoice_id: str):
        """
        Retrieves invoice information using the Squared Inc API.

        Args:
            invoice_id (str): The ID of the invoice to retrieve.

        Returns:
            dict: The invoice data as returned by the API.

        Raises:
            Exception: If the API request fails or returns an error.
        """
        payload = {
            "invoice_id": invoice_id,
            "api_key": self.api_key,
        }

        response = requests.post(
            f"{self.base_url}/invoice/get",
            json=payload,
        )
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                raise Exception(error_data)
            except requests.exceptions.JSONDecodeError:
                raise Exception(f"Error: {response.status_code} - {response.text}")
