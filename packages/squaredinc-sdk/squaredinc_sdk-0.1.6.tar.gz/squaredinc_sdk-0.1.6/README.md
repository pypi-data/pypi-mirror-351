# Squared Inc. SDK

A Python SDK for the Squared Inc. payment processing API.

## Installation

```bash
pip install squaredinc-sdk
```

## Usage

```python
from squaredinc_sdk import SquaredSDK

# Initialize the client
squared = SquaredSDK(api_key="your-api-key")

# Create an invoice
invoice = squared.create_invoice(
    currency="usd",
    amount=20,
    title="Order Title",
    description="Order Description",
    post_paid_text="Thank you message",
)

print(invoice)
```

## Development

### Requirements

- Python 3.7+
- Requests library

Squared Inc. Copyright (c) 2025. All rights reserved. 