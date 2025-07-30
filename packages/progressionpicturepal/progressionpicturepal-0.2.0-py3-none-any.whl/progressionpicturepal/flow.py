from PIL import Image, ImageDraw, ImageFont
import os
import math

class FlowDiagram:
    """
    A library to compose images with captions,
    scale them to a maximum size, and arrange them in rows with
    a maximum number of nodes per row (zig-zag layout), drawing
    directional arrows with arrowheads on a transparent background.
    Supports configurable padding between images and captions, dynamic
    caption height calculation, and automatic text wrapping within image width.
    """
    def __init__(
        self,
        spacing=20,
        spacing_vertical=50,
        caption_padding=10,
        max_node_dim=500,
        max_per_row=None,
        font_path=None,
        font_size=14,
        arrow_color=(0, 0, 0, 255),
        arrow_width=3,
        arrowhead_width=6,
        arrow_padding_h=15,
        arrow_padding_v=40,
        background=(255, 255, 255, 0),
    ):
        self.spacing = spacing
        self.spacing_vertical = spacing_vertical
        self.caption_padding = caption_padding
        self.max_node_dim = max_node_dim
        self.max_per_row = max_per_row
        self.arrow_color = arrow_color
        self.arrow_width = arrow_width
        self.arrowhead_width = arrowhead_width
        self.arrow_padding_h = arrow_padding_h
        self.arrow_padding_v = arrow_padding_v
        self.background = background

        # Load font
        if font_path and os.path.exists(font_path):
            self.font = ImageFont.truetype(font_path, font_size)
        else:
            try:
                self.font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except OSError:
                self.font = ImageFont.load_default()

        self.nodes = []
        self.arrows = []

    def add_node(self, image_path, caption):
        img = Image.open(image_path).convert("RGBA")
        max_side = max(img.width, img.height)
        if max_side > self.max_node_dim:
            scale = self.max_node_dim / max_side
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        self.nodes.append((img, caption))

    def add_arrow(self, from_idx, to_idx):
        self.arrows.append((from_idx, to_idx))

    def _wrap_text(self, text, draw, max_width):
        words = text.split()
        lines = []
        if not words:
            return lines
        line = words[0]
        for word in words[1:]:
            test_line = f"{line} {word}"
            bbox = draw.textbbox((0, 0), test_line, font=self.font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
        return lines

    def _compute_layout(self):
        # Dummy draw for text measurement
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), "Ay", font=self.font)
        line_height = bbox[3] - bbox[1]

        n = len(self.nodes)
        if not self.max_per_row or self.max_per_row >= n:
            widths = [img.width for img, _ in self.nodes]
            total_w = sum(widths) + self.spacing * (n - 1)

            max_img_h = max(img.height for img, _ in self.nodes)
            max_text_h = 0
            for img, cap in self.nodes:
                lines = self._wrap_text(cap, dummy_draw, img.width)
                max_text_h = max(max_text_h, len(lines) * line_height)

            total_h = max_img_h + self.caption_padding + max_text_h + self.caption_padding
            return total_w, total_h

        rows = [list(range(i, min(i + self.max_per_row, n))) for i in range(0, n, self.max_per_row)]
        row_widths = []
        total_h = 0
        for row in rows:
            row_w = sum(self.nodes[i][0].width for i in row) + self.spacing * (len(row) - 1)
            max_img_h = max(self.nodes[i][0].height for i in row)
            max_text_h = 0
            for i in row:
                img, cap = self.nodes[i]
                lines = self._wrap_text(cap, dummy_draw, img.width)
                max_text_h = max(max_text_h, len(lines) * line_height)

            row_h = max_img_h + self.caption_padding + max_text_h + self.caption_padding
            row_widths.append(row_w)
            total_h += row_h
        total_h += self.spacing_vertical * (len(rows) - 1)
        return max(row_widths), total_h

    def arrowed_line(self, canvas, ptA, ptB):
        draw = ImageDraw.Draw(canvas)
        draw.line([ptA, ptB], fill=self.arrow_color, width=self.arrow_width)
        x0, y0 = ptA
        x1, y1 = ptB
        xb = x0 + 0.95 * (x1 - x0)
        yb = y0 + 0.95 * (y1 - y0)
        if x0 == x1:
            v0 = (xb - self.arrowhead_width, yb)
            v1 = (xb + self.arrowhead_width, yb)
        elif y0 == y1:
            v0 = (xb, yb - self.arrowhead_width)
            v1 = (xb, yb + self.arrowhead_width)
        else:
            alpha = math.atan2(y1 - y0, x1 - x0) - math.pi / 2
            a = self.arrowhead_width * math.cos(alpha)
            b = self.arrowhead_width * math.sin(alpha)
            v0 = (xb + a, yb + b)
            v1 = (xb - a, yb - b)
        draw.polygon([v0, v1, ptB], fill=self.arrow_color)

    def render(self):
        canvas_w, canvas_h = self._compute_layout()
        canvas = Image.new("RGBA", (int(canvas_w), int(canvas_h)), self.background)
        draw = ImageDraw.Draw(canvas)

        n = len(self.nodes)
        if not self.max_per_row or self.max_per_row >= n:
            rows = [list(range(n))]
        else:
            rows = [list(range(i, min(i + self.max_per_row, n))) for i in range(0, n, self.max_per_row)]

        positions = {}
        y_offset = 0

        for r_idx, row in enumerate(rows):
            # measure heights
            bbox = draw.textbbox((0, 0), "Ay", font=self.font)
            line_height = bbox[3] - bbox[1]
            max_img_h = max(self.nodes[i][0].height for i in row)
            max_text_h = 0
            wraps = {}
            for i in row:
                img, cap = self.nodes[i]
                lines = self._wrap_text(cap, draw, img.width)
                wraps[i] = lines
                max_text_h = max(max_text_h, len(lines) * line_height)

            row_h = max_img_h + self.caption_padding + max_text_h + self.caption_padding

            # zig-zag
            forward = (r_idx % 2 == 0)
            x_offset = 0 if forward else canvas_w

            for idx in (row if forward else (row)):
                img, _ = self.nodes[idx]
                if forward:
                    xpos = x_offset
                    x_offset += img.width + self.spacing
                else:
                    xpos = x_offset - img.width
                    x_offset -= img.width + self.spacing

                positions[idx] = (xpos, y_offset, img.width, img.height)
                canvas.paste(img, (int(xpos), int(y_offset)), img)

                # draw wrapped caption lines
                lines = wraps[idx]
                for li, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=self.font)
                    line_w = bbox[2] - bbox[0]
                    cy = y_offset + max_img_h + self.caption_padding + li * line_height
                    cx = xpos + (img.width - line_w) / 2
                    draw.text((cx, cy), line, fill=self.arrow_color, font=self.font)

            y_offset += row_h + (self.spacing_vertical if r_idx < len(rows) - 1 else 0)

        # arrows
        for src, dst in self.arrows:
            sx, sy, sw, sh = positions[src]
            dx, dy, dw, dh = positions[dst]
            src_row = next(i for i, row in enumerate(rows) if src in row)
            dst_row = next(i for i, row in enumerate(rows) if dst in row)

            if src_row == dst_row:
                if src_row % 2 == 0:
                    ptA = (sx + sw + self.arrow_padding_h, sy + sh / 2)
                    ptB = (dx - self.arrow_padding_h, dy + dh / 2)
                else:
                    ptA = (sx - self.arrow_padding_h, sy + sh / 2)
                    ptB = (dx + dw + self.arrow_padding_h, dy + dh / 2)
            else:
                if dst_row > src_row:
                    ptA = (sx + sw / 2, sy + sh + self.arrow_padding_v)
                    ptB = (dx + dw / 2, dy - self.arrow_padding_v / 4)
                else:
                    ptA = (sx + sw / 2, sy - self.arrow_padding_v)
                    ptB = (dx + dw / 2, dy + dh + self.arrow_padding_v)

            self.arrowed_line(canvas, ptA, ptB)

        return canvas

    def save(self, path):
        self.render().save(path)


def create_flow_diagram(images, output_path, num_images=None, **fd_kwargs):
    """
    Generate and save a flow diagram from a list of (image_path, caption) tuples.

    :param images: List of (image_path, caption) tuples.
    :param output_path: File path to save the resulting diagram.
    :param num_images: Number of images from the list to include (default: all).
    :param fd_kwargs: Keyword args passed to FlowDiagram initializer.
    """
    if num_images is None:
        num_images = len(images)
    fd = FlowDiagram(**fd_kwargs)
    for image_path, caption in images[:num_images]:
        fd.add_node(image_path, caption)
    for i in range(min(num_images, len(images)) - 1):
        fd.add_arrow(i, i+1)
    fd.save(output_path)