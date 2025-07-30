from typing import List
from PIL import Image, ImageDraw
from PIL.Image import Image as ImageType
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
import os

def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))

def _calculate_text_size(text, font:FreeTypeFont):
    """
    Calculate the size of the text when rendered with the given font.
    Returns a tuple (width, height).
    """
    if not text:
        return (0, 0)
    # Create a dummy image to measure text size
    dummy_image = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    return draw.textbbox([0,0],text, font=font)

def create_git_commit_chart(
    data:List[int],
    tile_end_color="#56d364",
    tile_start_color="#033a16",
    background_color="#0d1117",
    tile_background_color="#151b23",
    tile_border_color="#ffffff1f",
    label_color="#ffffff",
    border_radius=5,
    tile_size=40,
    rows_per_column=7,
    inner_padding=15,
    outer_vertical_padding=75,
    outer_horizontal_padding=50,
    horizontal_labels:List[str]=[],
    vertical_labels:List[str]=[],
    horizontal_label_spacing_nth:None | int=None,
    vertical_label_spacing_nth:None | int=None,
    vertical_label_gap=20,
    horizontal_label_gap=20,
    label_font_size=50,
    label_font_file: None | str = None,
    skip: int = 0
) -> ImageType:
    """Create a Github contribution chart image.
    This function generates a contribution chart similar to the one seen on GitHub profiles.

    Args:
        data (List[int]): An array of integers
        tile_end_color (str, optional): The start range of the color for the tiles. Defaults to "#56d364".
        tile_start_color (str, optional): The end range of the color for the tiles. Defaults to "#033a16".
        background_color (str, optional): The background color of the image. Defaults to "#0d1117".
        tile_background_color (str, optional): The background color of the tile. Defaults to "#151b23".
        tile_border_color (str, optional): The border color of the tile. Defaults to "#ffffff1f".
        label_color (str, optional): The label color. Defaults to "#ffffff".
        border_radius (int, optional): Border radius of the tiles. Defaults to 5.
        tile_size (int, optional): The size of the tiles. Defaults to 40.
        rows_per_column (int, optional): Number of rows to split the data into. Defaults to 7.
        inner_padding (int, optional): The inner padding between tiles. Defaults to 15.
        outer_vertical_padding (int, optional): The outer vertical padding. Defaults to 75.
        outer_horizontal_padding (int, optional): The outer horizontal padding. Defaults to 50.
        horizontal_labels (List[str], optional): The horizontal labels to display. Will be spread evenly. Defaults to [].
        vertical_labels (List[str], optional): Vertical labels to display. Defaults to [].
        horizontal_label_spacing_nth (None | int, optional): The amount of tiles to gap between the horizontal labels.
        vertical_label_spacing_nth (None | int, optional): The amount of tiles to gap between the vertical labels. Defaults to None.
        vertical_label_gap (int, optional): The gap between the vertical label and the chart. Defaults to 20.
        horizontal_label_gap (int, optional): The gap between the horizontal label and the chart. Defaults to 20.
        label_font_size (int, optional): The font size. Defaults to 50.
        label_font_file (None | str, optional): The font file to use. Expects ttf. Defaults to Segoe UI.
        skip (int, optional): Number of tiles to offset at the start of the chart. Defaults to 0.

    Returns:
        ImageType: Image object containing the contribution chart.
    """

    if not label_font_file:
        label_font_file = f"{os.path.dirname(os.path.realpath(__file__))}/segoeuithis.ttf"

    with open(label_font_file, "rb") as font_file:
        font = ImageFont.truetype(font_file, label_font_size)


    # Calculate label sizes for padding
    font_height = _calculate_text_size("A", font)[3] - _calculate_text_size("A", font)[1]
    largest_vertical_label_width = max(
        _calculate_text_size(label, font)[2] for label in vertical_labels
    ) if vertical_labels else 0
    largest_horizontal_label_height = max(
        _calculate_text_size(label, font)[3] - _calculate_text_size(label, font)[1] for label in horizontal_labels
    ) if horizontal_labels else 0

    # Calculate the number of columns needed
    size = len(data) + skip
    num_columns = (size + rows_per_column - 1) // rows_per_column

    # Calculate total inner gap
    total_horizontal_inner_gap = inner_padding * (num_columns - 1)
    total_vertical_inner_gap = inner_padding * (rows_per_column - 1)

    # Calculate total width and height of the chart
    total_width = (
        num_columns * tile_size
        + total_horizontal_inner_gap
        + 2 * outer_horizontal_padding
        + largest_vertical_label_width
        + vertical_label_gap
    )

    total_height = (
        rows_per_column * tile_size
        + total_vertical_inner_gap
        + 2 * outer_vertical_padding
        + largest_horizontal_label_height
        + horizontal_label_gap
    )

    # Calculate label spacings if not provided
    if not horizontal_label_spacing_nth:
        horizontal_label_spacing_nth = num_columns  // len(horizontal_labels) + 1

    if not vertical_label_spacing_nth:
        vertical_label_spacing_nth = rows_per_column // len(vertical_labels) + 1

    # Create a new image with the specified background color
    image = Image.new("RGBA", (total_width, total_height), background_color)
    tile_layer = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    tile_draw = ImageDraw.Draw(tile_layer)

    # Draw the background tiles and 
    # blend it with the image
    
    for i in range(size):
        if i < skip:
            continue
        row = i % rows_per_column
        column = i // rows_per_column
        x = (
            outer_horizontal_padding
            + largest_vertical_label_width
            + vertical_label_gap
            + column * (tile_size + inner_padding)
        )
        y = (
            outer_vertical_padding
            + largest_horizontal_label_height
            + horizontal_label_gap
            + row * (tile_size + inner_padding)
        )
        tile_draw.rounded_rectangle(
            [x, y, x + tile_size, y + tile_size],
            fill=tile_background_color,
            outline=tile_border_color,
            width=1,
            radius=border_radius
        )
    image = Image.alpha_composite(image, tile_layer)

    # Normalize the data to fit within the range of 0 to 1
    max_value = max(data) if data else 1 
    normalized_data = [min(value / max_value, 1) for value in data]

    # New layer for the actual data,
    # Draw the data tiles with colors based on normalized values
    # and blend it with the image
    data_layer = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    data_draw = ImageDraw.Draw(data_layer)
    for i in range(len(normalized_data) + skip):
        if i < skip: continue
        value = normalized_data[i - skip]
        row = i % rows_per_column
        column = i // rows_per_column
        x = (
            outer_horizontal_padding
            + largest_vertical_label_width
            + vertical_label_gap
            + column * (tile_size + inner_padding)
        )
        y = (
            outer_vertical_padding
            + largest_horizontal_label_height
            + horizontal_label_gap
            + row * (tile_size + inner_padding)
        )

        # Interpolate the color based on the normalized value
        start_rgb = _hex_to_rgb(tile_start_color)
        end_rgb = _hex_to_rgb(tile_end_color)
        interp_rgb = tuple(
            int(start + (end - start) * value)
            for start, end in zip(start_rgb, end_rgb)
        )
        alpha = int(value * (255)) 
        color = (*interp_rgb, alpha)

        data_draw.rounded_rectangle(
            [x, y, x + tile_size, y + tile_size],
            fill=color,
            outline=tile_border_color,
            width=1,
            radius=border_radius
        )
    image = Image.alpha_composite(image, data_layer)

    # Create a new layer for labels
    label_layer = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    label_draw = ImageDraw.Draw(label_layer)

    # Draw the horizontal labels at the top of the chart
    if horizontal_labels:
        for label_idx, col in enumerate(range(0, num_columns, horizontal_label_spacing_nth)):
            if label_idx >= len(horizontal_labels):
                break
            x = (
                outer_horizontal_padding
                + largest_vertical_label_width
                + vertical_label_gap
                + col * (tile_size + inner_padding)
            )
            y = outer_vertical_padding + (font_height / 2) - horizontal_label_gap
            label_draw.text(
                (x, y),
                horizontal_labels[label_idx],
                font=font,
                fill=label_color,
                anchor="lm"
            )

    # Draw the vertical labels on the left side of the chart
    if vertical_labels:
        for label_idx, row in enumerate(range(0, rows_per_column, vertical_label_spacing_nth or 1)):
            if label_idx >= len(vertical_labels):
                break

            x = outer_horizontal_padding - vertical_label_gap 
            y = (
                outer_vertical_padding
                + (font_height / 2)
                + (largest_horizontal_label_height + horizontal_label_gap)
                + row * (tile_size + inner_padding)
            )
            label_draw.text(
                (x, y),
                vertical_labels[label_idx],
                font=font,
                fill=label_color,
                anchor="lm"
            )
    image = Image.alpha_composite(image, label_layer)
    return image