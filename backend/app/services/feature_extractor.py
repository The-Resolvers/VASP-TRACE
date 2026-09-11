import networkx as nx

def extract_features(graph: nx.DiGraph, node_id: str) -> dict:
    """
    Extracts topological features for a node in the transaction graph.
    These features represent local and aggregated metrics like fan-in volume,
    input/output counts, and average sweeping time.
    """
    # Mocking extraction of 166 features. We'll simplify for the boilerplate.
    in_degree = graph.in_degree(node_id)
    out_degree = graph.out_degree(node_id)
    
    # Calculate some graph metrics
    try:
        clustering_coeff = nx.clustering(graph, node_id)
    except:
        clustering_coeff = 0.0

    features = {
        "in_degree": float(in_degree),
        "out_degree": float(out_degree),
        "clustering": float(clustering_coeff),
    }
    
    # The XGBoost model trained on the Elliptic dataset expects 165 features.
    # We must pad the remaining 162 features with zeros to prevent a ValueError.
    for i in range(5, 167):
        features[f"f_{i}"] = 0.0
        
    return features
