from pydantic import PrivateAttr, Field

from biochatter.api_agent.base.agent_abc import BaseAPI
from .base import ScanpyAPI

# Jiahang: how to help developers identify which arguments are useful?
# Jiahang: unfinished arguments. which should be used?
class ScTlUmap(ScanpyAPI):
    """Embed the neighborhood graph using UMAP."""

    _api_name: str = PrivateAttr(default="sc.tl.umap")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    min_dist: float = Field(
        0.5,
        description="The effective minimum distance between embedded points.",
    )
    spread: float = Field(
        1.0,
        description="The effective scale of embedded points.",
    )
    n_components: int = Field(
        2,
        description="The number of dimensions of the embedding.",
    )

class ScTlTsne(ScanpyAPI):
    """Embed the neighborhood graph using t-SNE."""

    _api_name: str = PrivateAttr(default="sc.tl.tsne")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    n_pcs: int | None = Field(
        None,
        description="The number of principal components to use for t-SNE.",
    )

class ScTlDiffMap(ScanpyAPI):
    """Compute a diffmap from a neighborhood graph."""

    _api_name: str = PrivateAttr(default="sc.tl.diffmap")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    ),
    # Jiahang: predict to be 2...
    n_comps: int = Field(
        15,
        description="The number of dimensions of the representation.",
    )
    
class ScTlEmbeddingDensity(ScanpyAPI):
    """Calculate the density of cells in an embedding (per condition).."""

    _api_name: str = PrivateAttr(default="sc.tl.embedding_density")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    basis: str = Field(
        "umap",
        description="The embedding over which the density will be calculated",
    )
    groupby: str | None = Field(
        None,
        description="Key for categorical observation/cell annotation for which densities are calculated per category.",
    )
    components: str | list[str] | None = Field(
        None,
        description="The embedding dimensions over which the density should be calculated. This is limited to two components.",
    )


class ScTlLeiden(ScanpyAPI):
    """Cluster the neighborhood graph using the Leiden algorithm."""

    _api_name: str = PrivateAttr(default="sc.tl.leiden")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    resolution: float = Field(
        1.0,
        description=(
            "A parameter value controlling the coarseness of the clustering. "
            "Higher values lead to more clusters."
        ),
    )
    random_state: int = Field(
        0,
        description="Random seed for reproducibility.",
    )
    use_weights: bool = Field(
        True,
        description="Whether to use edge weights in the clustering.",
    )

class ScTlLouvain(ScanpyAPI):
    """Cluster the neighborhood graph using the Louvain algorithm."""

    _api_name: str = PrivateAttr(default="sc.tl.louvain")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    resolution: float | None = Field(
        None,
        description="Resolution of the clustering.",
    )
    random_state: int = Field(
        0,
        description="Random seed for reproducibility.",
    )

class ScTlDendrogram(ScanpyAPI):
    """Compute a dendrogram of the neighborhood graph."""

    _api_name: str = PrivateAttr(default="sc.tl.dendrogram")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    n_pcs: int | None = Field(
        None,
        description="The number of principal components to use for the dendrogram.",
    )
    var_names: str | list[str] | None = Field(
        None,
        description="List of var_names to use for computing the hierarchical clustering.",
    )
    cor_method: str = Field(
        "pearson",
        description="The correlation method to use for computing the hierarchical clustering.",
    )

class ScTlRankGenesGroups(ScanpyAPI):
    """Rank genes for characterizing groups."""

    _api_name: str = PrivateAttr(default="sc.tl.rank_genes_groups")
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    groupby: str = Field(
        ...,
        description="The key of the observations grouping to consider.",
    )

TOOLS = [
    ScTlUmap,
    ScTlTsne,
    ScTlDiffMap,
    ScTlEmbeddingDensity,
    ScTlLeiden,
    ScTlLouvain,
    ScTlDendrogram,
    ScTlRankGenesGroups,
]

TOOLS_DICT = {tool._api_name.default: tool for tool in TOOLS}
