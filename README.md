# Project Title

This project is a Python application that interacts with the TON (Telegram Open Network) blockchain and a MongoDB database.

# Getting Started

Install poetry:

`pip install poetry`

Install dependencies:

`poetry install`

Run the application:

`poetry shell`

`python3 main.py`

# Example of .env file:

```
PAY_ADDRESS="<ton address>"
DB_CLUSTER_NAME='ton_service_db'
DATABASE='mongodb://localhost:27017'
APP_PORT=5002
```

# Example of request to service:

Create invoice:

```
{
	"invoice_id": 4,
	"value": 200
}
```
Answer:
```
{
	"invoice_id": 4,
	"status": "new",
	"value": 200,
	"value_id": 202
}
```

Get invoice:

```
{
	"invoice_id": 4
}
```
Answer:
```
{
	"invoice_id": 4,
	"status": "confirm",
	"value": 200,
	"value_id": 202
}
```
The system has been tested on testnet and is now running on it. to switch to mainnet change line ton_client.py line 65:

`client = TonClient.from_testnet_config(trust_level=0)` to `client = TonClient.from_mainnet_config(trust_level=0)`