import httpx
import hashlib

class BlockchainClient:
    def __init__(self):
        self.base_url = "https://blockstream.info/api/address"
        self.client = httpx.AsyncClient()
        self.cache = {}

    async def get_address_metadata(self, address: str) -> dict | None:
        url = f"{self.base_url}/{address}"
        try:
            response = await self.client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching live metadata for {address}: {e}")
            return None

    async def get_address_details(self, address: str) -> dict | None:
        if address in self.cache:
            return self.cache[address]

        url = f"{self.base_url}/{address}/txs"
        try:
            response = await self.client.get(url, timeout=10.0)
            response.raise_for_status()
            raw_txs = response.json()
            
            # Normalize Esplora format to standard format expected by GraphEngine
            normalized_data = self._normalize_data(address, raw_txs)
            
            self.cache[address] = normalized_data
            return normalized_data
        except Exception as e:
            print(f"Error fetching live data for {address}: {e}")
            # Strict rule: NO MOCK DATA. Fail cleanly on rate limits or errors.
            return None

    def _normalize_data(self, address: str, raw_txs: list) -> dict:
        normalized_txs = []
        # Limit to first 5 txs to simulate blockcypher's limit=5 and reduce trace fan-out
        for tx in raw_txs[:5]:
            norm_inputs = []
            for vin in tx.get("vin", []):
                prevout = vin.get("prevout", {})
                if prevout:
                    norm_inputs.append({
                        "output_value": prevout.get("value", 0),
                        "addresses": [prevout.get("scriptpubkey_address")] if prevout.get("scriptpubkey_address") else []
                    })
                
            norm_outputs = []
            for vout in tx.get("vout", []):
                norm_outputs.append({
                    "value": vout.get("value", 0),
                    "addresses": [vout.get("scriptpubkey_address")] if vout.get("scriptpubkey_address") else []
                })
                
            normalized_txs.append({
                "inputs": norm_inputs,
                "outputs": norm_outputs
            })
            
        return {
            "address": address,
            "txs": normalized_txs
        }

    async def close(self):
        await self.client.aclose()

# Keeping the variable name the same so we don't have to rewrite graph_engine.py everywhere
blockchair_client = BlockchainClient()
