import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

pd.set_option('future.no_silent_downcasting', True)

def get_venn(sets_dict, **kwargs):
    """
    Plot a 3-set Venn diagram (venn3) from a dictionary of exactly three sets,
    labeling each region with the actual elements belonging to that region.

    Args:
    sets_dict : dict
        A dictionary of the form:
            {
              "label1": set_of_items,
              "label2": set_of_items,
              "label3": set_of_items
            }
        Must contain exactly 3 key-value pairs.
    Kwargs:
        Width and Height of the figure.
    Returns:
        venn3 object
    """
    if len(sets_dict) != 3:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'Please select 3 foods\nCurrently selected: {len(sets_dict)}', 
                ha='center', va='center', fontsize=12, color='red')
        ax.axis('off')
        return fig

    labels = list(sets_dict.keys())
    sA, sB, sC = [set(sets_dict[lab]) for lab in labels]  # Ensure sets

    figsize = (
        kwargs.get('width', 800) / 100,  # Convert to inches
        kwargs.get('height', 400) / 100
    )

    fig, ax = plt.subplots(figsize=figsize)
    v = venn3([sA, sB, sC], set_labels=labels, ax=ax)

    def _set_region_text(region_id, elements):
        """Helper function to set the text for a given region of the Venn diagram."""
        label = v.get_label_by_id(region_id)
        if label is not None and elements:
            label.set_text("\n".join(sorted(elements)))
            label.set_fontsize(8)

    # Single-set regions
    _set_region_text('100', sA - sB - sC)
    _set_region_text('010', sB - sA - sC)
    _set_region_text('001', sC - sA - sB)

    # Two-set overlaps
    _set_region_text('110', (sA & sB) - sC)
    _set_region_text('101', (sA & sC) - sB)
    _set_region_text('011', (sB & sC) - sA)

    # Three-set overlap
    _set_region_text('111', sA & sB & sC)
    
    plt.title(f"Ingredients in: {', '.join(labels[:-1])}, & {labels[2]}", fontsize=10)
    plt.tight_layout()
    return fig

def get_scatter(df, x_col, y_col, color_col, prep_time_range=None, **kwargs):
    """
    Create an interactive scatter plot with hover functionality.

    Args:
        df : pandas.DataFrame
            The input dataframe containing the data to plot
        x_col : str
            Column name for x-axis
        y_col : str
            Column name for y-axis
        color_col : str
            Column name for color grouping
        prep_time_range : tuple, optional
            (min, max) range for filtering preparation time
    Kwargs:
        width : int
            Width of the plot in pixels
        height : int
            Height of the plot in pixels
    Returns:
        plotly.graph_objects.Figure
    """
    if prep_time_range:
        df = df[(df['prep_time'] >= prep_time_range[0]) & 
                (df['prep_time'] <= prep_time_range[1])]
    
    fig = px.scatter(df, 
                    x=x_col, 
                    y=y_col, 
                    color=color_col,
                    hover_data=['name', 'diet', 'region'],  # Show these on hover
                    title=f'{y_col.title()} vs {x_col.title()} by {color_col.title()}')
    
    fig.update_layout(
        width=kwargs.get('width', 800),
        height=kwargs.get('height', 400),
    )
    
    return fig

def get_heatmap(df, x_col, y_col, threshold=1, **kwargs):
    """
    Create a heatmap showing the distribution between two categorical variables.

    Args:
        df : pandas.DataFrame
            The input dataframe containing the data to plot
        x_col : str
            Column name for x-axis categories
        y_col : str
            Column name for y-axis categories
        threshold : int, optional
            Minimum count threshold for including cells
    Kwargs:
        width : int
            Width of the plot in pixels
        height : int
            Height of the plot in pixels
    Returns:
        plotly.graph_objects.Figure
    """
    heat_df = pd.crosstab(df[y_col],df[x_col])

    if threshold:
        heat_df = heat_df[heat_df >= threshold]
    
    fig = px.imshow(heat_df,
                    labels=dict(x=x_col.title(), 
                              y=y_col.title(), 
                              color="Count"),
                    title=f'Distribution of {y_col.title()} vs {x_col.title()}',
                    color_continuous_scale="sunsetdark")
    
    fig.update_layout(
        width=kwargs.get('width', 800),
        height=kwargs.get('height', 400),
    )
    
    
    return fig

def make_sankey(df, src, targ, vals=None, **kwargs):
    """
    Generate a Sankey diagram showing flows between source and target categories.

    Args:
        df : pandas.DataFrame
            The input dataframe containing flow data
        src : str
            Column name for source nodes
        targ : str
            Column name for target nodes
        vals : str, optional
            Column name for flow values
    Kwargs:
        width : int
            Width of the plot in pixels
        height : int
            Height of the plot in pixels
        pad : int
            Node padding
        thickness : int
            Link thickness
        line_color : str
            Node line color
        line_width : int
            Node line width
    Returns:
        plotly.graph_objects.Figure
    """
    if vals:
        values = df[vals]
    else:
        values = [1] * len(df[src])  # all 1

    df, labels = _code_mapping(df, src, targ)
    link = {'source': df[src], 'target': df[targ], 'value': values}

    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 50)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 1)

    node = {'label': labels, 'pad': pad, 'thickness': thickness, 'line': {'color': line_color, 'width': line_width}}
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    width = kwargs.get('width', 800)
    height = kwargs.get('height', 400)

    fig.update_layout(
        autosize=False,
        width=width,
        height=height
    )

    return fig

def _code_mapping(df, src, targ):
    """
    Map categorical labels to integer codes for Sankey diagram.

    Args:
        df : pandas.DataFrame
            The input dataframe containing the labels
        src : str
            Column name for source labels
        targ : str
            Column name for target labels
    Returns:
        tuple : (pandas.DataFrame, list)
            Modified dataframe with integer codes and list of original labels
    """
    # Get distinct labels
    labels = sorted(list(set(list(df[src]) + list(df[targ]))))

    # Get integer codes
    codes = list(range(len(labels)))

    # Create label to code mapping
    lc_map = dict(zip(labels, codes))

    # Substitute names for codes in dataframe
    df = df.replace({src: lc_map, targ: lc_map})
    return df, labels
