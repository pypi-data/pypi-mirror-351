"""Module for interacting with the `scanpy` API for plotting (`pl`)."""

import uuid
from typing import Any
from pydantic import BaseModel, Field, PrivateAttr

from biochatter.api_agent.base.agent_abc import BaseAPI
from .base import ScanpyAPI

from typing import Literal, Mapping

class ScPlScatter(ScanpyAPI):
    """Scatter plot along observations or variables axes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.scatter",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(default="data", description="Annotated data matrix.")
    x: str | None = Field(default=None, description="x coordinate.")
    y: str | None = Field(default=None, description="y coordinate.")
    color: str | tuple[float, ...] | list[str | tuple[float, ...]] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes, or a hex color specification.",
    )
    use_raw: bool | None = Field(
        default=None,
        description="Whether to use raw attribute of adata. Defaults to True if .raw is present.",
    )
    layers: str | list[str] | None = Field(
        default=None,
        description="Layer(s) to use from adata's layers attribute.",
    )
    basis: str | None = Field(
        default=None,
        description="String that denotes a plotting tool that computed coordinates (e.g., 'pca', 'tsne', 'umap').",
    )
    sort_order: bool = Field(
        default=True,
        description="For continuous annotations used as color parameter, plot data points with higher values on top.",
    )
    groups: str | list[str] | None = Field(
        default=None,
        description="Restrict to specific categories in categorical observation annotation.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot ('2d' or '3d').",
    )
    legend_loc: str | None = Field(
        default="right margin",
        description="Location of legend ('none', 'right margin', 'on data', etc.).",
    )
    size: int | float | None = Field(
        default=None,
        description="Point size. If None, automatically computed as 120000 / n_cells.",
    )
    color_map: str | None = Field(
        default=None,
        description="Color map to use for continuous variables (e.g., 'magma', 'viridis').",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot, do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If True or a str, save the figure. String is appended to default filename.",
    )


### Embeddings
class ScPlPca(ScanpyAPI):
    """Scatter plot of cells in PCA coordinates."""

    _api_name: str = PrivateAttr(
        default="sc.pl.pca",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix.",
    )
    color: str | list[str] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes.",
    )
    components: str | list[str] = Field(
        default="1,2",
        description="For example, ['1,2', '2,3']. To plot all available components use 'all'.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot.",
    )
    legend_loc: str = Field(
        default="right margin",
        description="Location of legend.",
    )
    legend_fontsize: int | float | str | None = Field(
        default=None,
        description="Font size for legend.",
    )
    legend_fontweight: int | str | None = Field(
        default=None,
        description="Font weight for legend.",
    )
    color_map: str | None = Field(
        default=None,
        description="String denoting matplotlib color map.",
    )
    palette: str | list[str] | dict | None = Field(
        default=None,
        description="Colors to use for plotting categorical annotation groups.",
    )
    frameon: bool | None = Field(
        default=None,
        description="Draw a frame around the scatter plot.",
    )
    size: int | float | None = Field(
        default=None,
        description="Point size. If `None`, is automatically computed as 120000 / n_cells.",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot, do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If `True` or a `str`, save the figure.",
    )
    ax: str | None = Field(
        default=None,
        description="A matplotlib axes object.",
    )
    return_fig: bool = Field(
        default=False,
        description="Return the matplotlib figure object.",
    )
    marker: str | None = Field(
        default=".",
        description="Marker symbol.",
    )
    annotate_var_explained: bool = Field(
        default=False,
        description="Annotate the percentage of explained variance.",
    )


class ScPlTsne(ScanpyAPI):
    """Scatter plot of cells in tSNE basis."""

    _api_name: str = PrivateAttr(
        default="sc.pl.tsne",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix.",
    )
    color: str | list[str] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes.",
    )
    gene_symbols: str | None = Field(
        default=None,
        description="Column name in `.var` DataFrame that stores gene symbols.",
    )
    use_raw: bool | None = Field(
        default=None,
        description="Use `.raw` attribute of `adata` for coloring with gene expression.",
    )
    sort_order: bool = Field(
        default=True,
        description="Plot data points with higher values on top for continuous annotations.",
    )
    edges: bool = Field(
        default=False,
        description="Show edges.",
    )
    edges_width: float = Field(
        default=0.1,
        description="Width of edges.",
    )
    edges_color: str | list[float] | list[str] = Field(
        default="grey",
        description="Color of edges.",
    )
    neighbors_key: str | None = Field(
        default=None,
        description="Key for neighbors connectivities.",
    )
    arrows: bool = Field(
        default=False,
        description="Show arrows (deprecated in favor of `scvelo.pl.velocity_embedding`).",
    )
    arrows_kwds: dict[str, Any] | None = Field(
        default=None,
        description="Arguments passed to `quiver()`.",
    )
    groups: str | None = Field(
        default=None,
        description="Restrict to specific categories in categorical observation annotation.",
    )
    components: str | list[str] | None = Field(
        default=None,
        description="Components to plot, e.g., ['1,2', '2,3']. Use 'all' to plot all available components.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot ('2d' or '3d').",
    )
    legend_loc: str = Field(
        default="right margin",
        description="Location of legend.",
    )
    legend_fontsize: int | float | str | None = Field(
        default=None,
        description="Font size for legend.",
    )
    legend_fontweight: int | str = Field(
        default="bold",
        description="Font weight for legend.",
    )
    legend_fontoutline: int | None = Field(
        default=None,
        description="Line width of the legend font outline in pt.",
    )
    size: float | list[float] | None = Field(
        default=None,
        description="Point size. If `None`, computed as 120000 / n_cells.",
    )
    color_map: str | Any | None = Field(
        default=None,
        description="Color map for continuous variables.",
    )
    palette: str | list[str] | Any | None = Field(
        default=None,
        description="Colors for plotting categorical annotation groups.",
    )
    na_color: str | tuple[float, ...] = Field(
        default="lightgray",
        description="Color for null or masked values.",
    )
    na_in_legend: bool = Field(
        default=True,
        description="Include missing values in the legend.",
    )
    frameon: bool | None = Field(
        default=None,
        description="Draw a frame around the scatter plot.",
    )
    vmin: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Lower limit of the color scale.",
    )
    vmax: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Upper limit of the color scale.",
    )
    vcenter: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Center of the color scale, useful for diverging colormaps.",
    )
    norm: Any | None = Field(
        default=None,
        description="Normalization for the colormap.",
    )
    add_outline: bool = Field(
        default=False,
        description="Add a thin border around groups of dots.",
    )
    outline_width: tuple[float, ...] = Field(
        default=(0.3, 0.05),
        description="Width of the outline as a fraction of the scatter dot size.",
    )
    outline_color: tuple[str, ...] = Field(
        default=("black", "white"),
        description="Colors for the outline: border color and gap color.",
    )
    ncols: int = Field(
        default=4,
        description="Number of panels per row.",
    )
    hspace: float = Field(
        default=0.25,
        description="Height of the space between multiple panels.",
    )
    wspace: float | None = Field(
        default=None,
        description="Width of the space between multiple panels.",
    )
    return_fig: bool | None = Field(
        default=None,
        description="Return the matplotlib figure.",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot; do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If `True` or a `str`, save the figure.",
    )
    ax: Any | None = Field(
        default=None,
        description="A matplotlib axes object.",
    )
    # kwargs: dict[str, Any] | None = Field(
    #     default=None,
    #     description="Additional arguments passed to `matplotlib.pyplot.scatter()`.",
    # )
    # Jiahang: kwargs that being sent to internal API are not supported now since it needs
    # to be carefully handled and the handling way should be a standard.


class ScPlUmap(ScanpyAPI):
    """Scatter plot of cells in UMAP basis."""

    _api_name: str = PrivateAttr(
        default="sc.pl.umap",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix.",
    )
    color: str | list[str] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes.",
    )
    mask_obs: str | None = Field(
        default=None,
        description="Mask for observations.",
    )
    gene_symbols: str | None = Field(
        default=None,
        description="Column name in `.var` DataFrame that stores gene symbols.",
    )
    use_raw: bool | None = Field(
        default=None,
        description="Use `.raw` attribute of `adata` for coloring with gene expression.",
    )
    sort_order: bool = Field(
        default=True,
        description="Plot data points with higher values on top for continuous annotations.",
    )
    edges: bool = Field(
        default=False,
        description="Show edges.",
    )
    edges_width: float = Field(
        default=0.1,
        description="Width of edges.",
    )
    edges_color: str | list[float] | list[str] = Field(
        default="grey",
        description="Color of edges.",
    )
    neighbors_key: str | None = Field(
        default=None,
        description="Key for neighbors connectivities.",
    )
    arrows: bool = Field(
        default=False,
        description="Show arrows (deprecated in favor of `scvelo.pl.velocity_embedding`).",
    )
    arrows_kwds: dict[str, Any] | None = Field(
        default=None,
        description="Arguments passed to `quiver()`.",
    )
    groups: str | None = Field(
        default=None,
        description="Restrict to specific categories in categorical observation annotation.",
    )
    components: str | list[str] | None = Field(
        default=None,
        description="Components to plot, e.g., ['1,2', '2,3']. Use 'all' to plot all available components.",
    )
    dimensions: int | None = Field(
        default=None,
        description="Number of dimensions to plot.",
    )
    layer: str | None = Field(
        default=None,
        description="Name of the AnnData object layer to plot.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot ('2d' or '3d').",
    )
    scale_factor: float | None = Field(
        default=None,
        description="Scale factor for the plot.",
    )
    color_map: str | Any | None = Field(
        default=None,
        description="Color map for continuous variables.",
    )
    cmap: str | Any | None = Field(
        default=None,
        description="Alias for `color_map`.",
    )
    palette: str | list[str] | Any | None = Field(
        default=None,
        description="Colors for plotting categorical annotation groups.",
    )
    na_color: str | tuple[float, ...] = Field(
        default="lightgray",
        description="Color for null or masked values.",
    )
    na_in_legend: bool = Field(
        default=True,
        description="Include missing values in the legend.",
    )
    size: float | list[float] | None = Field(
        default=None,
        description="Point size. If `None`, computed as 120000 / n_cells.",
    )
    frameon: bool | None = Field(
        default=None,
        description="Draw a frame around the scatter plot.",
    )
    legend_fontsize: int | float | str | None = Field(
        default=None,
        description="Font size for legend.",
    )
    legend_fontweight: int | str = Field(
        default="bold",
        description="Font weight for legend.",
    )
    legend_loc: str = Field(
        default="right margin",
        description="Location of legend.",
    )
    legend_fontoutline: int | None = Field(
        default=None,
        description="Line width of the legend font outline in pt.",
    )
    colorbar_loc: str = Field(
        default="right",
        description="Location of the colorbar.",
    )
    vmax: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Upper limit of the color scale.",
    )
    vmin: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Lower limit of the color scale.",
    )
    vcenter: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="Center of the color scale, useful for diverging colormaps.",
    )
    norm: Any | None = Field(
        default=None,
        description="Normalization for the colormap.",
    )
    add_outline: bool = Field(
        default=False,
        description="Add a thin border around groups of dots.",
    )
    outline_width: tuple[float, ...] = Field(
        default=(0.3, 0.05),
        description="Width of the outline as a fraction of the scatter dot size.",
    )
    outline_color: tuple[str, ...] = Field(
        default=("black", "white"),
        description="Colors for the outline: border color and gap color.",
    )
    ncols: int = Field(
        default=4,
        description="Number of panels per row.",
    )
    hspace: float = Field(
        default=0.25,
        description="Height of the space between multiple panels.",
    )
    wspace: float | None = Field(
        default=None,
        description="Width of the space between multiple panels.",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot; do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If `True` or a `str`, save the figure.",
    )
    ax: Any | None = Field(
        default=None,
        description="A matplotlib axes object.",
    )
    return_fig: bool | None = Field(
        default=None,
        description="Return the matplotlib figure.",
    )
    marker: str = Field(
        default=".",
        description="Marker symbol.",
    )
    # kwargs: dict[str, Any] | None = Field(
    #     default=None,
    #     description="Additional arguments passed to `matplotlib.pyplot.scatter()`.",
    # )

class ScPlDrawGraph(ScanpyAPI):
    """Parameters for querying the Scanpy `pl.draw_graph` API."""

    _api_name: str = PrivateAttr(
        default="sc.pl.draw_graph",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix.",
    )
    color: str | list[str] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes.",
    )
    gene_symbols: str | None = Field(
        default=None,
        description="Column name in `.var` DataFrame that stores gene symbols.",
    )
    use_raw: bool | None = Field(
        default=None,
        description="Use `.raw` attribute of `adata` for coloring with gene expression.",
    )
    sort_order: bool = Field(
        default=True,
        description=(
            "For continuous annotations used as color parameter, "
            "plot data points with higher values on top of others."
        ),
    )
    edges: bool = Field(
        default=False,
        description="Show edges.",
    )
    edges_width: float = Field(
        default=0.1,
        description="Width of edges.",
    )
    edges_color: str | list[float] | list[str] = Field(
        default="grey",
        description="Color of edges.",
    )
    neighbors_key: str | None = Field(
        default=None,
        description="Where to look for neighbors connectivities.",
    )
    arrows: bool = Field(
        default=False,
        description="Show arrows (deprecated in favor of `scvelo.pl.velocity_embedding`).",
    )
    arrows_kwds: dict[str, Any] | None = Field(
        default=None,
        description="Arguments passed to `quiver()`.",
    )
    groups: str | list[str] | None = Field(
        default=None,
        description="Restrict to a few categories in categorical observation annotation.",
    )
    components: str | list[str] | None = Field(
        default=None,
        description="For instance, ['1,2', '2,3']. To plot all available components use components='all'.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot.",
    )
    legend_loc: str = Field(
        default="right margin",
        description="Location of legend.",
    )
    legend_fontsize: int | float | str | None = Field(
        default=None,
        description="Numeric size in pt or string describing the size.",
    )
    legend_fontweight: int | str = Field(
        default="bold",
        description="Legend font weight.",
    )
    legend_fontoutline: int | None = Field(
        default=None,
        description="Line width of the legend font outline in pt.",
    )
    colorbar_loc: str | None = Field(
        default="right",
        description="Where to place the colorbar for continuous variables.",
    )
    size: float | list[float] | None = Field(
        default=None,
        description="Point size. If None, is automatically computed as 120000 / n_cells.",
    )
    color_map: str | Any | None = Field(
        default=None,
        description="Color map to use for continuous variables.",
    )
    palette: str | list[str] | Any | None = Field(
        default=None,
        description="Colors to use for plotting categorical annotation groups.",
    )
    na_color: str | tuple[float, ...] = Field(
        default="lightgray",
        description="Color to use for null or masked values.",
    )
    na_in_legend: bool = Field(
        default=True,
        description="If there are missing values, whether they get an entry in the legend.",
    )
    frameon: bool | None = Field(
        default=None,
        description="Draw a frame around the scatter plot.",
    )
    vmin: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the lower limit of the color scale.",
    )
    vmax: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the upper limit of the color scale.",
    )
    vcenter: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the center of the color scale.",
    )
    norm: Any | None = Field(
        default=None,
        description="Normalization for the colormap.",
    )
    add_outline: bool = Field(
        default=False,
        description="Add a thin border around groups of dots.",
    )
    outline_width: tuple[float, ...] = Field(
        default=(0.3, 0.05),
        description="Width of the outline as a fraction of the scatter dot size.",
    )
    outline_color: tuple[str, ...] = Field(
        default=("black", "white"),
        description="Colors for the outline: border color and gap color.",
    )
    ncols: int = Field(
        default=4,
        description="Number of panels per row.",
    )
    hspace: float = Field(
        default=0.25,
        description="Height of the space between multiple panels.",
    )
    wspace: float | None = Field(
        default=None,
        description="Width of the space between multiple panels.",
    )
    return_fig: bool | None = Field(
        default=None,
        description="Return the matplotlib figure.",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot; do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If `True` or a `str`, save the figure.",
    )
    ax: Any | None = Field(
        default=None,
        description="A matplotlib axes object.",
    )
    layout: str | None = Field(
        default=None,
        description="One of the `draw_graph()` layouts.",
    )
    # kwargs: dict[str, Any] | None = Field(
    #     default=None,
    #     description="Additional arguments passed to `matplotlib.pyplot.scatter()`.",
    # )


class ScPlSpatial(ScanpyAPI):
    """Parameters for querying the Scanpy `pl.spatial` API."""

    _api_name: str = PrivateAttr(
        default="sc.pl.spatial",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix.",
    )
    color: str | list[str] | None = Field(
        default=None,
        description="Keys for annotations of observations/cells or variables/genes.",
    )
    gene_symbols: str | None = Field(
        default=None,
        description="Column name in `.var` DataFrame that stores gene symbols.",
    )
    use_raw: bool | None = Field(
        default=None,
        description="Use `.raw` attribute of `adata` for coloring with gene expression.",
    )
    layer: str | None = Field(
        default=None,
        description="Name of the AnnData object layer to plot.",
    )
    library_id: str | None = Field(
        default=None,
        description="Library ID for Visium data, e.g., key in `adata.uns['spatial']`.",
    )
    img_key: str | None = Field(
        default=None,
        description=(
            "Key for image data, used to get `img` and `scale_factor` from "
            "'images' and 'scalefactors' entries for this library."
        ),
    )
    img: Any | None = Field(
        default=None,
        description="Image data to plot, overrides `img_key`.",
    )
    scale_factor: float | None = Field(
        default=None,
        description="Scaling factor used to map from coordinate space to pixel space.",
    )
    spot_size: float | None = Field(
        default=None,
        description="Diameter of spot (in coordinate space) for each point.",
    )
    crop_coord: tuple[int, ...] | None = Field(
        default=None,
        description="Coordinates to use for cropping the image (left, right, top, bottom).",
    )
    alpha_img: float = Field(
        default=1.0,
        description="Alpha value for image.",
    )
    bw: bool = Field(
        default=False,
        description="Plot image data in grayscale.",
    )
    sort_order: bool = Field(
        default=True,
        description=(
            "For continuous annotations used as color parameter, plot data points "
            "with higher values on top of others."
        ),
    )
    groups: str | list[str] | None = Field(
        default=None,
        description="Restrict to specific categories in categorical observation annotation.",
    )
    components: str | list[str] | None = Field(
        default=None,
        description="For example, ['1,2', '2,3']. To plot all available components, use 'all'.",
    )
    projection: str = Field(
        default="2d",
        description="Projection of plot.",
    )
    legend_loc: str = Field(
        default="right margin",
        description="Location of legend.",
    )
    legend_fontsize: int | float | str | None = Field(
        default=None,
        description="Numeric size in pt or string describing the size.",
    )
    legend_fontweight: int | str = Field(
        default="bold",
        description="Legend font weight.",
    )
    legend_fontoutline: int | None = Field(
        default=None,
        description="Line width of the legend font outline in pt.",
    )
    colorbar_loc: str | None = Field(
        default="right",
        description="Where to place the colorbar for continuous variables.",
    )
    size: float = Field(
        default=1.0,
        description="Point size. If None, automatically computed as 120000 / n_cells.",
    )
    color_map: str | Any | None = Field(
        default=None,
        description="Color map to use for continuous variables.",
    )
    palette: str | list[str] | Any | None = Field(
        default=None,
        description="Colors to use for plotting categorical annotation groups.",
    )
    na_color: str | tuple[float, ...] | None = Field(
        default=None,
        description="Color to use for null or masked values.",
    )
    na_in_legend: bool = Field(
        default=True,
        description="If there are missing values, whether they get an entry in the legend.",
    )
    frameon: bool | None = Field(
        default=None,
        description="Draw a frame around the scatter plot.",
    )
    vmin: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the lower limit of the color scale.",
    )
    vmax: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the upper limit of the color scale.",
    )
    vcenter: str | float | Any | list[str | float | Any] | None = Field(
        default=None,
        description="The value representing the center of the color scale.",
    )
    norm: Any | None = Field(
        default=None,
        description="Normalization for the colormap.",
    )
    add_outline: bool = Field(
        default=False,
        description="Add a thin border around groups of dots.",
    )
    outline_width: tuple[float, ...] = Field(
        default=(0.3, 0.05),
        description="Width of the outline as a fraction of the scatter dot size.",
    )
    outline_color: tuple[str, ...] = Field(
        default=("black", "white"),
        description="Colors for the outline: border color and gap color.",
    )
    ncols: int = Field(
        default=4,
        description="Number of panels per row.",
    )
    hspace: float = Field(
        default=0.25,
        description="Height of the space between multiple panels.",
    )
    wspace: float | None = Field(
        default=None,
        description="Width of the space between multiple panels.",
    )
    return_fig: bool | None = Field(
        default=None,
        description="Return the matplotlib figure.",
    )
    show: bool | None = Field(
        default=None,
        description="Show the plot; do not return axis.",
    )
    save: str | bool | None = Field(
        default=None,
        description="If `True` or a `str`, save the figure.",
    )
    ax: Any | None = Field(
        default=None,
        description="A matplotlib axes object.",
    )
    # kwargs: dict[str, Any] | None = Field(
    #     default=None,
    #     description="Additional arguments passed to `matplotlib.pyplot.scatter()`.",
    # )
class ScPlHeatmap(ScanpyAPI):
    """Heatmap of the expression values of genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.heatmap",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    var_names: str | list[str] = Field(
        ...,
        description="List of var_names to use for the heatmap.",
    )
    groupby: str = Field(
        ...,
        description="Key for categorical observation/cell annotation for which densities are calculated per category.",
    )

class ScPlDotplot(ScanpyAPI):
    """Dot plot of the expression values of genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.dotplot",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    var_names: str | list[str] = Field(
        ...,
        description="List of var_names to use for the dot plot.",
    )
    groupby: str = Field(
        ...,
        description="Key for categorical observation/cell annotation for which densities are calculated per category.",
    )

class ScPlTracksplot(ScanpyAPI):
    """Compact plot of expression of a list of genes.

    In this type of plot each var_name is plotted as a filled line plot where the y values correspond to the var_name values and x is each of the cells. Best results are obtained when using raw counts that are not log-transformed.

    groupby is required to sort and order the values using the respective group and should be a categorical value."""

    _api_name: str = PrivateAttr(
        default="sc.pl.tracksplot",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    var_names: str | list[str] | Mapping[str, str | list[str]] = Field(
        ...,
        description="var_names should be a valid subset of adata.var_names. If var_names is a mapping, then the key is used as label to group the values (see var_group_labels). The mapping values should be sequences of valid adata.var_names. In this case either coloring or ‘brackets’ are used for the grouping of var names depending on the plot. When var_names is a mapping, then the var_group_labels and var_group_positions are set.",
    )
    groupby: str = Field(
        ...,
        description="The key of the observation grouping to consider.",
    )
    use_raw: bool | None = Field(
        None,
        description="Use raw attribute of adata if present.",
    )
    log: bool | None = Field(
        None,
        description="Plot on logarithmic axis.",
    )

class ScPlViolin(ScanpyAPI):
    """Violin plot of the expression values of genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.violin",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    keys: str | list[str] = Field(
        ...,
        description="Keys for accessing variables of .var_names or fields of .obs.",
    )
    groupby: str | None = Field(
        None,
        description="The key of the observation grouping to consider.",
    )

class ScPlDendrogram(ScanpyAPI):
    """Dendrogram of the expression values of genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.dendrogram",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    groupby: str = Field(
        ...,
        description="Key for categorical observation/cell annotation for which densities are calculated per category.",
    )

class ScPlDiffmap(ScanpyAPI):
    """Diffusion map of the expression values of genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.diffmap",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    color: str | list[str] | None = Field(
        None,
        description="Keys for annotations of observations/cells or variables/genes",
    )

class ScPlHighlyVariableGenes(ScanpyAPI):
    """Plot dispersions or normalized variance versus means for genes."""

    _api_name: str = PrivateAttr(
        default="sc.pl.highly_variable_genes",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )

class ScPlEmbeddingDensity(ScanpyAPI):
    """Plot the density of cells in an embedding (per condition)"""

    _api_name: str = PrivateAttr(
        default="sc.pl.embedding_density",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field( 
        "data",
        description="Annotated data matrix",
    )
    basis: str = Field(
        "umap",
        description="The embedding over which the density was calculated.",
    )
    key: str | None = Field(
        None,
        description="Name of the .obs covariate that contains the density estimates. Alternatively, pass groupby.",
    )
    groupby: str | None = Field(
        None,
        description="Name of the condition used in tl.embedding_density. Alternatively, pass key.",
    )

class ScPlRankGenesGroupsDotplot(ScanpyAPI):
    """Dot plot of the expression values of genes for characterising groups."""

    _api_name: str = PrivateAttr(
        default="sc.pl.rank_genes_groups_dotplot",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    groups: str | list[str] | None = Field(
        None,
        description="The groups for which to show the gene ranking.",
    )
    n_genes: int | None = Field(
        None,
        description="Number of genes to show in the dot plot.",
    )
    groupby: str | None = Field(
        None,
        description="The key of the observation grouping to consider. By default, the groupby is chosen from the rank genes groups parameter but other groupby options can be used. It is expected that groupby is a categorical. If groupby is not a categorical observation, it would be subdivided into num_categories (see dotplot()).",
    )

class ScPlHighestExprGenes(ScanpyAPI):
    """Fraction of counts assigned to each gene over all cells.

    Computes, for each gene, the fraction of counts assigned to that gene within
    a cell. The `n_top` genes with the highest mean fraction over all cells are
    plotted as boxplots.

    This plot is similar to the `scater` package function `plotHighestExprs(type
    = "highest-expression")`, see `here
    <https://bioconductor.org/packages/devel/bioc/vignettes/scater/inst/doc/vignette-qc.html>`__. Quoting
    from there:

        *We expect to see the “usual suspects”, i.e., mitochondrial genes, actin,
        ribosomal protein, MALAT1. A few spike-in transcripts may also be
        present here, though if all of the spike-ins are in the top 50, it
        suggests that too much spike-in RNA was added. A large number of
        pseudo-genes or predicted genes may indicate problems with alignment.*
        -- Davis McCarthy and Aaron Lun
    """

    _api_name: str = PrivateAttr(
        default="sc.pl.highest_expr_genes",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    n_top: int = Field(
        30,
        description="Number of genes to plot.",
    )
    layer: str | None = Field(
        None,
        description="Layer to use for the plot.",
    )
    gene_symbols: str | None = Field(
        None,
        description="Gene symbols to use for the plot.",
    )

class ScPlClusterMap(ScanpyAPI):
    """Hierarchically-clustered heatmap."""

    _api_name: str = PrivateAttr(
        default="sc.pl.clustermap",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    obs_keys: str | None = Field(
        None,
        description="Categorical annotation to plot with a different color map. Currently, only a single key is supported.",
    )
    use_raw: bool | None = Field(
        None,
        description="Whether to use raw attribute of adata. Defaults to True if .raw is present.",
    )
    
class ScPlStackedViolin(ScanpyAPI):
    """Stacked violin plots.

    Makes a compact image composed of individual violin plots (from violinplot()) stacked on top of each other. Useful to visualize gene expression per cluster.

    Wraps seaborn.violinplot() for AnnData.

    This function provides a convenient interface to the StackedViolin class. If you need more flexibility, you should use StackedViolin directly."""

    _api_name: str = PrivateAttr(
        default="sc.pl.stacked_violin",
    )
    _data_name: str = PrivateAttr(default='adata')
    adata: str = Field(
        "data",
        description="Annotated data matrix",
    )
    var_names: str | list[str] | Mapping[str, str | list[str]] = Field(
        ...,
        description="var_names should be a valid subset of adata.var_names. If var_names is a mapping, then the key is used as label to group the values (see var_group_labels). The mapping values should be sequences of valid adata.var_names. In this case either coloring or ‘brackets’ are used for the grouping of var names depending on the plot. When var_names is a mapping, then the var_group_labels and var_group_positions are set.",
    )
    groupby: str = Field(
        ...,
        description="The key of the observation grouping to consider.",
    )
    use_raw: bool | None = Field(
        None,
        description="Use raw attribute of adata if present.",
    )
    log: bool = Field(
        False,
        description="Plot on logarithmic axis.",
    )
    dendrogram: bool = Field(
        True,
        description="If True or a valid dendrogram key, a dendrogram based on the hierarchical clustering between the groupby categories is added. The dendrogram information is computed using scanpy.tl.dendrogram(). If tl.dendrogram has not been called previously the function is called with default parameters.",
    )
TOOLS = [
    ScPlScatter,
    ScPlPca,
    ScPlTsne,
    ScPlUmap,
    ScPlDrawGraph,
    ScPlSpatial,
    ScPlHeatmap,
    ScPlDotplot,
    ScPlTracksplot,
    ScPlViolin,
    ScPlDendrogram,
    ScPlDiffmap,
    ScPlHighlyVariableGenes,
    ScPlEmbeddingDensity,
    ScPlRankGenesGroupsDotplot,
    ScPlHighestExprGenes,
    ScPlClusterMap,
    ScPlStackedViolin,
]

TOOLS_DICT = {tool._api_name.default: tool for tool in TOOLS}