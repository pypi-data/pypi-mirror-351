import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize model once at module level
embedding_model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=512)

def _embed_pairs_and_calculate(pair1, pair2):
    """Calculate the embedding distance between two text pairs."""
    # Batch encode both pairs of text
    texts = [pair1, pair2]
    embeddings = embedding_model.encode(texts, prompt_name='query', batch_size=2)
    
    # Return cosine distance (1 - similarity)
    return 1 - embedding_model.similarity(embeddings[0:1], embeddings[1:2])[0][0].item()

def _calculate_lyapunov(ending_dist, starting_dist, timesteps):
    """Calculate Lyapunov exponent between two distances over time."""
    # Check for invalid inputs
    if starting_dist <= 0 or ending_dist <= 0 or timesteps <= 0:
        return None
    
    # Calculate ratio and ensure it's positive
    ratio = ending_dist / starting_dist
    if ratio <= 0:
        return None
        
    try:
        return np.log(ratio) / timesteps
    except (ZeroDivisionError, RuntimeWarning):
        return None

def process_paths(path1, path2):
    """Process two paths to calculate distances and Lyapunov exponents at each step."""
    # Batch encode all texts at once
    all_texts = path1 + path2
    all_embeddings = embedding_model.encode(all_texts, prompt_name='query', batch_size=32)
    
    # Split embeddings back into paths
    path1_embeddings = all_embeddings[:len(path1)]
    path2_embeddings = all_embeddings[len(path1):]
    
    distances = []
    exponents = [None]  # First exponent is always None since we need 2 points
    
    # Calculate distances and exponents at each step
    for i in range(len(path1)):
        # Calculate distance between current steps using pre-computed embeddings
        current_distance = 1 - embedding_model.similarity(
            path1_embeddings[i:i+1], 
            path2_embeddings[i:i+1]
        )[0][0].item()
        distances.append(current_distance)
        
        # Calculate Lyapunov exponent if we have more than one distance
        if i > 0:
            exponent = _calculate_lyapunov(
                ending_dist=current_distance,
                starting_dist=distances[0],  # Use the first distance as starting distance
                timesteps=i
            )
            exponents.append(exponent)
        else:
            exponents.append(None)  # Add None for the first step
    
    return distances, exponents 