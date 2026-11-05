# AA Page: backend design #31

- OpenAPI specification writing
- Research how to do authentication and authorization

## Sessions

```YAML
openapi: 3.0.0 # or whatever we're using
info:
  title: Authentication API (session)
  version: 1.0.0

servers:
  - url: # our server

paths:
 /auth/login:
  post:
   summary: Log in
   operationId: loginUser
   requestBody:
    required: true
    content:
     application/json:
      schema: 
       type: object
       required:
         - email
         - password
         - remember_me
       properties:
        email: 
         type: string
         format: email
        password:
         type: string
        remember_me:
         type: boolean 
   responses:
    "200":
     description: successful login
     headers:
      Set-Cookie:
       schema:
        type: string
     content:
      application/json:
       schema:
        $ref: "#/components/schemas/User"
    
    "401":
     description: Invalid email or password
    
 /auth/account:
  get:
   description: returns the account associated with current session
   operationId: getCurrentAccount
   security:
    - sessionCookie: []
   responses:
    "200":
     description: current account returned with success
     content:
      application/json:
       schema:
        $ref: "#/components/schemas/User"
    "401":
     description: missing, invalid or expired session
     
 
 /auth/logout:
  post: 
   description: invalidates the current session and clears its cookie
   operationId: logoutUser
   security:
    - sessionCookie: []
   responses:
    "204":
     description: successful logout
    "401":
     description: missing or invalid session
         
         
components:
 securitySchemes:
  sessionCookie:
   type: apiKey
   in: cookie
   name: session_id
   
 schemas:
  User:
   type: object
   required:
    - id
    - email
    - role
   properties:
    id:
     type: integer
    email:
     type: string
     format: email
    role:
     type: string
     enum:
      - user
      - admin
     
```

### Flow

**On login:**
2. Request with email and password is sent to backend
3. Find user in DB and verify the hash
4. Create a secure and random session ID
5. Save session in DB (session ID hash, user ID and expiry time)
6. Set browser cookie (browser receives the session ID in a cookie)

**On other requests:**

1. Request send
2. Browser automatically includes the session cookie
3. Backend validates the session

- user id, session id, expiry time
- if invalid: 401 Unauthorized

4. For admin-only, checks user role

- if invalid: 403 Forbidden

5. Backend gets the user ID from the session
2. Gets and returns needed data

### Cookies

Attributes:

- `HttpOnly` - browser stores, but never exposes it to `document.cookie` or JS
  APIs
- `Secure` - only send over HTTPS
- `SameSite=Lax` - restricts cross-site sending (helps prevent CSRF)
- `Max-Age`

Cookies need to be:

- **On successful login**: set
- session_id - random and as hash in DB
- httponly
- secure
- max_age -> 14/30 days (with remember me) or 8/12 h in seconds
- **On requests**: read and validated
- **On admin requests**: read, validate and check the role
- **On logout**: invalidate the session and clear the cookie

### Session

1. Generate a secure and random session ID
2. Send original session ID to the browser in `session_id` cookie
3. Store a hash of session ID in the database
4. On requests, has the cookie value and look up the corresponding session
5. Verify that the session exists and has not expired

### Database

```JSON
{     
"session_id_hash": "...",
"user_id": "...",           
"created_at": "...",
"expires_at": "..."
}
```

OR

## JWT

```YAML
openapi: 3.0.0 # or whatever we're using
info:
  title: Authentication API (JWT)

  version: 1.0.0

servers:
  - url: # our server

paths:
 /auth/login:
  post:
   summary: Log in
   operationId: loginUser
   
   requestBody:
    required: true
    content:
     application/json:
      schema: 
       type: object
       required:
         - email
         - password
       properties:
        email: 
         type: string
         format: email
        password:
         type: string
        remember_me:
         type: boolean
         default: false
   responses:
    "200":
     description: successful login. If remember_me is true, the server sets a reftesh-token cookie.
     headers:
      Set-Cookie:
       description: onlt when remember_me is true
       schema: 
        type: string
     content:
      application/json:
       schema:
        type: object
        required:
         - access_token
         - token_type
         - expires_in
        properties:
         access_token:
          type: string
          description: a signed JWT
         token_type:
          type: string
          enum:
           - Bearer
         expires_in:
          type: integer
          description: lifetime in seconds
    "401":
     description: Invalid email or password
    
 /auth/account:
  get:
   description: returns the current account
   operationId: getCurrentAccount
   security:
    - bearerAuth: []
   responses:
    "200":
     description: current account returned with success
     content:
      application/json:
       schema:
        $ref: "#/components/schemas/User"
    "401":
     description: missing, invalid or expired token
     
 /auth/refresh:
  post:
   description: refresh access token
   operationId: refreshAccessToken
   security:
    - refreshCookie: []
   responses:
    "200":
     description: access token refreshed
     headers:
      Set-Cookie:
       schema:
        type: string
       description: sets the replacement refresh token cookie
     content:
      application/json:
       schema:
        type: object
        required:
         - access_token
         - token_type
         - expires_in
        properties:
         access_toke:
           type: string
         token_type:
          type: string
          enum:
           - Bearer
         expires_in:
          type: integer
    "401":
     description: missing, invalid, expired or revoked refresh token
   
  
 /auth/logout:
  post: 
   description: ends current login
   operationId: logoutUser
   security:
    - bearerAuth: []
   responses:
    "204":
     description: successful logout. Server revokes the associated refresh token and clears the refresh-token cookie, if present
    "401":
     description: missing, invalid or expired access token
         
         
components:
 securitySchemes:
  bearerAuth:
   type: http
   scheme: bearer
   bearerFormat: JWT
  refreshCookie:
   type: apiKey
   in: cookie
   name: refresh_token
   
 schemas:
  User:
   type: object
   required:
    - id
    - email
    - role
   properties:
    id:
     type: integer
    email:
     type: string
     format: email
    role:
     type: string
     enum:
      - user
      - admin
     
```

### Flow

**On login:**

1. Receive email and password
2. Find the user and verify the stored password hash
3. Create a signed JWT with claims such as
   - `sub`: user ID
   - `iat`: issued-at time
   - `exp`: expiration time (Unix timestamp)
   - `iss`: issuer
4. Return the token and its lifetime to the client **On requests:**
5. Client sends `Authorization: Bearer <access_token>`
6. Validate JWT signature with `HS256` algorithm and a securely stored key
7. Validates expiry and claims (`exp`, `iss`)
8. If invalid/expired => 401 Unauthorized
9. If valid => identify user (by user ID) and check their permissions (role)
10. If invalid role => 403 Forbidden On logout:
11. Validate access JWT
12. Identify the user and current login session
13. Revoke refresh token by setting `revoked_at`
14. Clear `refresh_token` cookie
15. Frontend deletes stored access token and updates

### JWT

- **Header**: contains metadata (ex. signing algorithm)
- **Payload**: contains claims
- **Signature**: verifies the token's integrity using a secret or private key

### Remember Me

For that we may need access token and a refresh token. **Access token**:
short-lived token sent with API requests.

- validated before granting access
- typically 30-90 minutes or few hours **Refresh token**: obtains new access
  tokens without the user needing to login again.
- issued only when "Remember me" is selected
- stored in `HttpOnly`, `Secure`, `SameSite=Lax` cookies
- set expiration time and invalidate expired tokens
- issue a new refresh token each time the old one is used and invalidate the
  previous one
- allow refresh tokens to be revoked (on logout)

```JSON
// Refresh Token in DB
{
 "id": "...",
 "user_id": "...",
 "token_hash": "...",
 "created_at": "...",
 "expires_at": "...",
 "revoked_at": "..."
}
```

## Hashing

Passwords:

- need to be stored as hashed, which should be done with `bcrypt`
- can be verified using the library's verification functions

## Database

```JSON
{
 "user_id": "...",
 "email": "...@gmail.com",  // unique
 "password_hash": "...",
 "role": "admin"
}
```
