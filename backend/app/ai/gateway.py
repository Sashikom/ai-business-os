import os
import logging
from app.main import get_groq_client  # Импортируем функцию получения глобального клиента

logger = logging.getLogger(__name__)

class AIGateway:
    def __init__(self):
        # Берем уже правильно настроенный клиент из main.py
        self._client = get_groq_client()

    @property
    def client(self):
        if not self._client:
            logger.warning("Groq client is not initialized globally!")
        return self._client

    async def _generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            return "AI unavailable: Client not initialized"
        try:
            # Берем модель из .env
            model_name = os.getenv("GROQ_MODEL", "qwen-2.5-32b")
            
            response = self.client.chat.completions.create(
                model=model_name,  # Используем переменную, а не хардкод
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI error: {e}")
            return f"AI error: {str(e)}"

    # ... остальные методы (chat, market_research и т.д.) оставляем как были ...

    async def chat(self, message: str) -> str:
        return await self._generate("You are a business assistant. Answer in Russian, be detailed and professional.", message)

    async def market_research(self, query: str) -> str:
        return await self._generate("You are a market research expert. Analyze the market based on the query. Include: overview, trends, competitors, opportunities, risks. Answer in Russian.", query)

    async def content_generate(self, prompt: str) -> str:
        return await self._generate("You are a professional copywriter. Create quality content based on the request. Answer in Russian.", prompt)

    async def funnel_build(self, description: str) -> str:
        return await self._generate("You are a marketing funnel expert. Build a detailed sales funnel based on the business description. Include all stages, conversions, recommendations. Answer in Russian.", description)
