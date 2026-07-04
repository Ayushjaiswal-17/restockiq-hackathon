def build_substitution_graph(edges_df, gpu=True):
    """
    edges_df: columns [src_sku, dst_sku, weight] (co-purchase frequency)
    Returns a graph object + a function to get top substitutes for a SKU.
    """
    if gpu:
        import cudf
        import cugraph
        gdf = cudf.from_pandas(edges_df) if not hasattr(edges_df, "to_pandas") else edges_df
        G = cugraph.Graph()
        G.from_cudf_edgelist(gdf, source="src_sku", destination="dst_sku",
                              edge_attr="weight", renumber=True)
    else:
        import networkx as nx
        G = nx.from_pandas_edgelist(edges_df, "src_sku", "dst_sku", edge_attr="weight")
    return G

def get_top_substitutes(G, sku_id, edges_df, top_n=3):
    subset = edges_df[edges_df.src_sku == sku_id].sort_values("weight", ascending=False)
    return subset.head(top_n)["dst_sku"].tolist()