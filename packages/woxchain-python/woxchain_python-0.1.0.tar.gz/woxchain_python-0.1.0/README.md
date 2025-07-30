# Woxchain Python SDK

Official Python SDK for interacting with Woxchain RPC.

## Installation

```bash
pip install woxchain-python
```

## Example Usage

```python
from woxchain.client import WoxClient

client = WoxClient("https://testrpc.woxscan.com")
balance = client.get_balance("0xYourAddressHere")
print("Balance:", balance)
```
