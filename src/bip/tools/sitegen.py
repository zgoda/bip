import cmd2
import argparse

INTRO = '''
Aplikacja do generowania danych statycznych obsługiwanej instytucji.
'''


def load_parser():
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
    def do_load(self):
        """Load existing site data file.
        """
        pass


def main():
    import sys
    app = SiteGenerator()
    sys.exit(app.cmdloop())


if __name__ == '__main__':
    main()
