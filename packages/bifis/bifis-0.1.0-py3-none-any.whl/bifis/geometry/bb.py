"""
Axis-Aligned Bounding Box (AABB) module for the BiFIS framework.

This module provides functionality for creating and manipulating axis-aligned
bounding boxes, which are used for spatial queries, collision detection,
and region containment tests in computational geometry operations.
"""

# 📊 Data
import numpy as np


class AABB:
    """
    Axis-Aligned Bounding Box (AABB) representation.

    An AABB is a rectangular box whose faces are aligned with the coordinate axes,
    defined by its minimum and maximum points in each dimension.

    Parameters
    ----------
    points : numpy.ndarray
        Array of points with shape (n, d) where n is the number of points
        and d is the dimensionality (typically 2 or 3).

    Attributes
    ----------
    _min : numpy.ndarray
        Minimum coordinates of the bounding box in each dimension.
    _max : numpy.ndarray
        Maximum coordinates of the bounding box in each dimension.

    Examples
    --------
    >>> points = np.array([[0, 0, 0], [1, 2, 3], [-1, 5, 2]])
    >>> bbox = AABB(points)
    >>> bbox.min()
    array([-1,  0,  0])
    >>> bbox.max()
    array([1, 5, 3])
    >>> bbox.contains(np.array([0, 1, 1]))
    True
    >>> bbox.contains(np.array([2, 2, 2]))
    False
    """

    def __init__(self, points) -> None:
        """
        Initialize the bounding box from a set of points.

        Computes the minimum and maximum coordinates across all dimensions
        to define the bounding box corners.

        Parameters
        ----------
        points : numpy.ndarray
            Array of points with shape (n, d) where n is the number of points
            and d is the dimensionality (typically 2 or 3).
        """
        self._min = np.min(points, axis=0)
        self._max = np.max(points, axis=0)

    def contains(self, point):
        """
        Check if a point is inside the bounding box.

        A point is considered inside if it is greater than or equal to
        the minimum corner and less than or equal to the maximum corner
        in all dimensions.

        Parameters
        ----------
        point : numpy.ndarray
            Coordinates of the point to check with shape matching the
            dimensionality of the bounding box.

        Returns
        -------
        bool
            True if the point is inside the bounding box, False otherwise.
        """
        return np.all(self._min <= point) and np.all(point <= self._max)

    def min(self):
        """
        Get the minimum corner of the bounding box.

        Returns
        -------
        numpy.ndarray
            Minimum coordinates of the bounding box in each dimension.
        """
        return self._min

    def max(self):
        """
        Get the maximum corner of the bounding box.

        Returns
        -------
        numpy.ndarray
            Maximum coordinates of the bounding box in each dimension.
        """
        return self._max
