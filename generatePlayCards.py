import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import qrcode
from qrcode.image.styledpil import StyledPilImage
import hashlib
import argparse
import textwrap
import os
import requests
from io import BytesIO


def generate_qr_code(url, file_path, icon_path, icon_image_cache={}):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    if icon_path is None:
        img = qr.make_image(fill_color="black", back_color="white")
    else:
        if icon_path.startswith('http'):
            if icon_path not in icon_image_cache:
                response = requests.get(icon_path)
                icon_image_cache[icon_path] = BytesIO(response.content)
            icon_image = icon_image_cache[icon_path]
            img = qr.make_image(image_factory=StyledPilImage, embeded_image_path=icon_image)
        else:
            img = qr.make_image(image_factory=StyledPilImage, embeded_image_path=icon_path)
    img.save(file_path)


def add_qr_code_with_border(c, url, position, box_size, icon_path):
    hash_object = hashlib.sha256(url.encode())
    hex_dig = hash_object.hexdigest()

    qr_code_path = f"qr_{hex_dig}.png"  # Unique path for each QR code
    generate_qr_code(url, qr_code_path, icon_path)
    x, y = position
    c.drawImage(qr_code_path, x, y, width=box_size, height=box_size)
    os.remove(qr_code_path)


def draw_wrapped_text_in_box(
    c,
    text,
    font_name,
    start_font_size,
    min_font_size,
    box_width,
    box_height,
    x_left,
    y_top,
    line_spacing=1.0,
    center_horizontally=True,
    margin_top=0,
):
    """
    Renders multi-line `text` within a region (width=box_width, height=box_height),
    starting from y_top downward. It tries decreasing font sizes from `start_font_size`
    down to `min_font_size` until it fits.
    """
    if not text or pd.isna(text):
        return

    text = str(text).strip()
    if not text:
        return

    # We'll attempt from start_font_size down to min_font_size
    from textwrap import wrap

    for font_size in range(start_font_size, min_font_size - 1, -1):
        c.setFont(font_name, font_size)
        # Measure width of 'M' to guess line wrap length
        if c.stringWidth("M", font_name, font_size) == 0:
            continue
        approx_chars_per_line = int(box_width / c.stringWidth("M", font_name, font_size))
        if approx_chars_per_line < 1:
            approx_chars_per_line = 1

        # Try word-wrapping
        candidate_lines = wrap(text, width=approx_chars_per_line)
        wrapped_lines = []
        for line in candidate_lines:
            actual_width = c.stringWidth(line, font_name, font_size)
            # If the line is too wide, we manually clip it down
            while actual_width > box_width and len(line) > 1:
                line = line[:-1]
                actual_width = c.stringWidth(line, font_name, font_size)
            wrapped_lines.append(line)

        # Determine total height needed
        line_height = font_size * line_spacing
        needed_height = len(wrapped_lines) * line_height

        if needed_height <= box_height:
            # We can fit at this font size -> draw the lines
            c.setFillColorRGB(0, 0, 0)
            current_y = y_top
            for wrapped_line in wrapped_lines:
                line_width = c.stringWidth(wrapped_line, font_name, font_size)
                if center_horizontally:
                    x_text = x_left + (box_width - line_width) / 2
                else:
                    x_text = x_left
                c.drawString(x_text, current_y, wrapped_line)
                current_y -= line_height
            return

    # If even min_font_size doesn't fit all lines, draw anyway in min_font_size,
    # potentially truncating lines or some lines not fitting.
    c.setFont(font_name, min_font_size)
    approx_chars_per_line = int(box_width / c.stringWidth("M", font_name, min_font_size))
    approx_chars_per_line = max(approx_chars_per_line, 1)
    candidate_lines = textwrap.wrap(text, width=approx_chars_per_line)
    wrapped_lines = []
    for line in candidate_lines:
        actual_width = c.stringWidth(line, font_name, min_font_size)
        while actual_width > box_width and len(line) > 1:
            line = line[:-1]
            actual_width = c.stringWidth(line, font_name, min_font_size)
        wrapped_lines.append(line)

    line_height = min_font_size * line_spacing
    current_y = y_top
    for wrapped_line in wrapped_lines:
        line_width = c.stringWidth(wrapped_line, font_name, min_font_size)
        if center_horizontally:
            x_text = x_left + (box_width - line_width) / 2
        else:
            x_text = x_left
        c.drawString(x_text, current_y, wrapped_line)
        current_y -= line_height


def draw_centered_single_line(
    c,
    text,
    font_name,
    max_font_size,
    min_font_size,
    region_width,
    region_height,
    x_left,
    y_bottom
):
    """
    For the 'Year' text (or any single line),
    tries from `max_font_size` down to `min_font_size`.
    Once it fits horizontally and vertically, we place it in the vertical center.
    """
    if not text or pd.isna(text):
        return

    text = str(text).strip()
    if not text:
        return

    for size in range(max_font_size, min_font_size - 1, -1):
        text_width = c.stringWidth(text, font_name, size)
        text_height = size  # Single line
        if text_width <= region_width and text_height <= region_height:
            # We'll draw it here
            c.setFont(font_name, size)
            c.setFillColorRGB(0, 0, 0)
            # Center horizontally
            x_text = x_left + (region_width - text_width) / 2
            # Center vertically
            y_text = y_bottom + (region_height - text_height) / 2
            c.drawString(x_text, y_text, text)
            return

    # If it didn't fit at all, use min_font_size anyway
    c.setFont(font_name, min_font_size)
    text_width = c.stringWidth(text, font_name, min_font_size)
    text_height = min_font_size
    x_text = x_left + (region_width - text_width) / 2
    y_text = y_bottom + (region_height - text_height) / 2
    c.drawString(x_text, y_text, text)


def add_text_box(c, info, position, box_size):
    """
    Draws a thicker border and splits the box into three regions:
      Artist: top 40%
      Year:   middle 20%
      Title:  bottom 40%
    """
    x, y = position

    # Thicker border
    c.setLineWidth(3)
    c.rect(x, y, box_size, box_size)

    # Proportions
    artist_box_height = 0.40 * box_size
    year_box_height   = 0.20 * box_size
    title_box_height  = 0.40 * box_size

    margin = 3  # px from each border
    margin_top = 20

    # -----------------------
    #  Artist region (top)
    # -----------------------
    artist_top = y + box_size  # very top
    artist_bottom = artist_top - artist_box_height
    artist_region_height = artist_box_height - 2 * margin
    artist_region_top = artist_top - margin_top
    # left & width for the artist text
    artist_x_left = x + margin
    artist_box_width = box_size - 2 * margin

    draw_wrapped_text_in_box(
        c,
        text=info.get('Artist', ''),
        font_name="Helvetica-Bold",
        start_font_size=16,
        min_font_size=6,
        box_width=artist_box_width,
        box_height=artist_region_height,
        x_left=artist_x_left,
        y_top=artist_region_top,
        line_spacing=1.1,
        center_horizontally=True,
    )

    # -----------------------
    #  Year region (middle)
    # -----------------------
    year_top = artist_bottom  # below artist region
    year_bottom = year_top - year_box_height
    # The region we can draw in:
    year_region_width = box_size - 2 * margin
    year_region_height = year_box_height - 2 * margin
    year_x_left = x + margin
    year_y_bottom = year_bottom + margin
  
    year_text = info.get('Year', '')
    year_text = str(year_text).split('-')[0]

    draw_centered_single_line(
        c,
        text=year_text,
        font_name="Helvetica-Bold",
        max_font_size=50,
        min_font_size=8,
        region_width=year_region_width,
        region_height=year_region_height,
        x_left=year_x_left,
        y_bottom=year_y_bottom
    )

    # -----------------------
    #  Title region (bottom)
    # -----------------------
    title_top = year_bottom  # below year region
    title_bottom = y
    title_region_height = title_box_height - 2 * margin
    title_region_top = title_top - margin_top
    title_x_left = x + margin
    title_box_width = box_size - 2 * margin


    draw_wrapped_text_in_box(
        c,
        text=info.get('Title', ''),
        font_name="Helvetica",
        start_font_size=16,
        min_font_size=6,
        box_width=title_box_width,
        box_height=title_region_height,
        x_left=title_x_left,
        y_top=title_region_top,
        line_spacing=1.1,
        center_horizontally=True,
    )


def main(csv_file_path, output_pdf_path, icon_path=None):
    # Read CSV with pandas
    data = pd.read_csv(csv_file_path)
    # Clean up leading/trailing whitespace
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    page_width, page_height = A4
    box_size = 6.5 * cm

    boxes_per_row = int(page_width // box_size)
    boxes_per_column = int(page_height // box_size)
    boxes_per_page = boxes_per_row * boxes_per_column

    # Some margins
    vpageindent = 0.8 * cm
    # Center horizontally
    hpageindent = (page_width - (box_size * boxes_per_row)) / 2

    # We iterate through the data in "pages".
    for i in range(0, len(data), boxes_per_page):
        # --- First page: place QR codes ---
        for index in range(i, min(i + boxes_per_page, len(data))):
            row = data.iloc[index]
            # Build the QR code content: spotify:track:{Track ID}
            qr_content = f"spotify:track:{row['Track ID']}"

            position_index = index % (boxes_per_row * boxes_per_column)
            column_index = position_index % boxes_per_row
            row_index = position_index // boxes_per_row

            x = hpageindent + (column_index * box_size)
            y = page_height - vpageindent - (row_index + 1) * box_size

            add_qr_code_with_border(c, qr_content, (x, y), box_size, icon_path)

        c.showPage()

        # --- Second page: place text information ---
        for index in range(i, min(i + boxes_per_page, len(data))):
            row = data.iloc[index]

            position_index = index % (boxes_per_row * boxes_per_column)
            # Right to left; if you want left to right, remove the (boxes_per_row - 1 - ...)
            column_index = (boxes_per_row - 1) - (position_index % boxes_per_row)
            row_index = position_index // boxes_per_row

            x = hpageindent + (column_index * box_size)
            y = page_height - vpageindent - (row_index + 1) * box_size

            # Prepare info dict for text box
            info = {
                'Artist': row.get('Artist Name(s)', ''),
                'Title': row.get('Track Name', ''),
                'Year': row.get('Release Date', '')
            }
            add_text_box(c, info, (x, y), box_size)

        c.showPage()

    c.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("output_pdf", help="Path to the output PDF file")
    parser.add_argument(
        "--icon",
        help="Path or URL to an icon to embed in the QR Code (PNG with transparency recommended)",
        required=False
    )
    args = parser.parse_args()
    main(args.csv_file, args.output_pdf, args.icon)
