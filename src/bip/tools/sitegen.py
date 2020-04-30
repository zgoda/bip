from __future__ import annotations

import argparse
import json
import os

import cmd2

from ..utils.site import Site

INTRO = '''
Aplikacja do generowania danych statycznych obsługiwanej instytucji.
'''


def load_parser() -> argparse.ArgumentParser:
    """Function to create argument parser for load command.

    :return: argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-file', required=True,
        help='pełna ścieżka do pliku z danymi serwisu',
    )
    return parser


def save_parser() -> argparse.ArgumentParser:
    """Function to create argument parser for save command.

    :return: argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--output-file',
        help='[opcjonalna] pełna ścieżka do pliku do zapisania danych serwisu',
    )
    return parser


class SiteGenerator(cmd2.Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = 'bip> '
        self.intro = INTRO
        self.data = None
        self.dirty = None
        self.output_file = os.path.expanduser('~/site.json')
        self.add_settable(
            cmd2.Settable(
                'output_file', str, 'plik do którego zostanie zapisana konfiguracja'
            )
        )

    def do_new(self, _unused):
        """Utwórz nowy zestaw danych serwisu.
        """
        if self.dirty:
            self.pwarning('Istniejące dane serwisu nie zostały zapisane')
            resp = input('Czy porzucić bieżące dane? [t/N]: ')
            if resp.lower() == 'n':
                return
        self.data = Site.new()
        self.dirty = False
        self.poutput('Utworzony nowy zestaw danych serwisu')

    def do_show(self, _unused):
        """Wyświetlenie bieżących danych serwisu w formacie JSON.
        """
        if self.data is None:
            self.pwarning(
                'Nie ma żadnych danych serwisu, '
                'użyj "load" by załadować lub "new" by zainicjować nowy zestaw'
            )
            return
        if not self.data:
            self.pwarning('Dane serwisu są niepełne')
            return
        self.ppaged(json.dumps(self.data.to_dict(), indent='  '))

    load_parser = load_parser()

    @cmd2.with_argparser(load_parser)
    def do_load(self, args):
        """Załaduj istniejące dane serwisu z pliku.
        """
        try:
            with open(args.input_file) as fp:
                self.data = Site.from_dict(json.load(fp))
            self.poutput(f'Dane serwisu załadowane z pliku {args.input_file}')
        except IOError:
            self.pwarning(f'Nie udało się otworzyć pliku {args.input_file} do odczytu')
            self.data = Site.new()
        self.dirty = False

    save_parser = save_parser()

    @cmd2.with_argparser(save_parser)
    def do_save(self, args):
        """Zapisz dane serwisu do pliku.
        """
        if self.data is None:
            self.pwarning(
                'Nie ma żadnych danych serwisu, '
                'użyj "load" by załadować lub "new" by zainicjować nowy zestaw'
            )
            return
        file_path = args.output_file or self.output_file
        try:
            with open(file_path, 'w') as fp:
                json.dump(self.data.to_dict(), fp)
            self.dirty = False
            self.poutput(f'Dane serwisu zostały zapisane do pliku {file_path}')
        except IOError:
            self.perror(f'Nie udało się otworzyć pliku {file_path} do zapisu')
        except ValueError:
            self.perror('Dane serwisu nie dają się zapisać, sprawdź podane wartości')


def main():  # skipcq: FLK-D103
    import sys
    app = SiteGenerator()
    sys.exit(app.cmdloop())


if __name__ == '__main__':
    main()
