from pydantic import BaseModel, Field

class VaspTag(BaseModel):
    label: str
    address: str
    actor: str

class NodeDetails(BaseModel):
    id: str
    is_source: bool = False
    is_exchange: bool = False
    vasp_name: str | None = None
    confidence_score: float = 0.0
    shap_features: dict[str, float] | None = None
    is_mixer: bool = False

class EdgeDetails(BaseModel):
    source: str
    target: str
    value: float

class TraceResult(BaseModel):
    nodes: list[NodeDetails]
    links: list[EdgeDetails]
    leaderboard: list[dict]
