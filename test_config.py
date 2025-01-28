from src.config import load_config, get_alpaca_credentials

load_config()
creds = get_alpaca_credentials()
print("Alpaca API Key Present:", bool(creds['api_key']))
print("Alpaca Secret Key Present:", bool(creds['secret_key']))
