#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import configparser
import subprocess
import sys
import tempfile

from jinja2 import Environment, PackageLoader
from unidecode import unidecode


class OMLogo(object):
    """This class handle openMairie logo generation."""

    svg_data = ""

    def __init__(self, args):
        """ """
        self.args = args
        self._tools = self._available_tools()
        self._j2env = Environment(
            loader=PackageLoader("openmairie.devtools", "templates")
        )

    def render(self):
        """ """
        # import pdb; pdb.set_trace( )
        template = self._j2env.get_template("%s.svg.j2" % self.args.template)
        return template.render(
            application_name=self.args.application_name.decode(sys.stdin.encoding),
            base_color=self.args.base_color,
            triangle_color=self.args.triangle_color,
        ).encode(sys.stdout.encoding)

    def save(self, data, filename):
        """ """
        path = "%s/%s" % (tempfile.gettempdir(), filename)
        with open(path, "w") as f:
            f.write(data)
        return path

    def process(self):
        """ """
        data = self.render()
        filename = unidecode(self.args.application_name.decode(sys.stdin.encoding))
        svg_path = self.save(data, "%s.svg" % filename)
        print("SVG saved as: %s" % svg_path)
        png_path = "%s/%s.png" % (tempfile.gettempdir(), filename)

        # Convert SVG to PNG
        if self._tools["inkscape"]:
            subprocess.call(["inkscape", "-T", "-D", "-e", png_path, "-f", svg_path])

        # open the PNG if possible
        if self._tools["xdg-open"]:
            subprocess.call(["xdg-open", png_path])

    def _available_tools(self):
        """ """
        tools = {}
        for command in ("inkscape -V", "xdg-open --version"):
            try:
                tool = command.split(" ")[0]
                subprocess.call(command.split(" "))
            except OSError:
                print("%s is not available on your environnement." % tool)
                tools[tool] = False
            else:
                tools[tool] = True
        return tools


def main(args=None):
    """The main routine."""
    parser = configparser.ConfigParser()

    parser = argparse.ArgumentParser(description="om-logo",)
    parser.add_argument(
        "-a",
        dest="application_name",
        help="Your application name. Case is sensitive.",
        required=True,
    )
    parser.add_argument(
        "-b",
        dest="base_color",
        default="#808080",
        help="Your base color (text and circle), in hexadecimal, with quotes "
        "as separators (ex : '#808080')",
    )
    parser.add_argument(
        "-c",
        dest="triangle_color",
        default="#88aa00",
        help="Your triangle color, in hexadecimal, with quotes as separators "
        "(ex : '#88aa00')",
    )
    parser.add_argument(
        "-t",
        dest="template",
        default="banner",
        help="Which kind of logo should we generate ? Pick your choice "
        "between : banner | others_to_come",
    )
    #

    OMLogo(parser.parse_args()).process()


if __name__ == "__main__":
    main()
