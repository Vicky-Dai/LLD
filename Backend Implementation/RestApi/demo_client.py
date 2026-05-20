"""Demo script: generate a JWT and exercise the order API."""

from auth import create_access_token

if __name__ == "__main__":
    token = create_access_token("user-001")
    print("Bearer token for local testing:")
    print(token)
    print()
    print("Example curl commands:")
    print('curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/v1/orders')
    print(
        'curl -X POST http://127.0.0.1:8000/api/v1/orders '
        '-H "Authorization: Bearer <token>" '
        '-H "Content-Type: application/json" '
        '-H "Idempotency-Key: demo-key-1" '
        '-d \'{"product_id":"sku-001","quantity":2,"note":"demo"}\''
    )
