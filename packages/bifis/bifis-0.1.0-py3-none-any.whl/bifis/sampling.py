"""
Sampling module for the BiFIS framework.

This module implements various grid sampling approaches for computational fluid dynamics (CFD)
field reconstruction. It provides:
- Base grid sampling functionality
- Uniform grid sampling
- Variable-density grid sampling
- SDF-SDF-biased Field Importance Sampling (BiFIS)

The classes handle grid generation, point selection, and interpolation for different
sampling strategies, enabling efficient representation of complex flow fields.
"""

from .utils import rng, console
from .geometry.sdf import SDF
from .geometry.bb import AABB

# 📊 Data
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt


class ROI:
    """
    Region of Interest definition for focused sampling.

    Defines a rectangular region where sampling density may be increased.

    Attributes:
        xmin (float): Minimum x-coordinate of ROI
        xmax (float): Maximum x-coordinate of ROI
        ymin (float): Minimum y-coordinate of ROI
        ymax (float): Maximum y-coordinate of ROI
    """

    def __init__(self, config) -> None:
        """
        Initialize ROI from configuration.

        Args:
            config: Configuration object with 'roi' parameter
        """
        self.xmin, self.xmax, self.ymin, self.ymax = config["roi"]


class ROICounts:
    """
    Point counts for Region of Interest sampling.

    Defines how many points to sample in each region division.

    Attributes:
        xcounts (list): Point counts for x-axis regions [left, center, right]
        ycounts (list): Point counts for y-axis regions [bottom, middle, top]
    """

    def __init__(self, config) -> None:
        """
        Initialize ROI counts from configuration.

        Args:
            config: Configuration object with 'counts' parameter
        """
        self.xcounts, self.ycounts = config["counts"]


class Grid:
    """
    Base grid sampling class.

    Provides common functionality for different grid sampling approaches.

    Attributes:
        config: Configuration parameters
        width (int): Grid width in pixels
        height (int): Grid height in pixels
        s (int): Point size for visualization
        xinterpmin (float): Minimum x-coordinate of interpolation domain
        xinterpmax (float): Maximum x-coordinate of interpolation domain
        yinterpmin (float): Minimum y-coordinate of interpolation domain
        yinterpmax (float): Maximum y-coordinate of interpolation domain
        idx: Sample indices
        roi (ROI): Region of Interest
        counts (ROICounts): Point counts for ROI
        grid_points (ndarray): Array of grid points
        x, y, xy (ndarray): Grid indices
        img_shape (tuple): Grid dimensions as (height, width)
        img_x, img_y (ndarray): Grid coordinate arrays
        grid_x, grid_y (ndarray): Coordinate arrays for the sampling grid
    """

    def __init__(self, config, width, height, idx, *args, **kwargs) -> None:
        """
        Initialize the grid sampling.

        Args:
            config: Configuration object
            width (int): Grid width in pixels
            height (int): Grid height in pixels
            idx: Sample indices
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.config = config
        self.width = width
        self.height = height
        self.s = 10

        # Interpolation grid dimensions
        self.xinterpmin = self.config["domain"][0]
        self.xinterpmax = self.config["domain"][1]
        self.yinterpmin = self.config["domain"][2]
        self.yinterpmax = self.config["domain"][3]

        self.idx = idx

        self.roi = ROI(self.config)
        self.counts = ROICounts(self.config)

        console.print(f"🏁 Computing {self} grid...")

        self._init_bias()
        self._get_img_grid()
        self._get_coord_grid()
        self._set_grid()

    def __str__(self) -> str:
        """
        Get string representation of this grid class.

        Returns:
            str: Class name
        """
        return self.__class__.__name__

    def _init_bias(self) -> None:
        """
        Initialize bias for sampling.

        Placeholder method to be implemented by subclasses.
        """
        pass

    def _get_and_filter_geometry(self) -> None:
        """
        Get and filter geometry for sampling.

        Placeholder method to be implemented by subclasses.
        """
        pass

    def _get_coord_grid(self) -> None:
        """
        Generate coordinate grid.

        Placeholder method to be implemented by subclasses.
        """
        pass

    def _set_grid(self) -> None:
        """
        Set grid points by combining coordinate arrays.

        Creates 3D grid points from 2D grid coordinates.
        """
        # 2D for now
        self.grid_points = np.column_stack(
            [
                self.grid_x.ravel(),
                self.grid_y.ravel(),
                np.zeros_like(self.grid_x.ravel()),
            ]
        )

    def _get_img_grid(self) -> None:
        """
        Generate image grid coordinates.

        Creates 1D and 2D arrays for image grid coordinates.
        """
        # Image grid
        self.x = np.arange(self.width)
        self.y = np.arange(self.height)
        self.xy = np.arange(self.width * self.height)
        self.img_shape = (self.height, self.width)

        self.img_x, self.img_y = np.meshgrid(self.x, self.y)

        # NOTE Not sure if I used this anywhere else and it should not
        # be flattened
        self.img_x = self.img_x.flatten()
        self.img_y = self.img_y.flatten()

    def get_closest_samples(self, samples, scanline, full_dimensions=False):
        """
        Get closest samples to a scanline.

        Uses KDTree to efficiently find nearest samples to specified points.

        Args:
            samples (ndarray): Sample points
            scanline (ndarray): Points defining the scanline
            full_dimensions (bool): If True, use full dimensions for KDTree

        Returns:
            tuple: (sort_idx, s_samples)
                - sort_idx: Indices of selected samples
                - s_samples: Selected and sorted samples
        """
        # Init KDTree with remaining samples
        tree = KDTree(samples[:, :2] if full_dimensions else samples[:, 1:])

        # Query closest neighbors (overshoot k so we don't have less than width)
        distances, idx = tree.query(scanline, k=self.width)

        # Flatten array using scanline and keeping order in point results
        # 1st k=1 for all points, then k=2...
        query = np.column_stack([idx.flatten(order="F"), distances.flatten(order="F")])

        # Obtain unique neighbors
        query = query[np.unique(query[:, 0].astype(int), return_index=True)[1], :]

        # Sort them by distance and get ids, limit to image width
        sort_idx = query[np.argsort(query[:, 1]), 0].astype(int)[: self.width]
        s_samples = samples[sort_idx]

        # Sort x axis to get left to right, like an image
        s_idx = np.argsort(s_samples[:, 1])

        return sort_idx, s_samples[s_idx]

    def process_scanline(self, samples, cls_cx, grid_idx, grid_x, grid_y, i):
        """
        Process a single scanline and fill corresponding grid row.

        Args:
            samples (ndarray): Sample points
            cls_cx (ndarray): X-coordinates for the scanline
            grid_idx (ndarray): Grid indices to fill
            grid_x (ndarray): Grid x-coordinates to fill
            grid_y (ndarray): Grid y-coordinates to fill
            i (int): Row index

        Returns:
            ndarray: Remaining samples after removing used ones
        """
        # Obtain minimum y in data BB
        min_y = AABB(samples).min()[2]

        # Obtain scanline points for min y
        scanline = np.column_stack([cls_cx, np.full_like(cls_cx, min_y)])

        sort_idx, s_samples = self.get_closest_samples(samples, scanline)

        # Check that we have enough to fill a row
        assert s_samples.shape[0] == self.width

        # Fill grid
        grid_idx[i, self.x] = s_samples[self.x, 0]
        grid_x[i, self.x] = s_samples[self.x, 1]
        grid_y[i, self.x] = s_samples[self.x, 2]

        return np.delete(samples, sort_idx, axis=0)

    def process_scanlines(self, samples):
        """
        Process all scanlines to fill the entire grid.

        Args:
            samples (ndarray): Sample points

        Returns:
            tuple: (grid_idx, grid_x, grid_y) arrays
                - grid_idx: Grid indices
                - grid_x: Grid x-coordinates
                - grid_y: Grid y-coordinates
        """
        # Obtain x scanline
        cls_cx = np.linspace(samples[:, 1].min(), samples[:, 1].max(), self.width)

        i = 0
        grid_x = np.zeros((self.height, self.width))
        grid_y = np.zeros((self.height, self.width))
        grid_idx = np.zeros((self.height, self.width))

        while samples.shape[0] > 0:
            samples = self.process_scanline(
                samples, cls_cx, grid_idx, grid_x, grid_y, i
            )

            i += 1

        return grid_idx.ravel().astype(int), grid_x, grid_y

    def update(self, mesh):
        """
        Update grid with new mesh data.

        Args:
            mesh: Mesh data for updating the grid
        """
        self.mesh = mesh
        # self._get_and_filter_geometry()
        self._get_coord_grid()
        self._set_grid()

    def show(self, cx, cy, write) -> None:
        """
        Visualize the grid and original points.

        Args:
            cx (ndarray): X-coordinates of original points
            cy (ndarray): Y-coordinates of original points
            write (bool): If True, save visualization to file
        """
        fig1 = plt.figure()
        plt.scatter(cx, cy, self.s, c="tab:blue", label="Original samples")
        plt.scatter(
            self.grid_points[:, 0],
            self.grid_points[:, 1],
            self.s,
            c="r",
            label="Grid samples",
        )

        plt.xlim(self.xinterpmin, self.xinterpmax)
        plt.ylim(self.yinterpmin, self.yinterpmax)
        plt.gca().set_axis_off()
        plt.title(self)
        plt.legend(loc="upper right")

        if write:
            fig1.savefig("figures/flow_sdf.svg", transparent=True)


class Uniform(Grid):
    """
    Uniform grid sampling.

    Creates a regular grid with equal spacing in both dimensions.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize uniform grid sampling.

        Args:
            *args: Arguments passed to Grid.__init__
            **kwargs: Keyword arguments passed to Grid.__init__
        """
        super().__init__(*args, **kwargs)

    def update(self, mesh):
        """
        Update method (no-op for Uniform grid).

        Args:
            mesh: Ignored for Uniform grid
        """
        pass

    def _get_coord_grid(self) -> None:
        """
        Generate uniform coordinate grid.

        Creates evenly spaced grid in both dimensions.
        """
        # Interpolation grid
        self.xi = np.linspace(self.xinterpmin, self.xinterpmax, self.width)
        self.yi = np.linspace(self.yinterpmin, self.yinterpmax, self.height)

        # Structured grid creation
        self.grid_x, self.grid_y = np.meshgrid(self.xi, self.yi)


class VariableDensity(Grid):
    """
    Variable-density grid sampling.

    Creates a grid with higher point density in the Region of Interest.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize variable-density grid sampling.

        Args:
            *args: Arguments passed to Grid.__init__
            **kwargs: Keyword arguments passed to Grid.__init__
        """
        super().__init__(*args, **kwargs)

    def update(self, mesh):
        """
        Update method (no-op for Variable-density grid).

        Args:
            mesh: Ignored for Variable-density grid
        """
        pass

    def _get_coord_grid(self) -> None:
        """
        Generate variable-density coordinate grid.

        Creates grid with higher point density in ROI.
        """
        # Interpolation grid
        self.xi = np.concatenate(
            [
                np.linspace(self.xinterpmin, self.roi.xmin, self.counts.xcounts[0]),
                np.linspace(self.roi.xmin, self.roi.xmax, self.counts.xcounts[1]),
                np.linspace(self.roi.xmax, self.xinterpmax, self.counts.xcounts[2]),
            ]
        )
        self.yi = np.concatenate(
            [
                np.linspace(self.yinterpmin, self.roi.ymin, self.counts.ycounts[0]),
                np.linspace(self.roi.ymin, self.roi.ymax, self.counts.ycounts[1]),
                np.linspace(self.roi.ymax, self.yinterpmax, self.counts.ycounts[2]),
            ]
        )

        # Structured grid creation
        self.grid_x, self.grid_y = np.meshgrid(self.xi, self.yi)


class BiFIS(Grid):
    """
    SDF-biased Field Importance Sampling (BiFIS) grid.

    Creates an adaptive grid by sampling points based on distance to surface geometry.
    Points closer to the surface are sampled with higher probability.

    Attributes:
        surface (ndarray): Surface geometry points
        surface_idx (ndarray): Surface point indices
        samples (ndarray): Sample points
        func (callable, optional): Custom function for SDF calculation
        sdf (SDF): Signed distance field object
        full (ndarray): Complete set of sample points
    """

    def __init__(
        self, *args, samples=None, surface=None, surface_idx=None, func=None, **kwargs
    ) -> None:
        """
        Initialize BiFIS grid sampling.

        Args:
            *args: Arguments passed to Grid.__init__
            samples (ndarray, optional): Sample points
            surface (ndarray, optional): Surface geometry points
            surface_idx (ndarray, optional): Surface point indices
            func (callable, optional): Custom function for SDF calculation
            **kwargs: Keyword arguments passed to Grid.__init__
        """
        self.surface = surface
        self.surface_idx = surface_idx
        self.samples = samples
        self.func = func

        super().__init__(*args, **kwargs)

    def _init_bias(self):
        """
        Initialize bias for BiFIS sampling.

        Sets up geometry and signed distance field.
        """
        self._get_and_filter_geometry()

        self.sdf = SDF(
            self.surface[:, 1:4],
            self.full[:, 1:4],
            func=self.func,
        )

    def _get_and_filter_geometry(self) -> None:
        """
        Prepare and filter geometry for sampling.

        Combines sample and surface points, and filters out points outside the domain.
        """
        self.full = np.column_stack([self.idx, self.samples])
        self.surface = np.column_stack([self.surface_idx, self.surface])

        # Filter points outside of ROI
        mask = (
            (self.full[:, 1] >= self.xinterpmin)
            & (self.full[:, 1] <= self.xinterpmax)
            & (self.full[:, 2] >= self.yinterpmin)
            & (self.full[:, 2] <= self.yinterpmax)
        )
        self.full = self.full[mask]

    def _get_coord_grid(self) -> None:
        """
        Generate coordinate grid using importance sampling.

        Selects points based on signed distance field values, with
        more points near the surface geometry.
        """
        distances = self.sdf.compute()

        if self.config["preserve_surface"]:
            samples = self.surface
            del_idx = np.nonzero(np.isin(self.full[:, 0], samples[:, 0]))[0]

            distances = self.sdf.compute()

            self.full = np.delete(self.full, del_idx, axis=0)
            distances = np.delete(distances, del_idx, axis=0)

            # p must sum to 1 when cast to float64...
            p = distances / np.sum(distances, dtype=float)

            # NOTE For now you cannot ask for more samples than self.full
            r_samples = rng.choice(
                self.full,
                (self.width * self.height) - samples.shape[0],
                replace=False,
                p=p,
            )

            samples = np.concatenate([samples, r_samples])

            self.idx, self.grid_x, self.grid_y = self.process_scanlines(samples[:, :3])
        else:
            # p must sum to 1 when cast to float64. Normalize.
            p = distances / np.sum(distances, dtype=float)

            samples = rng.choice(
                self.full, self.width * self.height, replace=False, p=p
            )

            self.idx, self.grid_x, self.grid_y = self.process_scanlines(samples[:, :3])
