def detect_mixer(address_data: dict) -> bool:
    """
    Scans the transaction for structural obfuscation patterns (Wasabi/CoinJoin or Peeling chain).
    Adapted for Blockcypher API format.
    """
    if not address_data or "txs" not in address_data:
        return False
        
    transactions = address_data.get("txs", [])
    
    for tx in transactions:
        inputs = len(tx.get("inputs", []))
        outputs = len(tx.get("outputs", []))
        
        # Heuristic for CoinJoin: Many inputs and outputs, usually identical values.
        # Simplified for demonstration.
        if inputs >= 10 and outputs >= 10:
            return True
            
    return False
