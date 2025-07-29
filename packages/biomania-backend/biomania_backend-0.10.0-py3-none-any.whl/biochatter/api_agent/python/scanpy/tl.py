from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict, Field, PrivateAttr

from biochatter.api_agent.base.agent_abc import BaseAPI


class ScanpyToolsPaga(BaseAPI):
    """
    Map out the coarse-grained connectivity structures of complex manifolds by quantifying the connectivity of partitions in single-cell graphs using PAGA. PAGA generates a simpler abstracted graph representing confidence in connections, which can be used to obtain a simplified representation of manifold data while maintaining fidelity to the topology.
    """

    adata: Any = Field(
        ...,
        description="An annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    groups: Any = Field(
        None,
        description="Key for categorical in `adata.obs`. You can pass your predefined groups by choosing any categorical annotation of observations. Default: The first present key of `'leiden'` or `'louvain'`. Original type annotation: str | None",
        title="Groups",
    )
    use_rna_velocity: Optional[Any] = Field(
        False,
        description="Use RNA velocity to orient edges in the abstracted graph and estimate transitions. Requires that `adata.uns` contains a directed single-cell graph with key `['velocity_graph']`. This feature might be subject to change in the future. Original type annotation: bool",
        title="Use Rna Velocity",
    )
    model: Optional[Any] = Field(
        "v1.2",
        description="The PAGA connectivity model. Original type annotation: Literal['v1.2', 'v1.0']",
        title="Model",
    )
    neighbors_key: Any = Field(
        None,
        description="If not specified, paga looks `.uns['neighbors']` for neighbors settings and `.obsp['connectivities']`, `.obsp['distances']` for connectivities and distances respectively (default storage places for `pp.neighbors`). If specified, paga looks `.uns[neighbors_key]` for neighbors settings and `.obsp[.uns[neighbors_key]['connectivities_key']]`, `.obsp[.uns[neighbors_key]['distances_key']]` for connectivities and distances respectively. Original type annotation: str | None",
        title="Neighbors Key",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Copy `adata` before computation and return a copy. Otherwise, perform computation inplace and return `None`. Original type annotation: bool",
        title="Copy",
    )

    _api_name = PrivateAttr(default="scanpy.tools.paga")
    _products_original = PrivateAttr(
        default=[
            'data.uns["paga"]["connectivities"]',
            'data.uns["paga"]["connectivities_tree"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsLeiden(BaseAPI):
    """
    Cluster cells into subgroups using the Leiden algorithm, an improved version of the Louvain algorithm. It was proposed for single-cell analysis. This requires having run scanpy.pp.neighbors or scanpy.external.pp.bbknn first.
    """

    adata: Any = Field(..., description="The annotated data matrix.", title="Adata")
    resolution: Optional[Any] = Field(
        1,
        description="A parameter value controlling the coarseness of the clustering. Higher values lead to more clusters. Set to `None` if overriding `partition_type` to one that doesn’t accept a `resolution_parameter`.",
        title="Resolution",
    )
    restrict_to: Any = Field(
        None,
        description="Restrict the clustering to the categories within the key for sample annotation, tuple needs to contain `(obs_key, list_of_categories)`.",
        title="Restrict To",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Change the initialization of the optimization.",
        title="Random State",
    )
    key_added: Optional[Any] = Field(
        "leiden",
        description="`adata.obs` key under which to add the cluster labels.",
        title="Key Added",
    )
    adjacency: Any = Field(
        None,
        description="Sparse adjacency matrix of the graph, defaults to neighbors connectivities.",
        title="Adjacency",
    )
    directed: Any = Field(
        None,
        description="Whether to treat the graph as directed or undirected.",
        title="Directed",
    )
    use_weights: Optional[Any] = Field(
        True,
        description="If `True`, edge weights from the graph are used in the computation (placing more emphasis on stronger edges).",
        title="Use Weights",
    )
    n_iterations: Optional[Any] = Field(
        -1,
        description="How many iterations of the Leiden clustering algorithm to perform. Positive values above 2 define the total number of iterations to perform, -1 has the algorithm run until it reaches its optimal clustering.",
        title="N Iterations",
    )
    partition_type: Any = Field(
        None,
        description="Type of partition to use. Defaults to :class:`~leidenalg.RBConfigurationVertexPartition`.",
        title="Partition Type",
    )
    neighbors_key: Any = Field(
        None,
        description="Use neighbors connectivities as adjacency. If not specified, leiden looks at .obsp['connectivities'] for connectivities (default storage place for pp.neighbors).",
        title="Neighbors Key",
    )
    obsp: Any = Field(
        None,
        description="Use .obsp[obsp] as adjacency. You can't specify both `obsp` and `neighbors_key` at the same time.",
        title="Obsp",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Whether to copy `adata` or modify it inplace.",
        title="Copy",
    )
    flavor: Optional[Any] = Field(
        "leidenalg",
        description="Which package's implementation to use.",
        title="Flavor",
    )
    clustering_args: Any = Field(
        ..., description="No description available.", title="Clustering Args"
    )

    _api_name = PrivateAttr(default="scanpy.tools.leiden")
    _products_original = PrivateAttr(
        default=['data.obs["leiden"]', 'data.uns["leiden"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsLouvain(BaseAPI):
    """
    Cluster cells into subgroups using the Louvain algorithm, which was proposed for single-cell analysis. Prior to clustering, it is necessary to run scanpy's neighbors function or bbknn function, or provide an adjacency matrix explicitly.
    """

    adata: Any = Field(..., description="The annotated data matrix.", title="Adata")
    resolution: Any = Field(
        None,
        description="Parameter to control resolution for clustering.",
        title="Resolution",
    )
    random_state: Optional[Any] = Field(
        0, description="Seed for random state initialization.", title="Random State"
    )
    restrict_to: Any = Field(
        None,
        description="Restrict clustering to specific categories.",
        title="Restrict To",
    )
    key_added: Optional[Any] = Field(
        "louvain", description="Key to add the cluster labels under.", title="Key Added"
    )
    adjacency: Any = Field(
        None, description="Sparse adjacency matrix of the graph.", title="Adjacency"
    )
    flavor: Optional[Any] = Field(
        "vtraag",
        description="Choose between different clustering packages.",
        title="Flavor",
    )
    directed: Optional[Any] = Field(
        True, description="Specify if the graph is directed or not.", title="Directed"
    )
    use_weights: Optional[Any] = Field(
        False, description="Option to use weights from knn graph.", title="Use Weights"
    )
    partition_type: Any = Field(
        None,
        description="Type of partition to use in clustering.",
        title="Partition Type",
    )
    partition_kwargs: Optional[Any] = Field(
        {}, description="Keyword arguments for partitioning.", title="Partition Kwargs"
    )
    neighbors_key: Any = Field(
        None,
        description="Key to access neighbors connectivities.",
        title="Neighbors Key",
    )
    obsp: Any = Field(
        None, description="Use specified adjacency matrix for clustering.", title="Obsp"
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Option to copy data or modify it in place.",
        title="Copy",
    )

    _api_name = PrivateAttr(default="scanpy.tools.louvain")
    _products_original = PrivateAttr(
        default=['data.obs["louvain"]', 'data.uns["louvain"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsUmap(BaseAPI):
    """
    Embed the neighborhood graph using UMAP. UMAP is a manifold learning technique for visualizing high-dimensional data, optimizing the embedding to best reflect the data topology. It is faster than tSNE, which optimizes nearest-neighbor distances in the embedding to match high-dimensional space distances. The implementation used is umap-learn by McInnes (2018).
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    min_dist: Optional[Any] = Field(
        0.5,
        description="The effective minimum distance between embedded points. Smaller values result in a more clustered/clumped embedding, while larger values result in a more even dispersal of points. Default value in `umap-learn` is 0.1. Original type annotation: float",
        title="Min Dist",
    )
    spread: Optional[Any] = Field(
        1.0,
        description="The scale of embedded points, combined with `min_dist` to determine clustering. Original type annotation: float",
        title="Spread",
    )
    n_components: Optional[Any] = Field(
        2,
        description="Number of dimensions in the embedding. Original type annotation: int",
        title="N Components",
    )
    maxiter: Any = Field(
        None,
        description="Number of optimization iterations. Also called `n_epochs` in original UMAP. Original type annotation: int | None",
        title="Maxiter",
    )
    alpha: Optional[Any] = Field(
        1.0,
        description="Initial learning rate for the embedding optimization. Original type annotation: float",
        title="Alpha",
    )
    gamma: Optional[Any] = Field(
        1.0,
        description="Weighting for negative samples in low-dimensional embedding optimization. Higher values give more weight to negative samples. Original type annotation: float",
        title="Gamma",
    )
    negative_sample_rate: Optional[Any] = Field(
        5,
        description="Number of negative edge samples per positive edge sample in embedding optimization. Original type annotation: int",
        title="Negative Sample Rate",
    )
    init_pos: Optional[Any] = Field(
        "spectral",
        description="Initialization method for the low-dimensional embedding. Various options available. Original type annotation: _InitPos | np.ndarray | None",
        title="Init Pos",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Seed for random number generator or generator itself. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    a: Any = Field(
        None,
        description="Specific parameters for embedding control. Auto-set if None based on `min_dist` and `spread`. Original type annotation: float | None",
        title="A",
    )
    b: Any = Field(
        None,
        description="Specific parameters for embedding control. Auto-set if None based on `min_dist` and `spread`. Original type annotation: float | None",
        title="B",
    )
    method: Optional[Any] = Field(
        "umap",
        description="Chosen implementation between 'umap' and 'rapids'. Original type annotation: Literal['umap', 'rapids']",
        title="Method",
    )
    key_added: Any = Field(
        None,
        description="Specifies where the embedding is stored. Original type annotation: str | None",
        title="Key Added",
    )
    neighbors_key: Optional[Any] = Field(
        "neighbors",
        description="Key where UMAP looks for neighbors settings and connectivities. Original type annotation: str",
        title="Neighbors Key",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Option to return a copy instead of writing to adata. Original type annotation: bool",
        title="Copy",
    )

    _api_name = PrivateAttr(default="scanpy.tools.umap")
    _products_original = PrivateAttr(
        default=['data.obsm["X_umap"]', 'data.uns["umap"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsTsne(BaseAPI):
    """
    t-SNE is a dimensionality reduction technique used for visualizing single-cell data. The default implementation used here is from scikit-learn, but a faster alternative called Multicore-tSNE by Ulyanov (2016) can be installed for better performance.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    n_pcs: Any = Field(
        None,
        description="Use this many PCs. If `n_pcs==0` use `.X` if `use_rep is None`. Original type annotation: int | None",
        title="N Pcs",
    )
    use_rep: Any = Field(
        None,
        description="Use the indicated representation. If `None`, the representation is chosen automatically. Original type annotation: str | None",
        title="Use Rep",
    )
    perplexity: Optional[Any] = Field(
        30,
        description="Related to the number of nearest neighbors used in manifold learning algorithms. Choose a value between 5 and 50. Original type annotation: float",
        title="Perplexity",
    )
    metric: Optional[Any] = Field(
        "euclidean",
        description="Distance metric used to calculate neighbors. Original type annotation: str",
        title="Metric",
    )
    early_exaggeration: Optional[Any] = Field(
        12,
        description="Controls the spacing between natural clusters in the embedded space. Original type annotation: float",
        title="Early Exaggeration",
    )
    learning_rate: Optional[Any] = Field(
        1000,
        description="A critical parameter between 100 and 1000. Adjust if cost function increases during optimization. Original type annotation: float",
        title="Learning Rate",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Change to use different initial states for optimization. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    use_fast_tsne: Optional[Any] = Field(
        False,
        description="No description available. Original type annotation: bool",
        title="Use Fast Tsne",
    )
    n_jobs: Any = Field(
        None,
        description="Number of jobs for parallel computation. Original type annotation: int | None",
        title="N Jobs",
    )
    key_added: Any = Field(
        None,
        description="Specifies where the embedding is stored. Original type annotation: str | None",
        title="Key Added",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Return a copy instead of writing to `adata`. Original type annotation: bool",
        title="Copy",
    )

    _api_name = PrivateAttr(default="scanpy.tools.tsne")
    _products_original = PrivateAttr(
        default=['data.obsm["X_tsne"]', 'data.uns["tsne"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsDiffmap(BaseAPI):
    """
    Diffusion Maps: a tool for visualizing single-cell data using adapted Gaussian kernel, with the width of the connectivity kernel implicitly determined by the number of neighbors. Options include using a Gaussian kernel with 'method==\'gauss\'' or an exponential kernel with 'method==\'umap\'.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    n_comps: Optional[Any] = Field(
        15,
        description="The number of dimensions of the representation. Original type annotation: int",
        title="N Comps",
    )
    neighbors_key: Any = Field(
        None,
        description="If not specified, diffmap looks in .uns['neighbors'] for neighbors settings and .obsp['connectivities'] and .obsp['distances'] for connectivities and distances, respectively (default storage places for pp.neighbors). If specified, diffmap looks in .uns[neighbors_key] for neighbors settings and .obsp[.uns[neighbors_key]['connectivities_key']] and .obsp[.uns[neighbors_key]['distances_key']] for connectivities and distances, respectively. Original type annotation: str | None",
        title="Neighbors Key",
    )
    random_state: Optional[Any] = Field(
        0,
        description="A numpy random seed. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Return a copy instead of writing to adata. Original type annotation: bool",
        title="Copy",
    )

    _api_name = PrivateAttr(default="scanpy.tools.diffmap")
    _products_original = PrivateAttr(
        default=['data.obsm["X_diffmap"]', 'data.uns["diffmap_evals"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsEmbeddingDensity(BaseAPI):
    """
    Calculate the density of cells in an embedding (per condition). Gaussian kernel density estimation is used to calculate the density of cells in an embedded space. The cell density can be plotted using the `pl.embedding_density` function. Density values are scaled to be between 0 and 1 and are only comparable within the same category. The reliability of the KDE estimate depends on having enough cells in a category. This function was written by Sophie Tritschler and implemented into Scanpy by Malte Luecken.
    """

    adata: Any = Field(..., description="The annotated data matrix.", title="Adata")
    basis: Optional[Any] = Field(
        "umap",
        description="The embedding over which the density will be calculated. This embedded representation is found in `adata.obsm['X_[basis]']`.",
        title="Basis",
    )
    groupby: Any = Field(
        None,
        description="Key for categorical observation/cell annotation for which densities are calculated per category.",
        title="Groupby",
    )
    key_added: Any = Field(
        None,
        description="Name of the `.obs` covariate that will be added with the density estimates.",
        title="Key Added",
    )
    components: Any = Field(
        None,
        description="The embedding dimensions over which the density should be calculated. This is limited to two components.",
        title="Components",
    )

    _api_name = PrivateAttr(default="scanpy.tools.embedding_density")
    _products_original = PrivateAttr(
        default=['data.obs["umap_density"]', 'data.uns["umap_density_params"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsRankGenesGroups(BaseAPI):
    """
    Rank genes for characterizing groups. Expects logarithmized data.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    groupby: Any = Field(
        ...,
        description="The key of the observations grouping to consider. Original type annotation: str",
        title="Groupby",
    )
    mask_var: Any = Field(
        None,
        description="Select subset of genes to use in statistical tests. Original type annotation: NDArray[np.bool_] | str | None",
        title="Mask Var",
    )
    use_raw: Any = Field(
        None,
        description="Use `raw` attribute of `adata` if present. The default behavior is to use `raw` if present. Original type annotation: bool | None",
        title="Use Raw",
    )
    groups: Optional[Any] = Field(
        "all",
        description="Subset of groups for comparison, with options like ['g1', 'g2', 'g3'] or 'all'. Original type annotation: Literal['all'] | Iterable[str]",
        title="Groups",
    )
    reference: Optional[Any] = Field(
        "rest",
        description="Specifies which group to compare against. Original type annotation: str",
        title="Reference",
    )
    n_genes: Any = Field(
        None,
        description="Number of genes to include in results. Defaults to all genes. Original type annotation: int | None",
        title="N Genes",
    )
    rankby_abs: Optional[Any] = Field(
        False,
        description="Rank genes by absolute value of score. Original type annotation: bool",
        title="Rankby Abs",
    )
    pts: Optional[Any] = Field(
        False,
        description="Compute fraction of cells expressing genes. Original type annotation: bool",
        title="Pts",
    )
    key_added: Any = Field(
        None,
        description="Key in `adata.uns` where information is saved. Original type annotation: str | None",
        title="Key Added",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether to copy `adata` or modify it inplace. Original type annotation: bool",
        title="Copy",
    )
    method: Any = Field(
        None,
        description="Specifies the statistical testing method. Original type annotation: _Method | None",
        title="Method",
    )
    corr_method: Optional[Any] = Field(
        "benjamini-hochberg",
        description="Method for p-value correction. Original type annotation: _CorrMethod",
        title="Corr Method",
    )
    tie_correct: Optional[Any] = Field(
        False,
        description="Use tie correction for 'wilcoxon' scores. Original type annotation: bool",
        title="Tie Correct",
    )
    layer: Any = Field(
        None,
        description="Key from `adata.layers` to use for tests. Original type annotation: str | None",
        title="Layer",
    )
    kwds: Any = Field(
        ...,
        description="Parameters passed to test methods, affecting logistic regression parameters. For example, penalty='l1' for sparse solutions.",
        title="Kwds",
    )

    _api_name = PrivateAttr(default="scanpy.tools.rank_genes_groups")
    _products_original = PrivateAttr(default=['data.uns["rank_genes_groups"]'])
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsFilterRankGenesGroups(BaseAPI):
    """
    Filter out genes based on two criteria: log fold change and fraction of genes expressing the gene within and outside the groupby categories. Results are stored in adata.uns[key_added] (default: 'rank_genes_groups_filtered'). Filtered genes are set to NaN to preserve the original structure of adata.uns['rank_genes_groups'].
    """

    adata: Any = Field(
        ...,
        description="AnnData is the main data structure for storing annotated data.",
        title="Adata",
    )
    key: Any = Field(
        None, description="A string representing a key used for grouping.", title="Key"
    )
    groupby: Any = Field(
        None,
        description="A string representing the variable used for grouping.",
        title="Groupby",
    )
    use_raw: Any = Field(
        None,
        description="A boolean indicating whether to use raw data for calculations.",
        title="Use Raw",
    )
    key_added: Optional[Any] = Field(
        "rank_genes_groups_filtered",
        description="A string representing the key added to the data.",
        title="Key Added",
    )
    min_in_group_fraction: Optional[Any] = Field(
        0.25,
        description="A float specifying the minimum fraction of cells in a group.",
        title="Min In Group Fraction",
    )
    min_fold_change: Optional[Any] = Field(
        1,
        description="A float specifying the minimum fold change threshold.",
        title="Min Fold Change",
    )
    max_out_group_fraction: Optional[Any] = Field(
        0.5,
        description="A float specifying the maximum fraction of cells out of the group.",
        title="Max Out Group Fraction",
    )
    compare_abs: Optional[Any] = Field(
        False,
        description="A boolean indicating whether to compare absolute values of log fold change.",
        title="Compare Abs",
    )
    _api_name = PrivateAttr(default="scanpy.tools.filter_rank_genes_groups")
    _products_original = PrivateAttr(default=['data.uns["rank_genes_groups"]'])
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsMarkerGeneOverlap(BaseAPI):
    """
    Calculate an overlap score between data-derived marker genes and provided markers. Marker gene overlap scores can be quoted as overlap counts, overlap coefficients, or jaccard indices. The method returns a pandas dataframe which can be used to annotate clusters based on marker gene overlaps. This function was written by Malte Luecken.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    reference_markers: Any = Field(
        ...,
        description="A marker gene dictionary object where keys are cell identity names and values are sets or lists of strings matching the format of `adata.var_name`. Original type annotation: dict[str, set] | dict[str, list]",
        title="Reference Markers",
    )
    key: Optional[Any] = Field(
        "rank_genes_groups",
        description="The key in `adata.uns` where the rank_genes_groups output is stored. By default, this is 'rank_genes_groups'. Original type annotation: str",
        title="Key",
    )
    method: Optional[Any] = Field(
        "overlap_count",
        description="Method to calculate marker gene overlap, with options like 'overlap_count', 'overlap_coef', and 'jaccard'. Default is 'overlap_count'. Original type annotation: _Method",
        title="Method",
    )
    normalize: Any = Field(
        None,
        description="Normalization option for marker gene overlap output, applicable only when method is 'overlap_count'. Options are 'reference' and 'data'. Original type annotation: Literal['reference', 'data'] | None",
        title="Normalize",
    )
    top_n_markers: Any = Field(
        None,
        description="Number of top data-derived marker genes to use, default is 100. If adj_pval_threshold is set with top_n_markers, the threshold is ignored. Original type annotation: int | None",
        title="Top N Markers",
    )
    adj_pval_threshold: Any = Field(
        None,
        description="Significance threshold on adjusted p-values to select marker genes, applicable when adjusted p-values are calculated by sc.tl.rank_genes_groups(). If set alongside top_n_markers, the threshold is ignored. Original type annotation: float | None",
        title="Adj Pval Threshold",
    )
    key_added: Optional[Any] = Field(
        "marker_gene_overlap",
        description="Name of the field in `.uns` that will contain the marker overlap scores. Original type annotation: str",
        title="Key Added",
    )
    inplace: Optional[Any] = Field(
        False,
        description="Choose to return a marker gene dataframe or store it in `adata.uns`. Original type annotation: bool",
        title="Inplace",
    )
    _api_name = PrivateAttr(default="scanpy.tools.marker_gene_overlap")
    _products_original = PrivateAttr(default=['data.uns["marker_gene_overlap"]'])
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsScoreGenes(BaseAPI):
    """
    Score a set of genes by calculating the average expression of the genes after subtracting the average expression of a reference set of genes, randomly sampled from a gene pool for each binned expression value. This method replicates the approach in Seurat by Satija (2015) and has been implemented for Scanpy by Davide Cittaro.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix with original type annotation AnnData.",
        title="Adata",
    )
    gene_list: Any = Field(
        ...,
        description="The list of gene names used for score calculation with original type annotation Sequence[str] or pd.Index[str].",
        title="Gene List",
    )
    ctrl_as_ref: Optional[Any] = Field(
        True,
        description="Allows the algorithm to use the control genes as reference. Will be changed to `False` in scanpy 2.0 with original type annotation bool.",
        title="Ctrl As Ref",
    )
    ctrl_size: Optional[Any] = Field(
        50,
        description="Number of reference genes to be sampled from each bin. Can be set to `ctrl_size=len(gene_list)` if `len(gene_list)` is not too low with original type annotation int.",
        title="Ctrl Size",
    )
    gene_pool: Any = Field(
        None,
        description="Genes for sampling the reference set, default is all genes with original type annotation Sequence[str], pd.Index[str], or None.",
        title="Gene Pool",
    )
    n_bins: Optional[Any] = Field(
        25,
        description="Number of expression level bins for sampling with original type annotation int.",
        title="N Bins",
    )
    score_name: Optional[Any] = Field(
        "score",
        description="Name of the field to be added in `.obs` with original type annotation str.",
        title="Score Name",
    )
    random_state: Optional[Any] = Field(
        0,
        description="The random seed for sampling with original type annotation _LegacyRandom.",
        title="Random State",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Option to copy `adata` or modify it inplace with original type annotation bool.",
        title="Copy",
    )
    use_raw: Any = Field(
        None,
        description="Option to use the `raw` attribute of `adata`, defaults to `True` if `.raw` is present. Default value changed from `False` to `None` in version 1.4.5 with original type annotation bool or None.",
        title="Use Raw",
    )
    layer: Any = Field(
        None,
        description="Key from `adata.layers` that will be used to perform tests with original type annotation str or None.",
        title="Layer",
    )
    _api_name = PrivateAttr(default="scanpy.tools.score_genes")
    _products_original = PrivateAttr(default=['data.obs["score"]'])
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsScoreGenesCellCycle(BaseAPI):
    """
    Score cell cycle genes: Citation to Satija et al., 2015. Given lists of genes related to S phase and G2M phase, this function calculates scores and assigns a cell cycle phase (G1, S, or G2M). Refer to scanpy.tl.score_genes function for further details.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    s_genes: Any = Field(
        ...,
        description="List of genes associated with S phase. Original type annotation: Sequence[str]",
        title="S Genes",
    )
    g2m_genes: Any = Field(
        ...,
        description="List of genes associated with G2M phase. Original type annotation: Sequence[str]",
        title="G2M Genes",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Copy `adata` or modify it inplace. Original type annotation: bool",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.tools.score_genes_cell_cycle")
    _products_original = PrivateAttr(
        default=['data.obs["S_score"]', 'data.obs["G2M_score"]', 'data.obs["phase"]']
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyToolsDrawGraph(BaseAPI):
    """
    Force-directed graph drawing: An alternative to tSNE that often preserves the topology of the data better. It requires running scanpy.pp.neighbors first. The default layout ('fa', ForceAtlas2) uses the package fa2-modified, which can be installed via pip install fa2-modified. Force-directed graph drawing describes a class of long-established algorithms for visualizing graphs. It was suggested for visualizing single-cell data by Islam et al. Many other layouts as implemented in igraph are available. Similar approaches have been used by Zunder et al. or Weinreb et al.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    layout: Optional[Any] = Field(
        "fa",
        description="'fa' (`ForceAtlas2`) or any valid `igraph layout`. Choose from various layout options like 'fr', 'kk', 'lgl', 'drl', and 'rt'. Original type annotation: _Layout",
        title="Layout",
    )
    init_pos: Any = Field(
        None,
        description="`'paga'`/`True`, `None`/`False`, or any valid 2d-`.obsm` key. Use precomputed coordinates for initialization or initialize randomly. Original type annotation: str | bool | None",
        title="Init Pos",
    )
    root: Any = Field(
        None,
        description="Root for tree layouts. Original type annotation: int | None",
        title="Root",
    )
    random_state: Optional[Any] = Field(
        0,
        description="For layouts with random initialization like 'fr', change this to use different initial states for optimization. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    n_jobs: Any = Field(
        None,
        description="No description available. Original type annotation: int | None",
        title="N Jobs",
    )
    adjacency: Any = Field(
        None,
        description="Sparse adjacency matrix of the graph, defaults to neighbors connectivities. Original type annotation: spmatrix | None",
        title="Adjacency",
    )
    key_added_ext: Any = Field(
        None,
        description="By default, append `layout`. Original type annotation: str | None",
        title="Key Added Ext",
    )
    neighbors_key: Any = Field(
        None,
        description="Specify where to find connectivities data. Original type annotation: str | None",
        title="Neighbors Key",
    )
    obsp: Any = Field(
        None,
        description="Use .obsp[obsp] as adjacency. Cannot specify both `obsp` and `neighbors_key` simultaneously. Original type annotation: str | None",
        title="Obsp",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Return a copy instead of writing to adata. Original type annotation: bool",
        title="Copy",
    )
    kwds: Any = Field(..., description="No description available.", title="Kwds")
    _api_name = PrivateAttr(default="scanpy.tools.draw_graph")
    _products_original = PrivateAttr(
        default=['data.uns["draw_graph"]', 'data.obsm["X_draw_graph_fa"]']
    )
    _data_name = PrivateAttr(default="adata")


TOOLS_DICT = {
    "scanpy.tools.paga": ScanpyToolsPaga,
    "scanpy.tools.leiden": ScanpyToolsLeiden,
    "scanpy.tools.louvain": ScanpyToolsLouvain,
    "scanpy.tools.umap": ScanpyToolsUmap,
    "scanpy.tools.tsne": ScanpyToolsTsne,
    "scanpy.tools.diffmap": ScanpyToolsDiffmap,
    "scanpy.tools.embedding_density": ScanpyToolsEmbeddingDensity,
    "scanpy.tools.rank_genes_groups": ScanpyToolsRankGenesGroups,
    "scanpy.tools.filter_rank_genes_groups": ScanpyToolsFilterRankGenesGroups,
    "scanpy.tools.marker_gene_overlap": ScanpyToolsMarkerGeneOverlap,
    "scanpy.tools.score_genes": ScanpyToolsScoreGenes,
    "scanpy.tools.score_genes_cell_cycle": ScanpyToolsScoreGenesCellCycle,
    "scanpy.tools.draw_graph": ScanpyToolsDrawGraph,
}
