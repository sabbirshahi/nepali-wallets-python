from nepali_wallets.client import KhaltiClient, EsewaClient, ConnectIPSClient
from decouple import config

__all__ = [
    'khalti_client',
    'connect_ips_client',
]

khalti_client = KhaltiClient(
    public_key=config('KHALTI_PUBLIC_KEY'),
    secret_key=config('KHALTI_SECRET_KEY'),
    return_url=config('KHALTI_SUCCESS_URL'),
    website_url=config('KHALTI_FAILURE_URL'),
    sandbox=True
)

connect_ips_client = ConnectIPSClient(
    app_id=config('NCHL_APP_ID'),
    app_name=config('NCHL_APP_NAME'),
    app_password=config('NCHL_APP_PASSWORD'),
    merchant_id=config('NCHL_MERCHANT_ID'),
    creditor_password=config('NCHL_CREDITOR_PASSWORD'),
    creditor_path=config('NCHL_CREDITOR_PATH'),
    creditor=config('NCHL_CREDITOR_SANDBOX'),
    sandbox=config('NCHL_SANDBOX', cast=bool, default=True)
)
