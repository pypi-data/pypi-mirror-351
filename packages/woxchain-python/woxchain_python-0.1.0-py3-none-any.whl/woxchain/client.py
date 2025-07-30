import requests

class WoxClient:
    def __init__(self, rpc_url):
        self.rpc_url = rpc_url

    def get_balance(self, address):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }
        response = requests.post(self.rpc_url, json=payload)
        result = response.json().get('result', '0x0')
        return int(result, 16)
