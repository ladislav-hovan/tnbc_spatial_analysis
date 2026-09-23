#!/usr/bin/env python

### Imports ###
from pathlib import Path
from typing import Dict

### Functions ###
def fill_out_template(
    template_path: Path,
    subs: Dict[str, str],
    output_path: Path,
) -> None:
    """
    Fills out a text file containing formatable template placeholders
    (in the Python style, i.e. {placeholder}). Saves the result to
    a file. Requires that all the placeholders in the file are
    specified.

    Parameters
    ----------
    template_path : Path
        Path to the template file
    subs : Dict[str, str]
        Dictionary of substitutions to be made in the file
    output_path : Path
        Path to write the filled in file to
    """

    f = open(template_path, 'r')
    content = f.read()
    filled = content.format(**subs)

    of = open(output_path, 'w')
    of.write(filled)

### Main body ###
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-t', '--template', dest='template',
        help='path to the template file', metavar='FILE')
    parser.add_argument('-o', '--output', dest='output',
        help='path to save the filled template to', metavar='FILE')
    parser.add_argument('-s', '--sub', dest='subs', action='append', nargs=2,
        help='pairs of strings to be substituted and new values')

    args = parser.parse_args()
    sub_dict = {k: v for k,v in args.subs}

    fill_out_template(
        template_path=args.template,
        subs=sub_dict,
        output_path=args.output,
    )