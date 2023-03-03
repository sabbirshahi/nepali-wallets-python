import random
from datetime import datetime
from ..connectors import connect_ips_client


class TestConnectIPS:
    def test_nchl_create_intent(self):
        intent = connect_ips_client.create_intent(
            order_id="txn-001", transaction_date="01-01-2023", transaction_currency="NPR",
            transaction_amount=500, reference_id="REF-001", remarks="RMKS-001", particulars="PART-001"
        )
        assert intent[
                   'TOKEN'
               ] == 'aVhqONpT3ObxZs5YxxWC6TQwxSuDGGCfcXbYUjpTMvrJqVsM+0I5i9ItHrZbglORVBV7P/GtbcWbzcQhUAIzktPu1VXkw4' \
                    'nrlCgQja41Qor9a2ENhkJusJX60UL8GwFiyEB8uDFuhsJskGA79103zBVhOv66ozIP4OE8J3kgc9w='

    def test_nchl_payment(self):
        current_time = datetime.now()
        timestamp = int(current_time.timestamp())
        data = connect_ips_client.create_intent(
            order_id=f"{timestamp}",
            transaction_date=current_time.strftime('%d-%m-%Y'),
            transaction_currency="NPR",
            transaction_amount=random.randint(5, 10) * 100,
            reference_id=f"REF-{timestamp}",
            remarks=f"RMKS-{timestamp}",
            particulars=f"PART-{timestamp}"
        )

    def test_verify_nchl(self):
        resp = connect_ips_client.verify_payment(reference_id="823c-1cef6a01f26b", transaction_amount=12300)
        print(resp.json())
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUCCESS"
