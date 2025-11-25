import requests
from TokenManager import get_token_manager

token_manager = get_token_manager()

headers = {
    "Authorization": f"Bearer {token_manager.get_token()}",
}

site_name = "digitalitzacio-InstitutionalStrengthening"
tenant_domain = "iciq.sharepoint.com"

url = f"https://graph.microsoft.com/v1.0/sites/{tenant_domain}:/sites/{site_name}:/drives"

print("Requesting drive info from:", url)
r = requests.get(url, headers=headers)
r.raise_for_status()
print(r.json())
