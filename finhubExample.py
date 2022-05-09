from dotenv import load_dotenv

load_dotenv()

import os

api_key = os.getenv("FINHUB_API_KEY")  # _SANDBOX")

# symbol lookup
import finnhub

finnhub_client = finnhub.Client(api_key=api_key)

# print(finnhub_client.symbol_lookup("apple"))
# Get stock symbolds from a given exchange eg. US,  L (for LSE)
# print(finnhub_client.stock_symbols("L"))


print(finnhub_client.company_profile2(symbol="MNG.L"))
# print(finnhub_client.general_news("general", min_id=0))
print(finnhub_client.company_news("MNG.L", _from="2022-01-01", to="2022-05-10"))
print(finnhub_client.company_peers("MNG.L"))
