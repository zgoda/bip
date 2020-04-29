import argparse
import json

import cmd2

INTRO = '''
Aplikacja do generowania danych statycznych obsługiwanej instytucji.
'''


def load_parser():
    """Function to create argument parser for load command.

    :return: argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-file', required=True, help='path to site data file'
    )
    return parser


class SiteGenerator(cmd2.Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = 'bip> '
        self.intro = INTRO
        self.data = None

    load_parser = load_parser()

    @cmd2.with_argparser(load_parser)
    def do_load(self, args):
        """Load existing site data file.
        """
        with open(args.input_file) as fp:
            self.data = json.load(fp)


def main():  # skipcq: FLK-D103
    import sys
    app = SiteGenerator()
    sys.exit(app.cmdloop())


if __name__ == '__main__':
    main()
