import logging
import os
from groq import Groq

logger = logging.getLogger(__name__)


class AIGateway:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY", "")
            if api_key:
                self._client = Groq(api_key=api_key)
        return self._client

    async def _generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            return "AI unavailable: GROQ_API_KEY not set"
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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

    async def chat(self, message: str) -> str:
        return await self._generate("You are a business assistant. Answer in Russian, be detailed and professional.", message)

    async def market_research(self, query: str) -> str:
        return await self._generate("You are a market research expert. Analyze the market based on the query. Include: overview, trends, competitors, opportunities, risks. Answer in Russian.", query)

    async def content_generate(self, prompt: str) -> str:
        return await self._generate("You are a professional copywriter. Create quality content based on the request. Answer in Russian.", prompt)

    async def funnel_build(self, description: str) -> str:
        return await self._generate("You are a marketing funnel expert. Build a detailed sales funnel based on the business description. Include all stages, conversions, recommendations. Answer in Russian.", description)
