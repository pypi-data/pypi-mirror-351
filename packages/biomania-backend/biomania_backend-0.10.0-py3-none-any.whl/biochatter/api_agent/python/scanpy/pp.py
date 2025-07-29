from __future__ import annotations

from typing import Any, Optional
from pydantic import ConfigDict, Field, PrivateAttr

from biochatter.api_agent.base.agent_abc import BaseAPI


class ScanpyPreprocessingNeighbors(BaseAPI):
    """
    Compute the nearest neighbors distance matrix and a neighborhood graph of observations. The method heavily relies on UMAP for neighbor search efficiency and provides a method for estimating connectivities of data points. Connectivities are computed according to different methods based on the chosen parameter.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    n_neighbors: Optional[Any] = Field(
        15,
        description="The size of local neighborhood used for manifold approximation, with values typically ranging from 2 to 100. Ignored if transformer is an instance. Original type annotation: int",
        title="N Neighbors",
    )
    n_pcs: Any = Field(
        None,
        description="Specifies the number of principal components to use, with the option for automatic selection based on data size. Original type annotation: int | None",
        title="N Pcs",
    )
    use_rep: Any = Field(
        None,
        description="Specifies the representation to use, with automatic selection based on data size if set to None. Original type annotation: str | None",
        title="Use Rep",
    )
    knn: Optional[Any] = Field(
        True,
        description="Determines the method for generating neighbors, either using a hard threshold or a Gaussian Kernel. Original type annotation: bool",
        title="Knn",
    )
    method: Optional[Any] = Field(
        "umap",
        description="Specifies the method for computing connectivities, such as 'umap' or 'gauss'. Original type annotation: _Method",
        title="Method",
    )
    transformer: Any = Field(
        None,
        description="Specifies the approximate kNN search implementation method, with known options including 'pynndescent' and 'rapids'. Original type annotation: KnnTransformerLike | _KnownTransformer | None",
        title="Transformer",
    )
    metric: Optional[Any] = Field(
        "euclidean",
        description="Specifies the distance metric to use, either a known metric's name or a callable that returns a distance. Ignored if transformer is an instance. Original type annotation: _Metric | _MetricFn",
        title="Metric",
    )
    metric_kwds: Optional[Any] = Field(
        {},
        description="Options for the metric, ignored if transformer is an instance. Original type annotation: Mapping[str, Any]",
        title="Metric Kwds",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Specifies a numpy random seed, ignored if transformer is an instance. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    key_added: Any = Field(
        None,
        description="Specifies where the neighbors data is stored, with options for custom storage locations. Original type annotation: str | None",
        title="Key Added",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether to return a copy instead of writing to adata. Original type annotation: bool",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.neighbors")
    _products_original = PrivateAttr(
        default=[
            'data.uns["neighbors"]',
            'data.obsp["distances"]',
            'data.obsp["connectivities"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingLogP(BaseAPI):
    """
    Logarithmize the data matrix. Computes :math:`X = \\log(X + 1)`, where :math:`log` denotes the natural logarithm unless a different base is given.
    """

    data: Any = Field(
        ...,
        description="The (annotated) data matrix of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes.",
        title="Data",
    )
    base: Any = Field(
        None,
        description="Base of the logarithm. Natural logarithm is used by default.",
        title="Base",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether a copy of the data is returned when an AnnData object is passed.",
        title="Copy",
    )
    chunked: Any = Field(
        None,
        description="Indicates whether to process the data matrix in chunks to save memory, applicable only to AnnData objects.",
        title="Chunked",
    )
    chunk_size: Any = Field(
        None,
        description="Specifies the number of chunks to process the data in.",
        title="Chunk Size",
    )
    layer: Any = Field(
        None, description="Specifies the entry of layers to transform.", title="Layer"
    )
    obsm: Any = Field(
        None, description="Specifies the entry of obsm to transform.", title="Obsm"
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.log1p")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingHighlyVariableGenes(BaseAPI):
    """
    Annotate highly variable genes according to different flavors like 'seurat', 'cell_ranger', 'seurat_v3', or 'seurat_v3_paper'. Each flavor implements a different method for identifying highly variable genes based on mean expression or normalized variance. The function also provides options for handling batch effects and mimics Seurat's naming conventions for certain scenarios.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes.",
        title="Adata",
    )
    layer: Any = Field(
        None,
        description="If provided, use `adata.layers[layer]` for expression values instead of `adata.X`.",
        title="Layer",
    )
    n_top_genes: Any = Field(
        None,
        description="Number of highly-variable genes to keep. Mandatory if `flavor='seurat_v3'`.",
        title="N Top Genes",
    )
    min_disp: Optional[Any] = Field(
        0.5,
        description="Cutoff for the minimum dispersion. Ignored if `flavor='seurat_v3'`.",
        title="Min Disp",
    )
    max_disp: Optional[Any] = Field(
        "inf",
        description="Cutoff for the maximum dispersion. Ignored if `flavor='seurat_v3`.",
        title="Max Disp",
    )
    min_mean: Optional[Any] = Field(
        0.0125,
        description="Cutoff for the minimum mean. Ignored if `flavor='seurat_v3'`.",
        title="Min Mean",
    )
    max_mean: Optional[Any] = Field(
        3,
        description="Cutoff for the maximum mean. Ignored if `flavor='seurat_v3'`.",
        title="Max Mean",
    )
    span: Optional[Any] = Field(
        0.3,
        description="The fraction of data used when estimating variance in the loess model fit if `flavor='seurat_v3'`.",
        title="Span",
    )
    n_bins: Optional[Any] = Field(
        20,
        description="Number of bins for binning the mean gene expression for normalization.",
        title="N Bins",
    )
    flavor: Optional[Any] = Field(
        "seurat",
        description="Method to identify highly variable genes. Options include 'seurat', 'cell_ranger', 'seurat_v3', 'seurat_v3_paper'.",
        title="Flavor",
    )
    subset: Optional[Any] = Field(
        False,
        description="Subset to highly-variable genes if `True`, otherwise indicate highly variable genes.",
        title="Subset",
    )
    inplace: Optional[Any] = Field(
        True,
        description="Whether to place calculated metrics in `.var` or return them.",
        title="Inplace",
    )
    batch_key: Any = Field(
        None,
        description="Specify batch key to select highly-variable genes within each batch separately and merge.",
        title="Batch Key",
    )
    check_values: Optional[Any] = Field(
        True,
        description="Check if counts in selected layer are integers. Used for `flavor='seurat_v3'` or `'seurat_v3_paper'`.",
        title="Check Values",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.highly_variable_genes")
    _products_original = PrivateAttr(
        default=[
            'data.var["highly_variable"]',
            'data.var["means"]',
            'data.var["dispersions"]',
            'data.var["dispersions_norm"]',
            'data.var["variances"]',
            'data.var["variances_norm"]',
            'data.var["highly_variable_rank"]',
            'data.var["highly_variable_nbatches"]',
            'data.var["highly_variable_intersection"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingPca(BaseAPI):
    """
    Principal component analysis :cite:p:'Pedregosa2011'. Computes PCA coordinates, loadings and variance decomposition. Uses the implementation of scikit-learn :cite:p:'Pedregosa2011'. In previous versions, computing a PCA on a sparse matrix would make a dense copy of the array for mean centering. As of scanpy 1.5.0, mean centering is implicit. While results are extremely similar, they are not exactly the same. If you would like to reproduce the old results, pass a dense array.
    """

    data: Any = Field(
        ...,
        description="The (annotated) data matrix of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes.",
        title="Data",
    )
    n_comps: Any = Field(
        None, description="Number of principal components to compute.", title="N Comps"
    )
    layer: Any = Field(
        None, description="Layer of `adata` to use as expression values.", title="Layer"
    )
    zero_center: Optional[Any] = Field(
        True,
        description="Determines whether to compute standard PCA from covariance matrix or omit zero-centering variables.",
        title="Zero Center",
    )
    svd_solver: Any = Field(
        None,
        description="Specifies the SVD solver to use for PCA computation.",
        title="Svd Solver",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Allows changing initial states for optimization.",
        title="Random State",
    )
    return_info: Optional[Any] = Field(
        False,
        description="Relevant when not passing an AnnData object.",
        title="Return Info",
    )
    mask_var: Optional[Any] = Field(
        0,
        description="Specifies a set of genes to run PCA on, defaulting to highly variable genes if available.",
        title="Mask Var",
    )
    use_highly_variable: Any = Field(
        None,
        description="Determines whether to use highly variable genes only.",
        title="Use Highly Variable",
    )
    dtype: Optional[Any] = Field(
        "float32",
        description="Numpy data type string for result conversion.",
        title="Dtype",
    )
    chunked: Optional[Any] = Field(
        False,
        description="Determines whether to perform incremental PCA on segments or full PCA.",
        title="Chunked",
    )
    chunk_size: Any = Field(
        None,
        description="Number of observations to include in each chunk for incremental PCA.",
        title="Chunk Size",
    )
    key_added: Any = Field(
        None,
        description="Specifies where the PCA results are stored in the AnnData object.",
        title="Key Added",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether a copy is returned when passing an AnnData object.",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.pca")
    _products_original = PrivateAttr(
        default=[
            'data.obsm["X_pca"]',
            'data.varm["PCs"]',
            'data.uns["pca"]["variance_ratio"]',
            'data.uns["pca"]["variance"]',
        ]
    )
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingCalculateQcMetrics(BaseAPI):
    """
    Calculate quality control metrics. Calculates a number of qc metrics for an AnnData object, see section 'Returns' for specifics. Largely based on calculateQCMetrics from scater. Currently is most efficient on a sparse CSR or dense matrix. Note that this method can take a while to compile on the first call. That result is then cached to disk to be used later.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    expr_type: Optional[Any] = Field(
        "counts",
        description="Name of kind of values in X. Original type annotation: str",
        title="Expr Type",
    )
    var_type: Optional[Any] = Field(
        "genes",
        description="The kind of thing the variables are. Original type annotation: str",
        title="Var Type",
    )
    qc_vars: Optional[Any] = Field(
        [],
        description="Keys for boolean columns of `.var` which identify variables you could want to control for (e.g. 'ERCC' or 'mito'). Original type annotation: Collection[str] | str",
        title="Qc Vars",
    )
    percent_top: Optional[Any] = Field(
        [50, 100, 200, 500],
        description="List of ranks at which the cumulative proportion of expression will be reported as a percentage. Original type annotation: Collection[int] | None",
        title="Percent Top",
    )
    layer: Any = Field(
        None,
        description="If provided, use `adata.layers[layer]` for expression values instead of `adata.X`. Original type annotation: str | None",
        title="Layer",
    )
    use_raw: Optional[Any] = Field(
        False,
        description="If True, use `adata.raw.X` for expression values instead of `adata.X`. Original type annotation: bool",
        title="Use Raw",
    )
    inplace: Optional[Any] = Field(
        False,
        description="Whether to place calculated metrics in `adata`'s `.obs` and `.var`. Original type annotation: bool",
        title="Inplace",
    )
    log1p: Optional[Any] = Field(
        True,
        description="Set to `False` to skip computing `log1p` transformed annotations. Original type annotation: bool",
        title="Log1P",
    )
    parallel: Any = Field(
        None,
        description="No description available. Original type annotation: bool | None",
        title="Parallel",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.calculate_qc_metrics")
    _products_original = PrivateAttr(
        default=[
            'data.obs["total_genes_by_counts"]',
            'data.obs["total_counts"]',
            'data.obs["pct_counts_in_top_50_genes"]',
            'data.obs["pct_counts_in_top_100_genes"]',
            'data.obs["pct_counts_in_top_200_genes"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingFilterCells(BaseAPI):
    """
    Filter cell outliers based on counts and numbers of genes expressed. For instance, only keep cells with at least `min_counts` counts or `min_genes` genes expressed. This is to filter measurement outliers, i.e. “unreliable” observations. Only provide one of the optional parameters `min_counts`, `min_genes`, `max_counts`, `max_genes` per call.
    """

    data: Any = Field(..., description="string", title="Data")
    min_counts: Any = Field(None, description="string", title="Min Counts")
    min_genes: Any = Field(None, description="string", title="Min Genes")
    max_counts: Any = Field(None, description="string", title="Max Counts")
    max_genes: Any = Field(None, description="string", title="Max Genes")
    inplace: Optional[Any] = Field(True, description="string", title="Inplace")
    copy_: Optional[Any] = Field(
        False, alias="copy", description="string", title="Copy"
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.filter_cells")
    _products_original = PrivateAttr(
        default=["data.X", 'data.obs["n_counts"]', 'data.obs["n_genes"]']
    )
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingFilterGenes(BaseAPI):
    """
    Filter genes based on number of cells or counts.

    Keep genes that have at least `min_counts` counts or are expressed in at
    least `min_cells` cells or have at most `max_counts` counts or are expressed
    in at most `max_cells` cells.

    Only provide one of the optional parameters `min_counts`, `min_cells`,
    `max_counts`, `max_cells` per call.
    """

    data: Any = Field(
        ...,
        description="An annotated data matrix of shape `n_obs` × `n_vars`. Rows correspond\nto cells and columns to genes.\nOriginal type annotation: AnnData | _CSMatrix | np.ndarray | DaskArray",
        title="Data",
    )
    min_counts: Any = Field(
        None,
        description="Minimum number of counts required for a gene to pass filtering.\nOriginal type annotation: int | None",
        title="Min Counts",
    )
    min_cells: Any = Field(
        None,
        description="Minimum number of cells expressed required for a gene to pass filtering.\nOriginal type annotation: int | None",
        title="Min Cells",
    )
    max_counts: Any = Field(
        None,
        description="Maximum number of counts required for a gene to pass filtering.\nOriginal type annotation: int | None",
        title="Max Counts",
    )
    max_cells: Any = Field(
        None,
        description="Maximum number of cells expressed required for a gene to pass filtering.\nOriginal type annotation: int | None",
        title="Max Cells",
    )
    inplace: Optional[Any] = Field(
        True,
        description="Perform computation inplace or return result.\nOriginal type annotation: bool",
        title="Inplace",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="No description available.\nOriginal type annotation: bool",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.filter_genes")
    _products_original = PrivateAttr(
        default=["data.X", 'data.var["n_counts"]', 'data.var["n_genes"]']
    )
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingNormalizeTotal(BaseAPI):
    """
    Normalize counts per cell. Normalize each cell by total counts over all genes, so that every cell has the same total count after normalization. If choosing `target_sum=1e6`, this is CPM normalization. If `exclude_highly_expressed=True`, very highly expressed genes are excluded from the computation of the normalization factor (size factor) for each cell. This is meaningful as these can strongly influence the resulting normalized values for all other genes. Similar functions are used by Seurat, Cell Ranger, or SPRING. When used with a Dask Array in adata.X, this function will have to call functions that trigger `.compute()` on the Dask Array if `exclude_highly_expressed` is `True`, `layer_norm` is not `None`, or if `key_added` is not `None`.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes.",
        title="Adata",
    )
    target_sum: Any = Field(
        None,
        description="If `None`, after normalization, each observation (cell) has a total count equal to the median of total counts for observations (cells) before normalization.",
        title="Target Sum",
    )
    exclude_highly_expressed: Optional[Any] = Field(
        False,
        description="Exclude (very) highly expressed genes for the computation of the normalization factor (size factor) for each cell.",
        title="Exclude Highly Expressed",
    )
    max_fraction: Optional[Any] = Field(
        0.05,
        description="If `exclude_highly_expressed=True`, consider cells as highly expressed that have more counts than `max_fraction` of the original total counts in at least one cell.",
        title="Max Fraction",
    )
    key_added: Any = Field(
        None,
        description="Name of the field in `adata.obs` where the normalization factor is stored.",
        title="Key Added",
    )
    layer: Any = Field(
        None,
        description="Layer to normalize instead of `X`. If `None`, `X` is normalized.",
        title="Layer",
    )
    layers: Any = Field(None, description="No description available.", title="Layers")
    layer_norm: Any = Field(
        None, description="No description available.", title="Layer Norm"
    )
    inplace: Optional[Any] = Field(
        True,
        description="Whether to update `adata` or return dictionary with normalized copies of `adata.X` and `adata.layers`.",
        title="Inplace",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Whether to modify copied input object. Not compatible with inplace=False.",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.normalize_total")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingRegressOut(BaseAPI):
    """
    Regress out (mostly) unwanted sources of variation. Uses simple linear regression. This is inspired by Seurat's `regressOut` function in R :cite:p:`Satija2015`. Note that this function tends to overcorrect in certain circumstances as described in :issue:`526`.
    """

    adata: Any = Field(..., description="string", title="Adata")
    keys: Any = Field(..., description="string", title="Keys")
    layer: Any = Field(None, description="string", title="Layer")
    n_jobs: Any = Field(None, description="string", title="N Jobs")
    copy_: Optional[Any] = Field(
        False, alias="copy", description="string", title="Copy"
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.regress_out")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingScale(BaseAPI):
    """
    Scale data to unit variance and zero mean.

    .. note::
        Variables (genes) that do not display any variation (are constant across
        all observations) are retained and (for zero_center==True) set to 0
        during this operation. In the future, they might be set to NaNs.
    """

    data: Any = Field(
        ...,
        description="The (annotated) data matrix of shape `n_obs` × `n_vars`.\nRows correspond to cells and columns to genes.\nOriginal type annotation: AnnData | _CSMatrix | np.ndarray | DaskArray",
        title="Data",
    )
    zero_center: Optional[Any] = Field(
        True,
        description="If `False`, omit zero-centering variables, which allows to handle sparse\ninput efficiently.\nOriginal type annotation: bool",
        title="Zero Center",
    )
    max_value: Any = Field(
        None,
        description="Clip (truncate) to this value after scaling. If `None`, do not clip.\nOriginal type annotation: float | None",
        title="Max Value",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Whether this function should be performed inplace. If an AnnData object\nis passed, this also determines if a copy is returned.\nOriginal type annotation: bool",
        title="Copy",
    )
    layer: Any = Field(
        None,
        description="If provided, which element of layers to scale.\nOriginal type annotation: str | None",
        title="Layer",
    )
    obsm: Any = Field(
        None,
        description="If provided, which element of obsm to scale.\nOriginal type annotation: str | None",
        title="Obsm",
    )
    mask_obs: Any = Field(
        None,
        description="Restrict both the derivation of scaling parameters and the scaling itself\nto a certain set of observations. The mask is specified as a boolean array\nor a string referring to an array in :attr:`~anndata.AnnData.obs`.\nThis will transform data from csc to csr format if `issparse(data)`.\nOriginal type annotation: NDArray[np.bool_] | str | None",
        title="Mask Obs",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.scale")
    _products_original = PrivateAttr(
        default=["data.X", 'data.var["mean"]', 'data.var["std"]', 'data.var["var"]']
    )
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingSample(BaseAPI):
    """
    Sample observations or variables with or without replacement.
    """

    data: Any = Field(
        ...,
        description="The (annotated) data matrix of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes.",
        title="Data",
    )
    fraction: Any = Field(
        None,
        description="Sample to this `fraction` of the number of observations or variables. Can be larger than 1.0 if `replace=True`. See `axis` and `replace`.",
        title="Fraction",
    )
    n: Any = Field(
        None,
        description="Sample to this number of observations or variables. See `axis`.",
        title="N",
    )
    rng: Any = Field(
        None, description="Random seed to change subsampling.", title="Rng"
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether a copy is returned if an :class:`~anndata.AnnData` is passed.",
        title="Copy",
    )
    replace: Optional[Any] = Field(
        False,
        description="If True, samples are drawn with replacement.",
        title="Replace",
    )
    axis: Optional[Any] = Field(
        "obs",
        description="Sample `observations` (axis 0) or `variables` (axis 1).",
        title="Axis",
    )
    p: Any = Field(
        None,
        description="Drawing probabilities (floats) or mask (bools). If `p` is an array of probabilities, it must sum to 1.",
        title="P",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.sample")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="data")


class ScanpyPreprocessingDownsampleCounts(BaseAPI):
    """
    Downsample counts from count matrix. If `counts_per_cell` is specified, each cell will be downsampled. If `total_counts` is specified, the expression matrix will be downsampled to contain at most `total_counts`.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix. Original type annotation: AnnData",
        title="Adata",
    )
    counts_per_cell: Any = Field(
        None,
        description="Target total counts per cell. If a cell has more than 'counts_per_cell', it will be downsampled to this number. Resulting counts can be specified on a per cell basis by passing an array. Should be an integer or integer ndarray with the same length as the number of obs. Original type annotation: int | Collection[int] | None",
        title="Counts Per Cell",
    )
    total_counts: Any = Field(
        None,
        description="Target total counts. If the count matrix has more than `total_counts` it will be downsampled to have this number. Original type annotation: int | None",
        title="Total Counts",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Random seed for subsampling. Original type annotation: _LegacyRandom",
        title="Random State",
    )
    replace: Optional[Any] = Field(
        False,
        description="Whether to sample the counts with replacement. Original type annotation: bool",
        title="Replace",
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Determines whether a copy of `adata` is returned. Original type annotation: bool",
        title="Copy",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.downsample_counts")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingCombat(BaseAPI):
    """
    ComBat function for batch effect correction. Corrects for batch effects by fitting linear models, gains statistical power via an EB framework where information is borrowed across genes. Uses the implementation combat.py.
    """

    adata: Any = Field(
        ...,
        description="Annotated data matrix with original type annotation as AnnData.",
        title="Adata",
    )
    key: Optional[Any] = Field(
        "batch",
        description="Key to a categorical annotation from AnnData.obs to be used for batch effect removal with original type annotation as str.",
        title="Key",
    )
    covariates: Any = Field(
        None,
        description="Additional covariates like adjustment variables or biological conditions, referred to as design matrix X in Equation 2.1, and mod argument in the original combat function in the sva R package. Note: Not including covariates may introduce bias or remove biological signal in unbalanced designs with original type annotation as Collection[str] | None.",
        title="Covariates",
    )
    inplace: Optional[Any] = Field(
        True,
        description="Whether to replace adata.X or return the corrected data with original type annotation as bool.",
        title="Inplace",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.combat")
    _products_original = PrivateAttr(default=["data.X"])
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingScrublet(BaseAPI):
    """
    Predict doublets using Scrublet. Predict cell doublets using a nearest-neighbor classifier of observed transcriptomes and simulated doublets, best with raw counts matrix from a single sample or similar samples. This function is a wrapper around pre-processing functions in Scanpy and directly calls Scrublet().
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix of cells and genes, expected to be un-normalized if adata_sim is not supplied.",
        title="Adata",
    )
    adata_sim: Any = Field(
        None,
        description="An optional annData object generated for advanced use cases, with the same number of variables as adata.",
        title="Adata Sim",
    )
    batch_key: Any = Field(
        None,
        description="An optional column name in adata that distinguishes between batches.",
        title="Batch Key",
    )
    sim_doublet_ratio: Optional[Any] = Field(
        2.0,
        description="The number of doublets to simulate relative to the observed transcriptomes.",
        title="Sim Doublet Ratio",
    )
    expected_doublet_rate: Optional[Any] = Field(
        0.05,
        description="The estimated doublet rate for the experiment when adata_sim is not supplied.",
        title="Expected Doublet Rate",
    )
    stdev_doublet_rate: Optional[Any] = Field(
        0.02,
        description="Uncertainty in the expected doublet rate when adata_sim is not supplied.",
        title="Stdev Doublet Rate",
    )
    synthetic_doublet_umi_subsampling: Optional[Any] = Field(
        1.0,
        description="Rate for sampling UMIs when creating synthetic doublets.",
        title="Synthetic Doublet Umi Subsampling",
    )
    knn_dist_metric: Optional[Any] = Field(
        "euclidean",
        description="The distance metric used when finding nearest neighbors.",
        title="Knn Dist Metric",
    )
    normalize_variance: Optional[Any] = Field(
        True,
        description="Whether to normalize the data such that each gene has a variance of 1.",
        title="Normalize Variance",
    )
    log_transform: Optional[Any] = Field(
        False,
        description="Indicates whether to log-transform the data before PCA.",
        title="Log Transform",
    )
    mean_center: Optional[Any] = Field(
        True,
        description="Indicates whether to center the data so that each gene has a mean of 0.",
        title="Mean Center",
    )
    n_prin_comps: Optional[Any] = Field(
        30,
        description="Number of principal components used to embed transcriptomes before constructing k-nearest-neighbor graph.",
        title="N Prin Comps",
    )
    use_approx_neighbors: Any = Field(
        None,
        description="Whether to use the approximate nearest neighbor method for the KNN classifier.",
        title="Use Approx Neighbors",
    )
    get_doublet_neighbor_parents: Optional[Any] = Field(
        False,
        description="Whether to return the parent transcriptomes that generated the doublet neighbors of each observed transcriptome.",
        title="Get Doublet Neighbor Parents",
    )
    n_neighbors: Any = Field(
        None,
        description="Number of neighbors used to construct the KNN graph of observed transcriptomes and simulated doublets.",
        title="N Neighbors",
    )
    threshold: Any = Field(
        None,
        description="Doublet score threshold for identifying transcriptomes as doublets.",
        title="Threshold",
    )
    verbose: Optional[Any] = Field(
        True, description="Indicates whether to log progress updates.", title="Verbose"
    )
    copy_: Optional[Any] = Field(
        False,
        alias="copy",
        description="Whether to return a copy of the input data with Scrublet results added.",
        title="Copy",
    )
    random_state: Optional[Any] = Field(
        0,
        description="Initial state for doublet simulation and nearest neighbors.",
        title="Random State",
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.scrublet")
    _products_original = PrivateAttr(
        default=[
            'data.obs["doublet_score"]',
            'data.obs["predicted_doublet"]',
            'data.uns["scrublet"]["doublet_scores_sim"]',
            'data.uns["scrublet"]["doublet_parents"]',
            'data.uns["scrublet"]["parameters"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


class ScanpyPreprocessingScrubletSimulateDoublets(BaseAPI):
    """
    Simulate doublets by adding the counts of random observed transcriptome pairs.
    """

    adata: Any = Field(
        ...,
        description="The annotated data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes. Genes should have been filtered for expression and variability, and the object should contain raw expression of the same dimensions.",
        title="Adata",
    )
    layer: Any = Field(
        None,
        description="Layer of adata where raw values are stored, or 'X' if values are in .X.",
        title="Layer",
    )
    sim_doublet_ratio: Optional[Any] = Field(
        2.0,
        description="Number of doublets to simulate relative to the number of observed transcriptomes. If None, self.sim_doublet_ratio is used.",
        title="Sim Doublet Ratio",
    )
    synthetic_doublet_umi_subsampling: Optional[Any] = Field(
        1.0,
        description="Rate for sampling UMIs when creating synthetic doublets. If 1.0, each doublet is created by simply adding the UMIs from two randomly sampled observed transcriptomes. For values less than 1, the UMI counts are added and then randomly sampled at the specified rate.",
        title="Synthetic Doublet Umi Subsampling",
    )
    random_seed: Optional[Any] = Field(
        0, description="No description available.", title="Random Seed"
    )
    _api_name = PrivateAttr(default="scanpy.preprocessing.scrublet_simulate_doublets")
    _products_original = PrivateAttr(
        default=[
            'data.obsm["scrublet"]["doublet_parents"]',
            'data.uns["scrublet"]["parameters"]',
        ]
    )
    _data_name = PrivateAttr(default="adata")


TOOLS_DICT = {
    "scanpy.preprocessing.neighbors": ScanpyPreprocessingNeighbors,
    "scanpy.preprocessing.log1p": ScanpyPreprocessingLogP,
    "scanpy.preprocessing.highly_variable_genes": ScanpyPreprocessingHighlyVariableGenes,
    "scanpy.preprocessing.pca": ScanpyPreprocessingPca,
    "scanpy.preprocessing.calculate_qc_metrics": ScanpyPreprocessingCalculateQcMetrics,
    "scanpy.preprocessing.filter_cells": ScanpyPreprocessingFilterCells,
    "scanpy.preprocessing.filter_genes": ScanpyPreprocessingFilterGenes,
    "scanpy.preprocessing.normalize_total": ScanpyPreprocessingNormalizeTotal,
    "scanpy.preprocessing.regress_out": ScanpyPreprocessingRegressOut,
    "scanpy.preprocessing.scale": ScanpyPreprocessingScale,
    "scanpy.preprocessing.sample": ScanpyPreprocessingSample,
    "scanpy.preprocessing.downsample_counts": ScanpyPreprocessingDownsampleCounts,
    "scanpy.preprocessing.combat": ScanpyPreprocessingCombat,
    "scanpy.preprocessing.scrublet": ScanpyPreprocessingScrublet,
    "scanpy.preprocessing.scrublet_simulate_doublets": ScanpyPreprocessingScrubletSimulateDoublets,
}
