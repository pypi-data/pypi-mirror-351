import pytest
from scdrakex.rembedding import Embeddingr_embed_data

def test_r_embed_data():
    count_matrix = [[1, 2, 3], [4, 5, 6]]
    genes = ["gene1", "gene2", "gene3"]
    model_dir = "path/to/model"
    
    # Call the embedding function
    embeddings = Embeddingr_embed_data(
        count_matrix=count_matrix,
        genes=genes,
        model_dir=model_dir,
        max_length=1200,
        batch_size=64,
        use_batch_labels=False,
        obs_to_save=None,
        device="cpu",
        use_fast_transformer=True,
        fast_transformer_backend="Linear"
    )
    
    # Check if embeddings are returned as expected
    assert isinstance(embeddings, list)
    assert len(embeddings) == len(count_matrix)
    assert all(isinstance(emb, list) for emb in embeddings)