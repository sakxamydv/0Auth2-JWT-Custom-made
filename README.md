# Custom OAuth 2.0 Server (FastAPI)

A lightweight implementation of a custom OAuth 2.0 authorization server built with FastAPI. This project demonstrates how authorization codes and JWT tokens are generated, handled, and exchanged under the hood during a standard OAuth 2.0 Authorization Code Flow.

> **Note:** This repository is currently a work in progress and intended for learning/educational purposes.

---

## What It Does

- **Authorization Endpoint (`GET /authorize`)**: Renders an inline consent screen where users enter credentials to grant third-party application access.
- **Credential Verification (`POST /authorize`)**: Validates mock user credentials, creates a temporary 10-minute authorization code, and redirects back to the client app with the code and state.
- **Token Exchange (`POST /token`)**: Validates the authorization code and client credentials, then issues a signed JWT access token (15-minute expiration).

---

## Tech Stack

- **Framework:** FastAPI
- **Security:** PyJWT, Secrets library
- **Server:** Uvicorn

---

## Getting Started

### 1. Prerequisites

Make sure you have Python 3.9+ installed.

### 2. Installation

Clone the repository and install the dependencies:

```bash
git clone [https://github.com/sakxamydv/0Auth2-JWT-Custom-made.git](https://github.com/sakxamydv/0Auth2-JWT-Custom-made.git)
cd 0Auth2-JWT-Custom-made

pip install fastapi uvicorn pyjwt
