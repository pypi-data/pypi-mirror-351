import datetime
import glob
import os.path
import re
from .formatter import format_impl
from .logging import color, init_logging, log
from .options import parse_args, Options


def main():
    args = parse_args()
    init_logging(args.log_level)

    pattern = args.glob
    if args.recursive:
        pattern = '**/' + pattern

    i = 0
    for f in args.file:
        if os.path.isdir(f):
            log.debug('Directory: %s', f)
            for g in glob.glob(pattern, root_dir=f, recursive=args.recursive):
                fg = os.path.join(f, g)
                if os.path.isdir(fg):
                    log.debug('Subdirectory: %s', g)
                    if args.directories:
                        i += 1
                        rename(fg, args, i)
                else:
                    i += 1
                    rename(fg, args, i)
        else:
            i += 1
            rename(f, args, i)


def rename(src: str, args: Options, i: int):
    dir = os.path.dirname(src)
    file = os.path.basename(src)
    stat = os.stat(src)
    mdate = datetime.datetime.fromtimestamp(stat.st_mtime)

    re_file = file
    if args.regex:
        pattern = re.compile(args.regex[0])
        re_file = re.sub(pattern, args.regex[1], re_file)

    if args.translate:
        trans = str.maketrans(args.translate[0], args.translate[1])
        re_file = re_file.translate(trans)

    if args.windows is not None:
        trans = str.maketrans('"*:<>?|/\\', chr(args.windows) * 9)
        re_file = re_file.translate(trans).strip()
    elif args.full_width:
        trans = str.maketrans('/\\"*:<>?|', '⧸⧹＂＊：＜＞？｜')
        re_file = re_file.translate(trans)

    if args.emoji is not None:
        # TODO: this covers many, but not all Emoji.
        emoji_pattern = r"[\U00010000-\U0010ffff]"
        re_file = re.sub(emoji_pattern, args.emoji, re_file)

    if args.strip is not None:
        re_file = re_file.strip(args.strip)

    if args.lower:
        re_file = re_file.lower()

    if args.slug:
        trans = str.maketrans('_"*:<>?|/\\', '-' * 10)
        re_file = re_file.translate(trans).lower().strip()
        re_file = re.sub(r'[\s-]+', '-', re_file)
        re_file = '.'.join(p.strip('-') for p in re_file.split('.'))

    root, ext = os.path.splitext(re_file)
    kwargs = {
        "i": i,
        "name": root,
        "ext": ext[1:],
        "fullname": re_file,
        "size": stat.st_size,
        "date": mdate.strftime('%Y-%m-%d'),
        "datetime": mdate,
    }
    result = format_impl(args.format, re_file, **kwargs)
    dest = os.path.join(dir, result)

    if file == result:
        return

    if args.dry_run or args.interactive:
        print(file, color('->', 'cyan'), result)
        if args.dry_run:
            return
        act = input(color('Rename? [Y/n] ', 'yellow'))
        if act != '' and act.lower()[0] != 'y':
            return
    else:
        log.debug('%s -> %s', file, result)

    common = os.path.commonpath([src, dest])
    prefix = os.path.dirname(dest)
    if common != prefix and not os.path.isdir(prefix):
        os.makedirs(prefix)
    os.rename(src, dest)


if __name__ == "__main__":
    main()
