import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://ai-business-os-backend:8000/api/v1")


class APIClient:
    """Клиент для запросов к backend API."""

    def __init__(self):
        self.base_url = BACKEND_URL

    async def _request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{self.base_url}{path}"
            try:
                if method == "GET":
                    resp = await client.get(url, **kwargs)
                elif method == "POST":
                    resp = await client.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                print(f"API Error: {e.response.status_code} - {e.response.text}")
                return None
            except Exception as e:
                print(f"API Error: {e}")
                return None

    # --- Пользовательские методы ---

    async def register(self, telegram_id: int, username: str = None,
                       first_name: str = None, last_name: str = None):
        return await self._request("POST", "/telegram/register", json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        })

    async def get_me(self, telegram_id: int):
        return await self._request("GET", "/telegram/me", params={
            "telegram_id": telegram_id,
        })

    async def activate_token(self, telegram_id: int, token: str):
        return await self._request("POST", "/telegram/activate-token", json={
            "telegram_id": telegram_id,
            "token": token,
        })

    # --- AI методы ---

    async def ai_chat(self, telegram_id: int, message: str, module: str = "chat"):
        return await self._request("POST", "/ai/chat", json={
            "telegram_id": telegram_id,
            "message": message,
            "module": module,
        })

    # --- Админские методы ---

    async def generate_tokens(self, admin_telegram_id: int, count: int = 1,
                              duration_days: int = 30):
        return await self._request("POST", "/admin/generate-tokens", json={
            "count": count,
            "duration_days": duration_days,
        }, params={"telegram_id": admin_telegram_id})

    async def list_tokens(self, admin_telegram_id: int, used: int = None):
        params = {"telegram_id": admin_telegram_id}
        if used is not None:
            params["used"] = used
        return await self._request("GET", "/admin/tokens", params=params)

    async def list_users(self, admin_telegram_id: int):
        return await self._request("GET", "/admin/users", params={
            "telegram_id": admin_telegram_id,
        })

    async def block_user(self, admin_telegram_id: int, block_telegram_id: int):
        return await self._request("POST", "/admin/block-user", params={
            "telegram_id": admin_telegram_id,
        }, json={"block_telegram_id": block_telegram_id})


api_client = APIClient()
