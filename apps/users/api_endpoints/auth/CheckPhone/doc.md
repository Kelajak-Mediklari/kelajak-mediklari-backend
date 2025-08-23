# CheckPhone API

## Endpoint
`POST /users/check-phone/`

## Description
Check if a phone number exists in the system. This endpoint is useful for determining if a user is already registered with a specific phone number.

## Request Body
```json
{
    "phone": "+998945552233"
}
```

## Fields
- `phone` (string, required): Phone number in E164 format (e.g., "+998945552233")

## Response

### Success (200 OK)
```json
{
    "exists": true,
    "phone": "+998945552233"
}
```

### Error Responses

#### Invalid Phone Format (400)
```json
{
    "phone": ["Enter a valid phone number."]
}
```

#### Missing Phone Number (400)
```json
{
    "phone": ["Phone number is required."]
}
```

## Usage Examples

### Check if phone exists
```bash
curl -X POST "http://localhost:8000/users/check-phone/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998945552233"}'
```

Response:
```json
{
    "exists": true,
    "phone": "+998945552233"
}
```

### Check if phone doesn't exist
```bash
curl -X POST "http://localhost:8000/users/check-phone/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998945552234"}'
```

Response:
```json
{
    "exists": false,
    "phone": "+998945552234"
}
```

## Use Cases
- Pre-registration validation
- Checking if a user needs to register or login
- Account recovery flows
- Preventing duplicate registration attempts

## Notes
- This endpoint does not require authentication
- Only checks for active users (not soft-deleted users)
- Returns standardized E164 format in response
- Always returns 200 OK for valid requests (even if phone doesn't exist)
