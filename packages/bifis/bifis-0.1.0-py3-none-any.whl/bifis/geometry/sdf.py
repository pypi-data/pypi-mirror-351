"""
Signed Distance Field (SDF) module for the BiFIS framework.

This module provides functionality to compute distance fields between point clouds,
which is essential for geometry-aware sampling in computational fluid dynamics.
The SDF class efficiently computes distances from target points to the nearest
source points (typically surface geometry), normalizes these distances, and
optionally transforms them using a custom function.
"""

# 📊 Data
from scipy.spatial import KDTree


class SDF:
    """
    Signed Distance Field computation between point clouds.

    Calculates the distance from each target point to the nearest source point,
    typically representing distances from sample points to a surface geometry.
    Distances can be normalized, inverted, and transformed using custom functions.

    Attributes:
        source (ndarray): Source points, typically surface geometry
        target (ndarray): Target points to compute distances for
        invert (bool): If True, return (1 - normalized distances)
        max (float, optional): Custom maximum for distance normalization
        func (callable, optional): Custom function to transform distances
    """

    def __init__(self, source, target, invert=True, func=None, max=None) -> None:
        """
        Initialize the Signed Distance Field calculator.

        Args:
            source (ndarray): Source point cloud (e.g., surface geometry)
            target (ndarray): Target point cloud to compute distances for
            invert (bool, default=True): If True, return (1 - normalized distances)
            func (callable, optional): Custom function to transform distances
            max (float, optional): Custom maximum value for distance normalization
        """
        self.source = source
        self.target = target
        self.invert = invert
        self.max = max
        self.func = func

    def compute(self):
        """
        Compute the distance field from target points to source points.

        Uses KDTree for efficient nearest-neighbor queries to find the distance
        from each target point to the nearest source point. Distances are
        normalized and optionally transformed or inverted.

        Returns:
            ndarray: Normalized (and possibly inverted) distances
        """
        # Create a KD-tree from the point cloud for efficient
        # nearest neighbor queries. Only surface...
        mesh_tree = KDTree(self.source)

        # Query the nearest distance for each point in the grid...
        distances, _ = mesh_tree.query(self.target)

        # Normalize
        if self.max:
            distances /= self.max
        else:
            distances /= distances.max()

        if self.func:
            distances = self.func(distances)

        return 1.0 - distances if self.invert else distances
