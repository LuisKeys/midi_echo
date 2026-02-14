"""Layout utilities for standardized GUI spacing and alignment."""


class LayoutSpacing:
    """Standardized spacing constants for consistent button and widget alignment."""

    # Padding for main grid buttons (button panels)
    MAIN_BUTTON_PADX = 10
    MAIN_BUTTON_PADY = 10

    # Padding for secondary buttons (tabs, controls)
    SECONDARY_BUTTON_PADX = 10
    SECONDARY_BUTTON_PADY = 10

    # Padding for small control buttons (+/- buttons, etc)
    CONTROL_BUTTON_PADX = 5
    CONTROL_BUTTON_PADY = 5

    # Padding for grid cells (pattern buttons, step buttons)
    GRID_CELL_PADX = 5
    GRID_CELL_PADY = 5

    # Padding for containers and frames
    CONTAINER_PADX = 10
    CONTAINER_PADY = 10

    # Padding for horizontal elements (label-button pairs)
    ELEMENT_PADX = 10
    ELEMENT_PADY = 0

    # Spacing between different sections
    SECTION_PADX = 10
    SECTION_PADY = 10

    # Label width for alignment
    LABEL_WIDTH = 150

    # Tight spacing for internal widget elements
    INTERNAL_PADX = 2
    INTERNAL_PADY = 2


def configure_button_grid(parent, rows: int, cols: int, uniform: bool = True) -> None:
    """Configure a grid with equal cell sizing for buttons.

    Args:
        parent: Parent widget (CTkFrame or CTk window)
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        uniform: If True, all cells will be equal size (recommended for button grids)
    """
    col_indices = tuple(range(cols))
    row_indices = tuple(range(rows))

    if uniform:
        parent.grid_columnconfigure(col_indices, weight=1, uniform="equal")
        parent.grid_rowconfigure(row_indices, weight=1, uniform="equal")
    else:
        parent.grid_columnconfigure(col_indices, weight=1)
        parent.grid_rowconfigure(row_indices, weight=1)
