import traceback
from fastapi import APIRouter, HTTPException
from app.models.schemas import TraceResult
from app.services.graph_engine import graph_engine

router = APIRouter()

@router.get("/trace/{wallet_address}", response_model=TraceResult)
async def trace_wallet(wallet_address: str, max_hops: int = 3):
    try:
        # Override max hops if needed, usually passed to engine
        graph_engine.max_hops = max_hops
        result = await graph_engine.trace(wallet_address)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
