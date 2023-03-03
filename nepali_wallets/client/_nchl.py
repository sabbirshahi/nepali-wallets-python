import base64
import json
from datetime import date
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from nepali_wallets.client.base import BasePaymentClient, PaymentClientError


class ConnectIPSClient(BasePaymentClient):
    app_id: str
    app_name: str
    app_password: str
    merchant_id: str
    creditor_password: str
    creditor_path: str
    creditor: str

    @property
    def encoded_credentials(self) -> str:
        return base64.urlsafe_b64encode(f'{self.app_id}:{self.app_password}'.encode()).decode()

    def _get_request_headers(self) -> dict:
        return {
            "Authorization": f"Basic {self.encoded_credentials}"
        }

    def _get_request_body(self) -> dict:
        pass

    def _generate_private_key(self) -> RSAPrivateKey:
        with open(
            f"{self.creditor_path}/{self.creditor}",  # path to your pfx file
            "rb") as pfxFile:
            pfxBinData = pfxFile.read()
            privateKey, cert, additionalCerts = pkcs12.load_key_and_certificates(
                pfxBinData, self.creditor_password.encode()
            )
            return privateKey

    def _generate_token(
        self, order_id: str, transaction_date: date,
        transaction_currency: str, transaction_amount: int,
        reference_id: str, remarks: str, particulars: str
    ) -> str:
        token_str = (
            f"MERCHANTID={self.merchant_id},APPID={self.app_id},APPNAME={self.app_name},TXNID={order_id},"
            f"TXNDATE={transaction_date},TXNCRNCY={transaction_currency},TXNAMT={transaction_amount},"
            f"REFERENCEID={reference_id},REMARKS={remarks},PARTICULARS={particulars},TOKEN=TOKEN"
        )
        private_key: RSAPrivateKey = self._generate_private_key()
        signature: base64 = private_key.sign(
            token_str.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def _generate_verify_token(self, order_id: str, transaction_amount: int) -> str:
        token_str: str = f"MERCHANTID={self.merchant_id},APPID={self.app_id},REFERENCEID={order_id},TXNAMT={transaction_amount}"
        private_key: RSAPrivateKey = self._generate_private_key()
        signature: base64 = private_key.sign(
            token_str.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def create_intent(
        self,
        order_id: str,
        transaction_date: str,
        transaction_currency: str,
        transaction_amount: int,
        reference_id: str,
        remarks: str,
        particulars: str
    ) -> dict:
        """
        Returns the intent body so that it can be sent to the client
        Args:
            order_id:
            transaction_date:
            transaction_currency:
            transaction_amount:
            reference_id:
            remarks:
            particulars:

        Returns:
        """
        return {
            "MERCHANTID": self.merchant_id,
            "APPID": self.app_id,
            "APPNAME": self.app_name,
            'TXNID': order_id,
            'TXNDATE': transaction_date,
            'TXNCRNCY': transaction_currency,
            'TXNAMT': transaction_amount,
            'REFERENCEID': reference_id,
            'REMARKS': remarks,
            'PARTICULARS': particulars,
            'TOKEN': self._generate_token(order_id, transaction_date, transaction_currency, transaction_amount,
                                          reference_id, remarks, particulars),
        }

    def complete_payment(self, token: str, confirmation_code: str = None):
        pass

    def verify_payment(self, reference_id: str, transaction_amount: int) -> dict:
        return self.session.post(
            f'{self.base_url}/connectipswebws/api/creditor/validatetxn',
            data=json.dumps({
                "merchantId": self.merchant_id,
                "appId": self.app_id,
                "referenceId": reference_id,
                "txnAmt": transaction_amount,
                "token": self._generate_verify_token(order_id=reference_id, transaction_amount=transaction_amount),
            }),
            headers={**self._get_request_headers(), 'Content-Type': 'application/json'}
        )

    def __init__(self, *args, **kwargs):
        # if len({'app_id', 'app_name', 'merchant_id', 'sandbox', 'app_password'} - set(kwargs.keys())):
        #     raise PaymentClientError
        super().__init__(*args, **kwargs)
        if self.sandbox:
            self.base_url = 'https://uat.connectips.com:7443'
            self.login_url = "https://uat.connectips.com:7443/connectipswebgw/loginpage"
        else:
            self.base_url = 'https://login.connectips.com'
            self.login_url = "https://login.connectips.com/connectipswebgw/loginpage"
