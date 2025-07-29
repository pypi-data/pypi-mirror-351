import argparse
import sys
from pathlib import Path

from .converter import Converter


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('-f', '--pipfile', type=Path, default='Pipfile', help='Path to Pipfile')
    p.add_argument('-t', '--pyproject', type=Path, default='pyproject.toml', help='Path to pyproject.toml')
    p.add_argument('--fix', action='store_true', help='Apply required changes')
    args = p.parse_args(argv)

    c = Converter(args.pipfile, args.pyproject)
    diff = c.diff()

    if diff.empty:
        print('pyproject.toml is up to date')
        return

    if diff.deps:
        print(f'Dependencies out of sync:\n{diff.deps}')

    if diff.version:
        print(f'Version out of sync: {diff.version}')

    if not args.fix:
        print('pyproject.toml NEEDS UPDATE!')
        sys.exit(1)

    c.sync()
    print('pyproject.toml UPDATED!')


if __name__ == '__main__':
    main()
