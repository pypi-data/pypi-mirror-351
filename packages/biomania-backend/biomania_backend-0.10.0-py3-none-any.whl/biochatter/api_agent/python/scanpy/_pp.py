from typing import Literal
from pydantic import BaseModel, PrivateAttr, Field, model_validator

from biochatter.api_agent.base.agent_abc import BaseAPI
from .base import ScanpyAPI

# Jiahang: unfinished
class ScPpNeighbors(ScanpyAPI):
    """Compute the nearest neighbors distance matrix and a neighborhood graph of observations."""

    _api_name: str = PrivateAttr(default='sc.pp.neighbors')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix")
    n_neighbors: int = Field(15, description="The size of local neighborhood (in terms of number of neighboring data points) used for manifold approximation.")
    n_pcs: int | None = Field(None, description="Number of principal components to use.")
    knn: bool = Field(True, description="If True, use a hard threshold to restrict the number of neighbors to n_neighbors, that is, consider a knn graph. Otherwise, use a Gaussian Kernel to assign low weights to neighbors more distant than the n_neighbors nearest neighbor.")


class ScPpCalculateQCMetrics(ScanpyAPI):
    """Calculate quality control metrics for the data matrix."""

    _api_name: str = PrivateAttr(default='sc.pp.calculate_qc_metrics')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix")
    expr_type: str = Field("counts", description="Name of kind of values in X")
    var_type: str = Field("genes", description="The kind of thing the variables are")
    qc_vars: str = Field("", description="Keys for boolean columns of .var for control variables")
    percent_top: str = Field("50,100,200,500", description="Ranks for library complexity assessment")
    layer: str = Field(None, description="Layer to use for expression values")
    use_raw: bool = Field(False, description="Use adata.raw.X instead of adata.X")
    inplace: bool = Field(False, description="Place calculated metrics in adata's .obs and .var")
    log1p: bool = Field(True, description="Compute log1p transformed annotations")
    parallel: bool | None = Field(None, description="Parallel computation flag")



class ScPpFilterCells(ScanpyAPI):
    """Filter cells based on number of gene counts."""
    _api_name: str = PrivateAttr(default='sc.pp.filter_cells')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="The (annotated) data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    min_counts: int | None = Field(None, description="Minimum number of counts required for a cell to pass filtering.")
    min_genes: int | None = Field(
        None, description="Minimum number of genes expressed required for a cell to pass filtering."
    )
    max_counts: int | None = Field(None, description="Maximum number of counts required for a cell to pass filtering.")
    max_genes: int | None = Field(
        None, description="Maximum number of genes expressed required for a cell to pass filtering."
    )
    inplace: bool = Field(True, description="Perform computation inplace or return result.")



class ScPpFilterGenes(ScanpyAPI):
    """Filter genes based on number of cell counts."""

    _api_name: str = PrivateAttr(default='sc.pp.filter_genes')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="An annotated data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    min_counts: int | None = Field(None, description="Minimum number of counts required for a gene to pass filtering.")
    min_cells: int | None = Field(
        None,
        description="Minimum number of cells in which the gene is expressed required for the gene to pass filtering.",
    )
    max_counts: int | None = Field(None, description="Maximum number of counts allowed for a gene to pass filtering.")
    max_cells: int | None = Field(
        None,
        description="Maximum number of cells in which the gene is expressed allowed for the gene to pass filtering.",
    )
    inplace: bool = Field(True, description="Perform computation inplace or return result.")



class ScPpHighlyVariableGenes(ScanpyAPI):
    """Identify highly variable genes based on mean and variance of gene expressions."""
    _api_name: str = PrivateAttr(default='sc.pp.highly_variable_genes')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data", description="Annotated data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes."
    )
    layer: str | None = Field(None, description="Use adata.layers[layer] for expression values instead of adata.X.")
    n_top_genes: int | None = Field(
        None, description="Number of highly-variable genes to keep. Mandatory if flavor='seurat_v3'."
    )
    min_mean: float = Field(
        0.0125,
        description="Minimum mean expression threshold for highly variable genes. Ignored if flavor='seurat_v3'.",
    )
    max_mean: float = Field(
        3, description="Maximum mean expression threshold for highly variable genes. Ignored if flavor='seurat_v3'."
    )
    min_disp: float = Field(
        0.5, description="Minimum dispersion threshold for highly variable genes. Ignored if flavor='seurat_v3'."
    )
    max_disp: float = Field(
        1e9,
        description="Maximum dispersion threshold for highly variable genes. Ignored if flavor='seurat_v3'. Note that we use 1e9 instead of inf as scanpy default to avoid JSON representation error.",
    )
    span: float = Field(
        0.3,
        description="Fraction of the data (cells) used in variance estimation for the loess model fit if flavor='seurat_v3'.",
    )
    n_bins: int = Field(
        20, description="Number of bins for binning the mean gene expression. Normalization is done per bin."
    )
    flavor: Literal["seurat", "cell_ranger", "seurat_v3", "seurat_v3_paper"] = Field(
        "seurat", description="The method to use for identifying highly variable genes."
    )
    subset: bool = Field(False, description="If True, subset to highly-variable genes, otherwise just indicate them.")
    # Jiahang: predict to be False...
    inplace: bool = Field(True, description="Whether to place calculated metrics in .var or return them.")
    batch_key: str | None = Field(
        None, description="If specified, highly-variable genes are selected separately within each batch and merged."
    )
    check_values: bool = Field(
        True, description="Whether to check if counts in selected layer are integers (relevant for flavor='seurat_v3')."
    )

class ScPpLog1p(ScanpyAPI):
    """Logarithmize the data matrix."""
    _api_name: str = PrivateAttr(default='sc.pp.log1p')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="The (annotated) data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    base: float | None = Field(None, description="Base of the logarithm. Natural logarithm is used by default.")
    chunked: bool | None = Field(
        None, description="Process the data matrix in chunks, which will save memory. Applies only to AnnData."
    )
    chunk_size: int | None = Field(None, description="Number of observations (n_obs) per chunk to process the data in.")
    layer: str | None = Field(None, description="Entry of layers to transform.")
    obsm: str | None = Field(None, description="Entry of obsm to transform.")

    def _arg_repr(self, key, val) -> str:
        if key == self._data_name:
            return f"{val}" # log1p requires the first arg to be positional arg. bad implementation.
        if type(val) == str and key != self._data_name:
            return f"{key}='{val}'"
        return f"{key}={val}"



class ScPpPCA(ScanpyAPI):
    """Apply Principal Component Analysis (PCA) for dimensionality reduction to data matrix ."""
    _api_name: str = PrivateAttr(default='sc.pp.pca')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="The (annotated) data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    n_comps: int | None = Field(
        None,
        description="Number of principal components to compute. Defaults to 50, or 1 - minimum dimension size of selected representation.",
    )
    layer: str | None = Field(None, description="If provided, which element of layers to use for PCA.")
    zero_center: bool = Field(
        True,
        description="If True, compute standard PCA from covariance matrix. If False, omit zero-centering variables.",
    )
    svd_solver: str | None = Field(
        None, description="SVD solver to use. Options: 'auto', 'arpack', 'randomized', 'lobpcg', or 'tsqr'."
    )
    random_state: int | None = Field(0, description="Change to use different initial states for the optimization.")
    return_info: bool = Field(
        False, description="Only relevant when not passing an AnnData. Whether to return PCA info."
    )
    mask_var: str | None = Field(
        None, description="To run PCA only on certain genes. Default is .var['highly_variable'] if available."
    )
    use_highly_variable: bool | None = Field(
        None,
        description="Whether to use highly variable genes only, stored in .var['highly_variable']. Deprecated in 1.10.0.",
    )
    dtype: str = Field("float32", description="Numpy data type string to which to convert the result.")
    chunked: bool = Field(
        False, description="If True, perform incremental PCA using sklearn IncrementalPCA or dask-ml IncrementalPCA."
    )
    chunk_size: int | None = Field(
        None, description="Number of observations to include in each chunk. Required if chunked=True."
    )



class ScPpNormalizeTotal(ScanpyAPI):
    """Normalize total counts per cell to a target sum."""
    _api_name: str = PrivateAttr(default='sc.pp.normalize_total')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="The annotated data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    target_sum: float | None = Field(
        None,
        description="Target sum after normalization. If None, each cell will have total counts equal to the median before normalization.",
    )
    exclude_highly_expressed: bool = Field(
        False, description="If True, exclude highly expressed genes from normalization computation."
    )
    max_fraction: float = Field(
        0.05,
        description="If exclude_highly_expressed=True, consider a gene as highly expressed if it has more than max_fraction of the total counts in at least one cell.",
    )
    key_added: str | None = Field(
        None, description="Name of the field in adata.obs where the normalization factor is stored."
    )
    layer: str | None = Field(None, description="Layer to normalize instead of X. If None, normalize X.")
    inplace: bool = Field(
        True, description="Whether to update adata or return normalized copies of adata.X and adata.layers."
    )



class ScPpRegressOut(ScanpyAPI):
    """Regress out unwanted sources of variation from the data matrix."""
    _api_name: str = PrivateAttr(default='sc.pp.regress_out')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="The annotated data matrix.")
    keys: str | list[str] = Field(
        ...,
        description="Keys for observation annotation on which to regress on. Can be a single key or a list of keys.",
    )
    layer: str | None = Field(None, description="Layer to regress on, if provided.")
    n_jobs: int | None = Field(
        None, description="Number of jobs for parallel computation. None means using default n_jobs."
    )



class ScPpScale(ScanpyAPI):
    """Scale the data matrix to unit variance and zero mean."""
    _api_name: str = PrivateAttr(default='sc.pp.scale')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="The (annotated) data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    zero_center: bool = Field(
        True, description="If False, omit zero-centering variables, which allows to handle sparse input efficiently."
    )
    max_value: float | None = Field(
        None, description="Clip (truncate) to this value after scaling. If None, do not clip."
    )
    layer: str | None = Field(None, description="If provided, which element of layers to scale.")
    obsm: str | None = Field(None, description="If provided, which element of obsm to scale.")
    mask_obs: str | None = Field(
        None,
        description="Restrict the scaling to a certain set of observations. The mask is specified as a boolean array or a string referring to an array in obs.",
    )



class ScPpSample(ScanpyAPI):
    """Sample observations or variables with or without replacement."""
    _api_name: str = PrivateAttr(default='sc.pp.sample')
    _data_name: str = PrivateAttr(default='data')
    data: str = Field(
        "data",
        description="The (annotated) data matrix of shape n_obs x n_vars. Rows correspond to cells and columns to genes.",
    )
    fraction: float | None = Field(None, description="Sample to this fraction of the number of observations.")
    n_obs: int | None = Field(None, description="Sample to this number of observations.")
    random_state: int | None = Field(0, description="Random seed to change subsampling.")



class ScPpDownsampleCounts(ScanpyAPI):
    """Downsample counts in the data matrix."""
    _api_name: str = PrivateAttr(default='sc.pp.downsample_counts')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix.")
    counts_per_cell: int | None = Field(
        None,
        description="Target total counts per cell. If a cell has more than ‘counts_per_cell’, it will be downsampled to this number. Can be an integer or integer ndarray with same length as number of observations.",
    )
    total_counts: int | None = Field(
        None,
        description="Target total counts. If the count matrix has more than total_counts, it will be downsampled to this number.",
    )
    random_state: int | None = Field(0, description="Random seed for subsampling.")
    replace: bool = Field(False, description="Whether to sample the counts with replacement.")



class ScPpRecipeZheng17(ScanpyAPI):
    """Preprocess data according to the Zheng et al. (2017) recipe."""
    _api_name: str = PrivateAttr(default='sc.pp.recipe_zeng17')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix.")
    n_top_genes: int = Field(1000, description="Number of genes to keep.")
    log: bool = Field(True, description="Take logarithm. If True, log-transform data after filtering.")
    plot: bool = Field(False, description="Show a plot of the gene dispersion vs. mean relation.")



class ScPpRecipeWeinreb17(ScanpyAPI):
    """Preprocess data according to the Weinreb et al. (2017) recipe."""
    _api_name: str = PrivateAttr(default='sc.pp.recipe_weinreb17')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix.")
    log: bool = Field(True, description="Logarithmize data? If True, log-transform the data.")
    mean_threshold: float = Field(0.01, description="Threshold for mean expression of genes.")
    cv_threshold: float = Field(2, description="Threshold for coefficient of variation (CV) for gene dispersion.")
    n_pcs: int = Field(50, description="Number of principal components to use.")
    svd_solver: str = Field("randomized", description="SVD solver to use.")
    random_state: int = Field(0, description="Random state for reproducibility of results.")



class ScPpRecipeSeurat(ScanpyAPI):
    """Preprocess data according to the Seurat recipe."""
    _api_name: str = PrivateAttr(default='sc.pp.recipe_seurat')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix.")
    log: bool = Field(True, description="Logarithmize data? If True, log-transform the data.")
    plot: bool = Field(False, description="Show a plot of the gene dispersion vs. mean relation.")



class ScPpCombat(ScanpyAPI):
    """Remove batch effects from the data matrix using ComBat."""
    _api_name: str = PrivateAttr(default='sc.pp.combat')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix.")
    key: str = Field(
        "batch", description="Key to a categorical annotation from obs that will be used for batch effect removal."
    )
    covariates: list[str] | None = Field(
        None, description="Additional covariates such as adjustment variables or biological conditions."
    )
    inplace: bool = Field(True, description="Whether to replace adata.X or to return the corrected data.")



class ScPpScrublet(ScanpyAPI):
    """Detect doublets in single-cell RNA-seq data using Scrublet."""
    _api_name: str = PrivateAttr(default='sc.pp.scrublet')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field("data", description="Annotated data matrix (n_obs x n_vars).")
    adata_sim: str | None = Field(
        None, description="Optional AnnData object from scrublet_simulate_doublets() with same number of vars as adata."
    )
    batch_key: str | None = Field(None, description="Optional obs column name discriminating between batches.")
    sim_doublet_ratio: float = Field(
        2.0, description="Number of doublets to simulate relative to the number of observed transcriptomes."
    )
    expected_doublet_rate: float = Field(0.05, description="Estimated doublet rate for the experiment.")
    stdev_doublet_rate: float = Field(0.02, description="Uncertainty in the expected doublet rate.")
    synthetic_doublet_umi_subsampling: float = Field(
        1.0, description="Rate for sampling UMIs when creating synthetic doublets."
    )
    knn_dist_metric: str = Field("euclidean", description="Distance metric used for nearest neighbor search.")
    normalize_variance: bool = Field(True, description="Normalize the data such that each gene has a variance of 1.")
    log_transform: bool = Field(False, description="Whether to log-transform the data prior to PCA.")
    mean_center: bool = Field(True, description="If True, center the data such that each gene has a mean of 0.")
    n_prin_comps: int = Field(
        30,
        description="Number of principal components used to embed the transcriptomes prior to KNN graph construction.",
    )
    use_approx_neighbors: bool = Field(
        False, description="Use approximate nearest neighbor method (annoy) for KNN classifier."
    )
    get_doublet_neighbor_parents: bool = Field(
        False, description="If True, return parent transcriptomes that generated the doublet neighbors."
    )
    n_neighbors: int | None = Field(None, description="Number of neighbors used to construct the KNN graph.")
    threshold: float | None = Field(None, description="Doublet score threshold for calling a transcriptome a doublet.")
    verbose: bool = Field(True, description="If True, log progress updates.")



class ScPpScrubletSimulateDoublets(ScanpyAPI):
    """Simulate doublets by adding the counts of random observed transcriptome pairs."""
    _api_name: str = PrivateAttr(default='sc.pp.scrublet_simulate_doublets')
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data", description="Annotated data matrix of shape n_obs x n_vars. Rows correspond to cells, columns to genes."
    )
    layer: str | None = Field(
        None, description="Layer of adata where raw values are stored, or 'X' if values are in .X."
    )
    sim_doublet_ratio: float = Field(
        2.0, description="Number of doublets to simulate relative to the number of observed transcriptomes."
    )
    synthetic_doublet_umi_subsampling: float = Field(
        1.0,
        description="Rate for sampling UMIs when creating synthetic doublets. If 1.0, simply add UMIs from two randomly sampled transcriptomes.",
    )
    random_seed: int = Field(0, description="Random seed for reproducibility.")


TOOLS = [
    ScPpNeighbors,
    ScPpCalculateQCMetrics,
    ScPpFilterCells,
    ScPpFilterGenes,
    ScPpHighlyVariableGenes,
    ScPpLog1p,
    ScPpPCA,
    ScPpNormalizeTotal,
    ScPpRegressOut,
    ScPpScale,
    ScPpSample,
    ScPpRecipeZheng17,
    ScPpRecipeWeinreb17,
    ScPpRecipeSeurat,
    ScPpCombat,
    ScPpScrublet,
    ScPpScrubletSimulateDoublets
]

TOOLS_DICT = {tool._api_name.default: tool for tool in TOOLS}