"""Example authentication flows and usage."""

import asyncio
import httpx
from typing import Optional

# Demo configuration
API_URL = "http://localhost:8000"
DEMO_EMAIL = "demo@engineeros.io"
DEMO_PASSWORD = "demo1234"


async def demo_login() -> Optional[str]:
    """
    Demonstrate login flow to get JWT token.
    
    Steps:
    1. POST /auth/login with email and password
    2. Receive access_token in response
    3. Use token in Authorization header for subsequent requests
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Login
        login_response = await client.post(
            f"{API_URL}/auth/login",
            json={
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD,
            },
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return None

        token_data = login_response.json()
        access_token = token_data["access_token"]
        user_id = token_data["user_id"]

        print(f"[OK] Login successful")
        print(f"  User ID: {user_id}")
        print(f"  Token: {access_token[:20]}...")

        return access_token


async def demo_authenticated_request(token: str) -> None:
    """
    Demonstrate making authenticated request with JWT token.
    """
    async with httpx.AsyncClient() as client:
        # Use token in Authorization header
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Example: Get current user info
        response = await client.get(
            f"{API_URL}/dev/me",
            headers=headers,
        )

        if response.status_code == 200:
            user_info = response.json()
            print(f"[OK] Authenticated request successful")
            print(f"  User: {user_info['user_id']}")
            print(f"  Email: {user_info['email']}")
            print(f"  Roles: {user_info['roles']}")
        else:
            print(f"[FAIL] Request failed: {response.status_code}")
            print(f"  {response.text}")


async def demo_unauthenticated_request() -> None:
    """
    Demonstrate making unauthenticated request (will fail).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/dev/me")

        if response.status_code != 401:
            print(f"Unexpected status: {response.status_code}")
        else:
            print(f"[OK] Unauthenticated access correctly rejected")
            print(f"  Error: {response.json()['detail']}")


async def demo_rate_limiting() -> None:
    """
    Demonstrate rate limiting protection.
    
    The /health endpoint has a 10 req/min limit.
    """
    async with httpx.AsyncClient() as client:
        print("Testing rate limiting (10 req/min on /health)...")

        success_count = 0
        for i in range(12):
            response = await client.get(f"{API_URL}/health")

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                print(f"  Request {i+1}: Rate limited! [OK]")
            else:
                print(f"  Request {i+1}: Status {response.status_code}")

        print(f"Successful requests: {success_count}/12")


async def main():
    """Run all demo flows."""
    print("=" * 60)
    print("EngineerOS Authentication Demo")
    print("=" * 60)

    # Demo 1: Login
    print("\n[1] Login Flow")
    print("-" * 60)
    token = await demo_login()

    if not token:
        print("Skipping remaining demos (login required)")
        return

    # Demo 2: Authenticated request
    print("\n[2] Authenticated Request")
    print("-" * 60)
    await demo_authenticated_request(token)

    # Demo 3: Unauthenticated request (fails)
    print("\n[3] Unauthenticated Request")
    print("-" * 60)
    await demo_unauthenticated_request()

    # Demo 4: Rate limiting
    print("\n[4] Rate Limiting")
    print("-" * 60)
    await demo_rate_limiting()

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
