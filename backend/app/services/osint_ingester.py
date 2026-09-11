import asyncio
import httpx
from app.core.database import get_database

class OSINTIngester:
    def __init__(self):
        self.running = False
        
    async def fetch_threat_intel(self):
        """
        Mock OSINT source. In a real system, this would poll OFAC, WalletExplorer, etc.
        For demonstration, we inject a live payload of tags.
        """
        return [
            {"address": "bc1q3zcdunpmqgn8enyxa3smu7fwrfvya35dz3uvjy", "label": "Binance Hot Wallet"},
            {"address": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s", "label": "Known Scammer (2019 Hack)"},
            {"address": "bc1qq3mjl2ex6tdvkvd4udffqpmf7d3n362wyr5frj", "label": "Kraken Cold Storage"},
            {"address": "1NchxF591wBDL2w5sjwAx9gXfg1X43pFot", "label": "Lazarus Group (Sanctioned)"},
        ]

    async def run(self):
        self.running = True
        print("Starting OSINT Threat Intel Ingester...")
        
        while self.running:
            try:
                db = get_database()
                if db is not None:
                    # Fetch live tags
                    tags = await self.fetch_threat_intel()
                    
                    # Upsert into database
                    for tag in tags:
                        await db.vasp_tags.update_one(
                            {"address": tag["address"]},
                            {"$set": tag},
                            upsert=True
                        )
                    print(f"OSINT Ingester: Successfully synced {len(tags)} tags to database.")
                else:
                    print("OSINT Ingester: Database not ready.")
            except Exception as e:
                print(f"OSINT Ingester Error: {e}")
                
            # Sleep for 1 hour (mocked to 60 seconds for demo observability)
            await asyncio.sleep(60)
            
    def stop(self):
        self.running = False

osint_ingester = OSINTIngester()
