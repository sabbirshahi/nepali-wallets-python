import json
from typing import Union

from .base import BasePaymentClient, BasePaymentIntent


class KhaltiIntent(BasePaymentIntent):
    def _get_intent_id(self) -> str:
        return self.data.get('pidx')


class KhaltiClient(BasePaymentClient):
    transaction_pin: str
    otp: str
    website_url: str
    return_url: str

    def _get_request_headers(self) -> dict:
        return {
            "Authorization": f"Key {self.secret_key}",
            'Content-Type': 'application/json',
        }

    def _get_request_body(self) -> dict:
        return {
            "public_key": self.public_key,
        }

    def create_intent(
        self,
        amount: int,
        order_id: str,
        order_name: str,
        customer_info: dict,
        amount_breakdown: Union[list, None] = None,
        product_details: Union[list, None] = None

    ) -> KhaltiIntent:
        return KhaltiIntent(
            self.session.post(
                f'{self.base_url}/epayment/initiate/',
                data=json.dumps(
                    {
                        "return_url": self.return_url,
                        "website_url": self.website_url,
                        "amount": amount,  # amount in paisa
                        'purchase_order_id': order_id,
                        "purchase_order_name": order_name,
                        "customer_info": customer_info,
                        "amount_breakdown": amount_breakdown or [],
                        "product_details": product_details or []
                    }
                ),
                headers=self._get_request_headers()
            )
        )

    def complete_payment(self, token: str, confirmation_code: str):
        print("payment completion is automatically handled by the khalti client itself")
        raise NotImplementedError()

    def verify_payment(self, token: str):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.sandbox:
            self.base_url = 'https://a.khalti.com/api/v2'
        else:
            self.base_url = 'https://khalti.com/api/v2'
