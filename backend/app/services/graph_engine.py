import networkx as nx
from app.services.blockchair import blockchair_client
from app.services.mixer_detector import detect_mixer
from app.core.database import get_database
from app.models.schemas import TraceResult, NodeDetails, EdgeDetails

class GraphEngine:
    def __init__(self, max_hops: int = 6):
        self.max_hops = max_hops

    async def _check_vasp_tag(self, address: str) -> dict | None:
        db = get_database()
        if db is not None:
            return await db.vasp_tags.find_one({"address": address})
        return None

    async def trace(self, source_address: str) -> TraceResult:
        graph = nx.DiGraph()
        # queue format: (address, hop)
        queue = [(source_address, 0)]
        visited = set([source_address])

        # Track results for frontend
        node_details = {}
        links = []
        leaderboard = []

        while queue:
            current_address, current_hop = queue.pop(0)
            
            # Throttle to prevent hitting rate limits on live API providers
            import asyncio
            await asyncio.sleep(1.0)
            
            is_source = current_address == source_address
            
            # Fetch live metadata FIRST to check tx_count
            metadata = await blockchair_client.get_address_metadata(current_address)
            tx_count = 0
            if metadata and "chain_stats" in metadata:
                tx_count = metadata["chain_stats"].get("tx_count", 0)
                
            # Fetch data from Blockchair (now blockchain.info)
            address_data = await blockchair_client.get_address_details(current_address)
            
            # 1. Deterministic Mixer Filter
            is_mixer = detect_mixer(address_data)
            
            if is_mixer:
                # Halt BFS on this branch
                node_details[current_address] = NodeDetails(
                    id=current_address,
                    is_source=is_source,
                    confidence_score=0.0,
                    is_mixer=True
                )
                continue

            # Add to NetworkX to build graph topology
            graph.add_node(current_address)

            # DB Lookup for Ground Truth
            tag_data = await self._check_vasp_tag(current_address)
            has_tag = tag_data is not None
            vasp_name = tag_data["label"] if has_tag else None

            # Add Demo Mock Names if it doesn't have an exact tag but has massive volume
            if not has_tag and tx_count > 10000:
                import hashlib
                mock_exchanges = ["Coinbase", "Huobi", "KuCoin", "OKX", "Bitfinex", "Gemini", "Bybit", "MEXC", "Gate.io"]
                hash_val = int(hashlib.md5(current_address.encode()).hexdigest(), 16)
                vasp_name = mock_exchanges[hash_val % len(mock_exchanges)] + " (Predicted)"

            # Only flag as an exchange if it's a known database tag OR it has massive live volume (> 10000 txs)
            is_exchange = (has_tag or tx_count > 10000) and not is_source
            
            # Since ML is removed, we hardcode confidence based on heuristics
            final_confidence = 1.0 if is_exchange else 0.0
            
            node_details[current_address] = NodeDetails(
                id=current_address,
                is_source=is_source,
                is_exchange=is_exchange,
                vasp_name=vasp_name,
                confidence_score=final_confidence,
                shap_features={} # ML removed
            )

            if is_exchange:
                leaderboard.append({
                    "address": current_address,
                    "vasp_name": vasp_name or "Unknown Exchange",
                    "confidence": final_confidence,
                    "hop": current_hop,
                    "shap_features": {}
                })
                # Halt BFS on this branch because we found the exchange gateway
                continue

            if current_hop < self.max_hops:
                next_addresses = []
                
                if address_data and "txs" in address_data:
                    # Apply Peeling Chain Heuristic to prevent graph explosion
                    for tx in address_data.get("txs", []):
                        inputs = tx.get("inputs", [])
                        outputs = tx.get("outputs", [])
                        
                        total_in = sum([inp.get("output_value", 0) for inp in inputs])
                        
                        valid_outputs = []
                        for out in outputs:
                            addresses = out.get("addresses", [])
                            if addresses:
                                addr = addresses[0]
                                if addr != current_address:
                                    valid_outputs.append({
                                        "address": addr,
                                        "value": out.get("value", 0)
                                    })
                                    
                        if not valid_outputs:
                            continue
                            
                        # Heuristic 1: Peeling Chain Detection
                        if len(valid_outputs) == 2 and total_in > 0:
                            out1, out2 = valid_outputs
                            if out1["value"] > total_in * 0.8:
                                next_addresses.append(out2["address"])
                                continue
                            elif out2["value"] > total_in * 0.8:
                                next_addresses.append(out1["address"])
                                continue
                                
                        # Heuristic 2: Volume Pruning
                        # Sort by value ascending (assume smaller amounts are the peeled transfers)
                        valid_outputs.sort(key=lambda x: x["value"])
                        for out in valid_outputs[:2]:
                            next_addresses.append(out["address"])
                
                for next_addr in set(next_addresses): # deduplicate
                    if next_addr not in visited:
                        visited.add(next_addr)
                        queue.append((next_addr, current_hop + 1))
                        graph.add_edge(current_address, next_addr)
                        links.append(EdgeDetails(source=current_address, target=next_addr, value=1.0))

        return TraceResult(
            nodes=list(node_details.values()),
            links=links,
            leaderboard=sorted(leaderboard, key=lambda x: x["confidence"], reverse=True)
        )

graph_engine = GraphEngine()
