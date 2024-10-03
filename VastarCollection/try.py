import requests
import base64

# HDFC Configuration
HDFC_API_KEY = '036D41F236C4106987121D03E4E892'
HDFC_MERCHANT_ID = 'SG988'
HDFC_CLIENT_ID = 'hdfcmaster'
API_SECRET = '235FEFB19884D54AD85B8961A19FE8'

# Encode API key in Base64
encoded_credentials = base64.b64encode(f"{HDFC_API_KEY}:".encode()).decode()

# Set the order ID you want to check
order_id = 'order-8285'
url = f'https://smartgatewayuat.hdfcbank.com/orders/{order_id}'

# Set headers
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'version': '2023-06-30',
    'Content-Type': 'application/x-www-form-urlencoded',
    'x-merchantid': HDFC_MERCHANT_ID,
    'x-customerid': '1'  # Replace with actual customer ID
}

# Make the GET request
response = requests.get(url, headers=headers)

# Print the response
if response.status_code == 200:
    print("Order Status:", response.json())
else:
    print(f"Failed to retrieve order status: {response.status_code} - {response.text}")
