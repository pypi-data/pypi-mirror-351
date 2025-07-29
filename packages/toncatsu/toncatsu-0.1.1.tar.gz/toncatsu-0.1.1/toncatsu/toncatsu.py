# -*- coding: utf-8 -*-
"""
Created on Wed May 28 10:09:05 2025

@author: hasada83d
"""

from .data_handler import Data
from .matcher_core import Toncatsu

def toncatsu(node_df, link_df, observation_df, output_dir, split_length=10):
    """
    Perform map-matching using GMNS-format node/link data and GPS observations.

    This function initializes a Data object, loads node, link, and observation data,
    performs coordinate transformation, constructs a network graph, applies the Toncatsu
    map-matching algorithm, and saves the results to the specified output directory.

    Parameters
    ----------
    node_df : pd.DataFrame
        DataFrame representing the nodes. Must contain:
        - 'node_id': Unique identifier for each node
        - 'x_coord': X coordinate (e.g., longitude)
        - 'y_coord': Y coordinate (e.g., latitude)

    link_df : gpd.GeoDataFrame
        GeoDataFrame representing the links. Must contain:
        - 'link_id': Unique identifier for each link
        - 'from_node_id': ID of source node
        - 'to_node_id': ID of target node
        - 'geometry': Shapely LineString geometry

    observation_df : pd.DataFrame
        DataFrame representing GPS observations. Must contain:
        - 'id': Observation ID
        - 'x_coord': X coordinate (longitude)
        - 'y_coord': Y coordinate (latitude)

    output_dir : str or Path
        Path to the directory where output files will be saved.

    split_length : float, optional
        The length (in meters) to segment long links for preprocessing.
        Default is 10.

    Returns
    -------
    data : Data
        The Data object used for processing, containing all intermediate and final results.
    """
    data = Data()
    data.read_node(node_df)
    data.read_link(link_df)
    data.read_observation(observation_df)
    data.reproject_crs() 
    data.create_graph()

    matcher = Toncatsu()
    matcher.set_data(data)
    matcher.fit(nearest_neighborhood="link", interpolate_onlink=True,split_length=split_length)
    
    data.save_output(outout_dir=output_dir)
    
    return data