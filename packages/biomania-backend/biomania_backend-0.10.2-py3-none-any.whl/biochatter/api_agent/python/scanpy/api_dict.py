import scanpy as sc

pp_api_list = [
	{
		"api": sc.pp.neighbors,
		"products": [
			"data.uns[\"neighbors\"]",
			"data.obsp[\"distances\"]",
			"data.obsp[\"connectivities\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.pp.log1p,
		"products": [
			"data.X"
		],
		"data_name": "data"
	},
	{
		"api": sc.pp.highly_variable_genes,
		"products": [
			"data.var[\"highly_variable\"]",
			"data.var[\"means\"]",
			"data.var[\"dispersions\"]",
			"data.var[\"dispersions_norm\"]",
			"data.var[\"variances\"]",
			"data.var[\"variances_norm\"]",
			"data.var[\"highly_variable_rank\"]",
			"data.var[\"highly_variable_nbatches\"]",
			"data.var[\"highly_variable_intersection\"]"
		],
		"data_name": "adata",
		"_comment": "These products are curated from doc, from 'variances' to the end are actually non-existent.Products are not always fully generated, such as the current case.When testing dependencies, results would show non-existent dependencies. Although we already fixed this problem in dependency finder program,this is still a problematic software design making return values unclear and unfixed.We should encourage fixed api name, arguments and return values. In the meanwhile, returning an object is acceptable only if it is fixed. Note that we hope products can be automatically extracted from doc through LLM. If doc provides vague information products, then we believe it is poorly designed."
	},
	{
		"api": sc.pp.pca,
		"products": [
			"data.obsm[\"X_pca\"]",
			"data.varm[\"PCs\"]",
			"data.uns[\"pca\"][\"variance_ratio\"]",
			"data.uns[\"pca\"][\"variance\"]"
		],
		"data_name": "data"
	},
    # unfinished: how to deal with dynamic products?
    {
        "api": sc.pp.calculate_qc_metrics,
        "products": [
            "data.obs[\"total_genes_by_counts\"]",
            "data.obs[\"total_counts\"]",
            "data.obs[\"pct_counts_in_top_50_genes\"]",
            "data.obs[\"pct_counts_in_top_100_genes\"]",
            "data.obs[\"pct_counts_in_top_200_genes\"]",
        ],
        "data_name": "adata"
	},
    # unfinished: n_cells and n_genes are not guaranteed to be generated.
    # Jiahang: after all these noded being added, how to determine upstream dependencies?
    {
        "api": sc.pp.filter_cells,
        "products": [
			"data.X",
            "data.obs[\"n_counts\"]",
            "data.obs[\"n_genes\"]",
        ],
        "data_name": "data"
	},
    {
        "api": sc.pp.filter_genes,
        "products": [
			"data.X",
            "data.var[\"n_counts\"]",
            "data.var[\"n_genes\"]",
        ],
        "data_name": "data"
	},
    {
        "api": sc.pp.normalize_total,
        "products": [
            "data.X"
        ],
        "data_name": "adata"
    },
    # unfinished: how this api being used? doc is not clear.
    {
        "api": sc.pp.regress_out,
        "products": [
            "data.X"
        ],
        "data_name": "adata"
    },
    {
        "api": sc.pp.scale,
        "products": [
            "data.X",
            "data.var[\"mean\"]",
            "data.var[\"std\"]",
            "data.var[\"var\"]"
        ],
        "data_name": "data"
    },
    {
        "api": sc.pp.sample,
        "products": [
            "data.X"
        ],
        "data_name": "data"
	},
    {
        "api": sc.pp.downsample_counts,
        "products": [
            "data.X"
        ],
        "data_name": "adata"
    },
    {
        "api": sc.pp.recipe_zheng17,
        "_deprecated": True,
        "_comment": "recipe* API are not guaranteed to work."
    },
    # Jiahang: how this works?
    {
        "api": sc.pp.combat,
		"products": [
			"data.X"
		],
		"data_name": "adata"
    },
    # Jiahang: how to deal with multi-inputs?
    {
        "api": sc.pp.scrublet,
        "products": [
            "data.obs[\"doublet_score\"]",
            "data.obs[\"predicted_doublet\"]",
            "data.uns[\"scrublet\"][\"doublet_scores_sim\"]",
            "data.uns[\"scrublet\"][\"doublet_parents\"]",
            "data.uns[\"scrublet\"][\"parameters\"]",
        ],
        "data_name": "adata"
    },
    {
        "api": sc.pp.scrublet_simulate_doublets,
        "products": [
            "data.obsm[\"scrublet\"][\"doublet_parents\"]",
            "data.uns[\"scrublet\"][\"parameters\"]",
		],
        "data_name": "adata"
	}
]

tl_api_list = [
	{
		"api": sc.tl.paga,
		"products": [
			"data.uns[\"paga\"][\"connectivities\"]",
			"data.uns[\"paga\"][\"connectivities_tree\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.leiden,
		"products": [
			"data.obs[\"leiden\"]",
			"data.uns[\"leiden\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.louvain,
		"products": [
			"data.obs[\"louvain\"]",
			"data.uns[\"louvain\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.umap,
		"products": [
			"data.obsm[\"X_umap\"]",
			"data.uns[\"umap\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.tsne,
		"products": [
			"data.obsm[\"X_tsne\"]",
			"data.uns[\"tsne\"]"
		],  
		"data_name": "adata"
	},
	{
		"api": sc.tl.diffmap,
		"products": [
			"data.obsm[\"X_diffmap\"]",
			"data.uns[\"diffmap_evals\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.embedding_density,
		"products": [
			"data.obs[\"umap_density\"]",
			"data.uns[\"umap_density_params\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.tl.rank_genes_groups,
		"products": [
			"data.uns[\"rank_genes_groups\"]"
		],
		"data_name": "adata"
	},
    # Jiahang: this case is complex, leave it for now.
    {
        "api": sc.tl.ingest,
        "_deprecated": True,
	},
    {
        "api": sc.tl.filter_rank_genes_groups,
        "products": [
            "data.uns[\"rank_genes_groups\"]"
        ],
        "data_name": "adata"
	},
    {
        "api": sc.tl.marker_gene_overlap,
        "products": [
            "data.uns[\"marker_gene_overlap\"]"
        ],
        "data_name": "adata"
    },
    {
        "api": sc.tl.score_genes,
        "products": [
            "data.obs[\"score\"]"
        ],
        "data_name": "adata"
    },
    {
        "api": sc.tl.score_genes_cell_cycle,
        "products": [
            "data.obs[\"S_score\"]",
            "data.obs[\"G2M_score\"]",
            "data.obs[\"phase\"]"
        ],
        "data_name": "adata"
    },
    # Jiahang: special case, this API has no data argument.
    {
        "api": sc.tl.sim,
        "_deprecated": True,
	},
    # Jiahang: dynamic return values.
    {
        "api": sc.tl.draw_graph,
        "products": [
            "data.uns[\"draw_graph\"]",
            "data.obsm[\"X_draw_graph_fa\"]",
        ],
        "data_name": "adata"
    },
    {
        "api": sc.tl.dpt,
        "_deprecated": True,
        "_comment": "need preprocessing codes"
	}
]

pl_api_list = [
	{
		"api": sc.pl.paga,
		"products": [
			"data.uns[\"paga\"][\"pos\"]"
		],
		"data_name": "adata"
	},
	{
		"api": sc.pl.scatter,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.umap,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.tsne,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.heatmap,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.dotplot,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.violin,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.dendrogram,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.diffmap,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.highly_variable_genes,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.pca,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.embedding_density,
		"products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups,
        "products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.rank_genes_groups_dotplot,
		"products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups_violin,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups_heatmap,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups_stacked_violin,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups_matrixplot,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.rank_genes_groups_tracksplot,
        "products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.correlation_matrix,
		"products": [],
		"data_name": "adata",
		"_deprecated": True,
		"_comment": "Not found in doc."
	},
	{
		"api": sc.pl.highest_expr_genes,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.tracksplot,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.clustermap,
		"products": [],
		"data_name": "adata"
	},
	{
		"api": sc.pl.stacked_violin,
		"products": [],
		"data_name": "adata"
	},
    {
		"api": sc.pl.matrixplot,
		"products": [],
		"data_name": "adata"
	},
    {
		"api": sc.pl.ranking,
		"products": [],
		"data_name": "adata",
        "_deprecated": True,
        "_comment": "document is too poor"
	},
    {
        "api": sc.pl.filter_genes_dispersion,
        "_deprecated": True,
        "_comment": "description is too similar to sc.pp.highly_variable_genes"
	},
    {
        "api": sc.pl.filter_genes_dispersion,
        "_deprecated": True,
        "_comment": "description is too similar to sc.pp.highly_variable_genes"
	},
    {
        "api": sc.pl.scrublet_score_distribution,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.pca_loadings,
        "products": [],
		"data_name": "adata"
	},
    {
        "api": sc.pl.pca_variance_ratio,
        "_deprecated": True,
        "_comment": "document is too poor"
	},
    # Jiahang: poor doc
    {
        "api": sc.pl.draw_graph,
        "products": [],
        "data_name": "adata"
	},
    {
        "api": sc.pl.paga_path,
        "products": [],
        "data_name": "adata"
    },
	{
        "api": sc.pl.sim,
        "_deprecated": True,
        "_comment": "poor doc"
    },
]

pp = {
	"meta": {
		"package": sc,
		"module": sc.pp,
	},
	"api_list": pp_api_list
}

tl = {
	"meta": {
		"package": sc,
		"module": sc.tl,
	},
	"api_list": tl_api_list
}

pl = {
	"meta": {
		"package": sc,
		"module": sc.pl,
	},
	"api_list": pl_api_list
}