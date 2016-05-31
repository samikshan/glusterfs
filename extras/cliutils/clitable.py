# -*- coding: utf-8 -*-
import sys

USE_CLI_COLOR = True


def use_cli_color(flag):
    global USE_CLI_COLOR
    USE_CLI_COLOR = flag


class COLORS:
    """
    Terminal Colors
    """
    RED = "\033[31m"
    GREEN = "\033[32m"
    ORANGE = "\033[33m"
    NOCOLOR = "\033[0m"
    BLACK = "\033[30m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def colored(txt, color=None):
    if color is None or not USE_CLI_COLOR:
        return txt

    c = getattr(COLORS, color.upper(), None)
    if c is None:
        return txt

    return "{0}{1}{2}".format(c, txt, COLORS.NOCOLOR)


DEFAULT_FORMAT = {
    "width": 0,
    "align": "left",
    "fill": "",
    "color": lambda x: "default"
}

ALIGN = {
    "left": "<",
    "default": "<",
    "right": ">",
    "center": "^"
}


def clicolumn(txt, opts=DEFAULT_FORMAT, title=False):
    align = opts.get("align").lower()
    if hasattr(opts.get("color"), "__call__"):
        c = opts.get("color")(txt)
    else:
        c = opts.get("color")

    c = c.upper()
    if getattr(COLORS, c, None) is None or title:
        c = None

    if align not in ALIGN:
        align = "default"

    align = ALIGN[align]
    width = opts.get("width", 0)
    fill = opts.get("fill", "")

    raw_txt = "{0:{fill}{align}{width}}".format(txt,
                                                fill=fill,
                                                align=align,
                                                width=width)
    return colored(raw_txt, c)


class CliTable(object):
    def __init__(self, num_columns, space="   ",
                 title_row=True, underline=True,
                 row_color_func=lambda x: "default"):
        self.num_columns = num_columns
        self.cols_format = [DEFAULT_FORMAT] * num_columns
        self.rows = []
        self.title_row_values = []
        self.max_lengths = [0] * num_columns
        self.space = space
        self.title_row = title_row
        self.underline = underline
        self.row_color_func = row_color_func

    def format_column(self, col, align="left",
                      fill="", color=lambda x: "default"):
        self.cols_format[col - 1] = {
            "align": align,
            "fill": fill,
            "color": color
        }

    def set_max(self, values):
        for idx, v in enumerate(values):
            v = str(v)
            if self.max_lengths[idx] < len(v):
                self.max_lengths[idx] = len(v)

    def add_title_row(self, *values):
        self.set_max(values)
        self.title_row_values = values

    def add_row(self, *values):
        self.set_max(values)
        self.rows.append(values)

    def display(self):
        if self.rows:
            # Print Title Row and Underline using hyphen
            if self.title_row_values:
                title_row_out = []
                total_length = 0
                for idx, col in enumerate(self.title_row_values):
                    total_length += self.max_lengths[idx]
                    self.cols_format[idx]["width"] = self.max_lengths[idx]
                    title_row_out.append(
                        clicolumn(col, DEFAULT_FORMAT, title=True)
                    )
                sys.stdout.write("{0}\n".format(self.space.join(
                    title_row_out)))
                if self.underline:
                    hyphen_width = (len(self.space) * (self.num_columns - 1) +
                                    total_length)
                    sys.stdout.write("{0}\n".format("-" * hyphen_width))

        for row in self.rows:
            row_out = []
            raw_data_for_row_color = []
            for idx, col in enumerate(row):
                self.cols_format[idx]["width"] = self.max_lengths[idx]

                raw_data_for_row_color.append(col)
                row_out.append(
                    clicolumn(col, self.cols_format[idx])
                )

            row_color = self.row_color_func(raw_data_for_row_color)
            row_color = row_color.upper()
            if getattr(COLORS, row_color, None) is None:
                row_color = None

            out = "{0}\n".format(self.space.join(row_out))
            sys.stdout.write(colored(out, row_color))
