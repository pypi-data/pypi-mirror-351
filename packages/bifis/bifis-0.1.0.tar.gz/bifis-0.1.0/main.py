from bifis.utils import Config, RichArgumentParser, console
from bifis.sampling import Uniform, VariableDensity, BiFIS
import pathlib
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from scipy.interpolate import griddata
import numpy as np

parser = RichArgumentParser(
    "mlwind", description="Visualization script for OpenFOAM simulations."
)
parser.add_argument("-w", "--write", help="Write ouput to file.", action="store_true")
parser.add_argument(
    "-c",
    "--config",
    help="Path to JSON config file.",
    type=str,
    required=True,
)
parser.add_argument(
    "-r",
    "--resolution",
    help="Width and height of the output image.",
    type=int,
    nargs="*",
    default=[80, 40],
)
parser.add_argument(
    "-m", "--multiplier", help="Resolution multiplier.", type=int, default=4
)


def print_info(name, arr):
    console.print(name)
    console.print("Array Shape: {}".format(arr.shape))
    console.print("Min: {} Max: {} Avg: {}".format(arr.min(), arr.max(), arr.mean()))
    console.print("Sample: {}".format(arr[-1]))


def generate_2d_random_outside_deck(x_interval, y_interval, num_points, deck_path):
    """
    Generate random points within specified intervals but outside the deck.

    Parameters:
    -----------
    x_interval : tuple
        (min_x, max_x) range
    y_interval : tuple
        (min_y, max_y) range
    num_points : int
        Number of points to generate
    deck_path : matplotlib.path.Path
        Path defining the deck boundary

    Returns:
    --------
    numpy.ndarray
        Array of points outside the deck
    """
    # Generate more points than required to account for points that will be inside deck
    safety_factor = 1.5  # Generate extra points to ensure we have enough
    x_min, x_max = x_interval
    y_min, y_max = y_interval

    # Generate initial set of random points
    x_values = np.random.uniform(x_min, x_max, size=int(num_points * safety_factor))
    y_values = np.random.uniform(y_min, y_max, size=int(num_points * safety_factor))
    points = np.column_stack([x_values, y_values])

    # Check which points are outside the deck
    is_inside = deck_path.contains_points(points)
    points_outside = points[~is_inside]

    # If we got fewer points than requested, generate more until we have enough
    while len(points_outside) < num_points:
        # Generate additional points
        add_x = np.random.uniform(x_min, x_max, size=num_points - len(points_outside))
        add_y = np.random.uniform(y_min, y_max, size=num_points - len(points_outside))
        add_points = np.column_stack([add_x, add_y])

        # Filter again
        add_inside = deck_path.contains_points(add_points)
        add_outside = add_points[~add_inside]

        # Append to our collection of outside points
        points_outside = np.vstack([points_outside, add_outside])

    # Return exactly the requested number of points
    return points_outside[:num_points]


def generate_pressure_field(x, y, deck):
    """Generate a synthetic pressure field around an deck.

    Lower pressure above the deck, higher pressure below.
    """
    # Base pressure
    p = np.ones_like(x)

    # Find approximate center of deck
    center_x = np.mean(deck[:, 0])
    center_y = np.mean(deck[:, 1])

    # Distance from center
    dx = x - center_x
    dy = y - center_y
    r = np.sqrt(dx**2 + dy**2)

    # Angle relative to center (used to differentiate top/bottom)
    theta = np.arctan2(dy, dx)

    # Pressure decreases on top of deck, increases below
    # Effect diminishes with distance
    decay = np.exp(-5 * r)
    p -= 0.5 * decay * np.sin(theta)

    # Add some noise for realism
    p += 0.05 * np.random.randn(*x.shape) * decay

    return p


def build_toy_deck():
    """
    Create the deck using the original coordinates.

    Returns:
    --------
    tuple
        (points, deck, path) containing:
        - points: numpy array with the deck points
        - deck: reference to the same points (for compatibility)
        - path: matplotlib.path.Path object representing the deck
    """
    # Top
    points = np.column_stack([np.linspace(0.2, 0.8, 13), np.full((13), 0.7)])
    # Right middle wing point
    points = np.concatenate(
        [points, np.array([[0.8, 0.625]])],
        axis=0,
    )
    # Right wing
    points = np.concatenate(
        [points, np.column_stack([np.linspace(0.8, 0.7, 3), np.full((3), 0.55)])],
        axis=0,
    )
    # Right diagonal
    points = np.concatenate(
        [
            points,
            np.column_stack([np.linspace(0.7, 0.6, 5), np.linspace(0.55, 0.3, 5)]),
        ],
        axis=0,
    )
    # Bottom
    points = np.concatenate(
        [points, np.column_stack([np.linspace(0.6, 0.4, 5), np.full((5), 0.3)])], axis=0
    )
    # Left diagonal
    points = np.concatenate(
        [
            points,
            np.column_stack([np.linspace(0.4, 0.3, 5), np.linspace(0.3, 0.55, 5)]),
        ],
        axis=0,
    )
    # Left wing
    points = np.concatenate(
        [points, np.column_stack([np.linspace(0.3, 0.2, 3), np.full((3), 0.55)])],
        axis=0,
    )
    # Left middle wing points
    points = np.concatenate(
        [points, np.array([[0.2, 0.625]])],
        axis=0,
    )

    _, idx = np.unique(points, return_index=True, axis=0)
    points = points[np.sort(idx), :]

    deck_points = points

    codes = [Path.MOVETO] + [Path.LINETO] * (len(deck_points) - 2) + [Path.CLOSEPOLY]
    path = Path(deck_points, codes)

    return points, deck_points, path


def main(args):
    if args.write:
        pathlib.Path("figures").mkdir(parents=True, exist_ok=True)

    # Load configuration
    config = Config(args.config)

    # Build toy deck
    points, deck, path = build_toy_deck()

    # Close poly
    points = np.concatenate(
        [points, np.array([[0.2, 0.7]])],
        axis=0,
    )

    extra_points = int(args.resolution[0] * args.resolution[1] * 1.2)

    # Complement with random cells
    points = np.concatenate(
        [
            points,
            generate_2d_random_outside_deck(
                (config["domain"][0], config["domain"][1]),
                (config["domain"][2], config["domain"][3]),
                extra_points,
                path,
            ),
        ],
        axis=0,
    )

    print_info("Deck", deck)
    print_info("Points", points)

    # Deck polygon
    codes = [Path.MOVETO] + [Path.LINETO] * (len(deck) - 2) + [Path.CLOSEPOLY]
    path = Path(deck, codes)

    # Create sampling objects and show samples
    uniform = Uniform(
        config, args.resolution[0], args.resolution[1], np.arange(len(points))
    )
    uniform.show(points[:, 0], points[:, 1], write=False)

    variable_density = VariableDensity(
        config, args.resolution[0], args.resolution[1], np.arange(len(points))
    )
    variable_density.show(points[:, 0], points[:, 1], write=False)

    bifis = BiFIS(
        config,
        args.resolution[0],
        args.resolution[1],
        np.arange(len(points)),
        samples=points,
        surface=deck,
        surface_idx=np.arange(len(deck)),
    )
    bifis.show(points[:, 0], points[:, 1], write=False)

    # Generate CFD pressure field on the original points
    p_original = generate_pressure_field(points[:, 0], points[:, 1], deck)

    # Create figure with 2x2 subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Set up common visualization parameters
    aspect = "auto"
    cmap = "viridis"
    interpolation_method = "linear"

    # Create high-resolution grid for visualization
    xi_hi = np.linspace(
        config["domain"][0], config["domain"][1], args.resolution[0] * args.multiplier
    )
    yi_hi = np.linspace(
        config["domain"][2], config["domain"][3], args.resolution[1] * args.multiplier
    )

    grid_x_hi, grid_y_hi = np.meshgrid(xi_hi, yi_hi)

    # Native representations
    fields_c_i = griddata(
        (points[:, 0], points[:, 1]),
        p_original,
        (grid_x_hi, grid_y_hi),
        method=interpolation_method,
    )

    fields_i = griddata(
        (points[:, 0], points[:, 1]),
        p_original,
        (uniform.grid_x, uniform.grid_y),
        method=interpolation_method,
    )

    fields_vd_i = griddata(
        (points[:, 0], points[:, 1]),
        p_original,
        (variable_density.grid_x, variable_density.grid_y),
        method=interpolation_method,
    )

    # BiFIS uses idx instead of interpolation to get pixel data
    fields_b_i = p_original[bifis.idx].reshape(bifis.img_shape)

    fields = {
        "CFD": fields_c_i,
        "Uniform": fields_i,
        "Variable": fields_vd_i,
        "BiFIS": fields_b_i,
    }

    # Interpolated representations
    fields_u_u = griddata(
        (uniform.grid_x.ravel(), uniform.grid_y.ravel()),
        fields_i.ravel(),
        (grid_x_hi, grid_y_hi),
        method=interpolation_method,
    )

    fields_vd_u = griddata(
        (variable_density.grid_x.ravel(), variable_density.grid_y.ravel()),
        fields_vd_i.ravel(),
        (grid_x_hi, grid_y_hi),
        method=interpolation_method,
    )

    fields_bifis_u = griddata(
        (bifis.grid_x.ravel(), bifis.grid_y.ravel()),
        p_original[bifis.idx],
        (grid_x_hi, grid_y_hi),
        method=interpolation_method,
    )

    fields_i = {
        "CFD": fields_c_i,
        "Uniform": fields_u_u,
        "Variable": fields_vd_u,
        "BiFIS": fields_bifis_u,
    }

    # Plot titles and field names
    titles = ["CFD", "Uniform", "Variable-density", "BiFIS"]
    field_names = ["CFD", "Uniform", "Variable", "BiFIS"]

    # Create a set of extent values for proper positioning
    extent = [
        config["domain"][0],
        config["domain"][1],
        config["domain"][2],
        config["domain"][3],
    ]

    # Plot each field in its own subplot
    for i, (title, field_name) in enumerate(zip(titles, field_names)):
        row, col = i // 2, i % 2
        ax = axs[row, col]

        im = ax.imshow(
            fields[field_name],
            aspect=aspect,
            cmap=cmap,
            origin="lower",
            extent=extent,
            rasterized=True,
        )

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        ax.set_title(title)

        ax.set_xticks([])
        ax.set_yticks([])

        # Add deck outline
        if field_name in ["CFD", "Uniform"]:
            deck_patch = patches.PathPatch(
                path, facecolor="white", edgecolor="black", lw=1.5
            )
            ax.add_patch(deck_patch)

    if args.write:
        plt.savefig("figures/cfd_fields_visualization.svg")

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Plot each interpolated field in its own subplot
    for i, (title, field_name) in enumerate(zip(titles, field_names)):
        row, col = i // 2, i % 2
        ax = axs[row, col]

        im = ax.imshow(
            fields_i[field_name],
            aspect=aspect,
            cmap=cmap,
            origin="lower",
            extent=extent,
            rasterized=True,
        )

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        ax.set_title(title + " (Interpolated)")

        ax.set_xticks([])
        ax.set_yticks([])

        deck_patch = patches.PathPatch(
            path, facecolor="white", edgecolor="black", lw=1.5
        )
        ax.add_patch(deck_patch)

    if args.write:
        plt.savefig("figures/cfd_fields_visualization_interpolated.svg")
    else:
        plt.show()

    console.print("✅ Done...")


if __name__ == "__main__":
    main(parser.parse_args())
