# Login API

## Endpoint
`POST /users/login/`

## Description
Authenticate users with phone number and password. Users must first register using the `register/` endpoint.

## Request Body
```json
{
    "phone": "+998945552233",
    "password": "securepassword123",
    "device_id": "unique_device_identifier"
}
```

## Fields
- `phone` (string, required): Phone number in E164 format (e.g., "+998945552233")
- `password` (string, required): User's password
- `device_id` (string, required): Unique device identifier

## Response

### Success (200 OK)
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "username": "john_doe",
        "phone": "+998945552233",
        "avatar": "http://example.com/media/users/2023/12/avatar.jpg"
    },
    "created": false
}
```

### Error Responses

#### User Not Found (400)
```json
{
    "phone": ["User with this phone number does not exist."]
}
```

#### Invalid Password (400)
```json
{
    "password": ["Invalid password."]
}
```

#### Validation Errors (400)
```json
{
    "phone": ["Phone number is required."],
    "password": ["Password is required."]
}
```

## Usage Flow
1. User must first register using `register/` endpoint
2. Call `login/` with phone and password
3. Use returned tokens for authenticated requests

## Notes
- Users must be registered before they can login
- Each successful login deactivates older device sessions (keeps only the latest 2 devices)
- Tokens include device ID for multi-device session management
- `created` field is always false for login (true only for registration)
