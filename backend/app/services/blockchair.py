import httpx

class BlockchainClient:
    def __init__(self):
        self.base_url = "https://blockchain.info"
        self.client = httpx.AsyncClient()

    async def get_address_details(self, address: str) -> dict | None:
        url = f"{self.base_url}/rawaddr/{address}"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data for {address}: {e}")
            return None

    async def close(self):
        await self.client.aclose()

# Keeping the variable name the same so we don't have to rewrite graph_engine.py
blockchair_client = BlockchainClient()
