import logging
import os.path
from argparse import ArgumentParser, ArgumentTypeError, Namespace, RawDescriptionHelpFormatter
import textwrap


class Options(Namespace):
    file: list[str]
    """Absolute paths to target files/directories"""
    format: str
    recursive: bool
    directories: bool
    glob: str
    regex: tuple[str, str] | None
    translate: tuple[str, str] | None
    windows: int | None
    full_width: bool
    emoji: str | None
    strip: str | None
    lower: bool
    slug: bool
    dry_run: bool
    interactive: bool
    # sort: str
    # desc: bool
    log_level: int


def path(f: str) -> str:
    """Convert path argument str to absolute path"""
    f = os.path.expanduser(f)
    if not os.path.exists(f):
        raise ArgumentTypeError(f"path {f} does not exist")
    return os.path.abspath(f)


def build_parser():
    epilog = textwrap.dedent(
        '''\
        FORMAT arguments:
            The original filename can be inserted with {}, and additional
            arguments are: {name}, {ext}, {date}, {datetime}, {size}, {i}.
            Values support custom formatting, like {i:04} or {datetime:%Y-%m-%d}.

        FORMAT examples:
            add number prefix and date suffix:
            {i:04}-{name}-{date}.{ext}
        '''
    )
    parser = ArgumentParser(
        description='Rename files and directories.',
        formatter_class=RawDescriptionHelpFormatter,
        epilog=epilog
    )
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='rename items within subdirectories')
    parser.add_argument('-D', '--directories', action='store_true',
                        help='rename directories within a specified directory')
    parser.add_argument('-g', '--glob', default='*',
                        help='only rename items matching the glob pattern')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dry-run', action='store_true',
                       help='list changes but do not rename anything')
    group.add_argument('-i', '--interactive', action='store_true',
                       help='prompt before each rename operation')

    # parser.add_argument('-s', '--sort', choices=['name', 'date', 'size'],
    #                     metavar='ATTR')
    # parser.add_argument('--desc', action='store_true')

    parser.add_argument('-v', '--verbose',
                        action='store_const', dest='log_level',
                        default=logging.INFO, const=logging.DEBUG,
                        help='output details about matches and operations')

    format = parser.add_argument_group('format')
    format.add_argument('-e', '--regex', nargs=2,
                        metavar=('PATTERN', 'REPLACEMENT',),
                        help='regex pattern replacement, requires 2 args')
    format.add_argument('-t', '--translate', nargs=2,
                        metavar=('CHARS', 'REPLACEMENT',),
                        help='translate individual characters, req. 2 args')
    group = format.add_mutually_exclusive_group()
    group.add_argument('-W', '--windows', nargs='?', const=ord('_'),
                       metavar='REPLACEMENT', type=ord,
                       help='replace characters not allowed on Windows')
    group.add_argument('-F', '--full-width', action='store_true',
                       help='replace unsafe characters with full-width')
    format.add_argument('-J', '--emoji', nargs='?', const='_',
                        metavar='REPLACEMENT', type=str,
                        help='replace emoji characters')
    format.add_argument('-s', '--strip', metavar='CHARS', type=str,
                        help='remove leading/trailing characters')
    format.add_argument('-l', '--lower', action='store_true',
                        help='convert to lowercase')
    format.add_argument('-S', '--slug', action='store_true',
                        help='convert to lowercase+hypens for ws/special char')
    format.add_argument('-f', '--format', default='{fullname}',
                        help='Python format string to rename to, see '
                        'https://docs.python.org/3.11/library/string.html'
                        '#formatstrings')

    parser.add_argument('file', nargs='*', default=[os.getcwd()], type=path,
                        help='file to rename, or directory to rename the '
                        'contents of')

    return parser


def parse_args() -> Options:
    parser = build_parser()
    args = parser.parse_args(namespace=Options)

    if args.format == '{}' and not (
        args.regex or args.translate or args.windows or args.full_width
        or args.emoji or args.strip
    ):
        parser.error(
            'at least one argument is required: -f, -e, -t -W, -F, -J, -s')

    return args
