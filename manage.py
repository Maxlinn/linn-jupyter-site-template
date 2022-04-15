# work by Maxlinn

import argparse
import os
import re
from urllib.parse import urlparse
from urllib.request import quote
from typing import List, Union


class IComponent(object):
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        pass

    def run(self, args: argparse.Namespace):
        pass


class FixLocalLinkComponent(IComponent):

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--fix-local-link', action='store_true',
                            default=False, help='Turn on MarkdownLocallyLinkFixer.')
        parser.add_argument('--fix-base-dir', type=str,
                            default='.', help='From where to start fix, default to current directory.')
        parser.add_argument('--fix-file-ext-regex', type=str,
                            default=r'\.md|\.ipynb', help='Which extensions of file to fix, using regex; '
                                                  'If want everything(even no ext), using ".*".')
        parser.add_argument('--fix-convert-path-sep', action='store_true',
                            default=True, help='Whether to replace \\ in link to /.')

    def run(self, args: argparse.Namespace):
        def should_ignore(basename):
            return re.match(args.ignore_regex, basename) is not None

        def is_ext_ok(fname):
            ext = os.path.splitext(fname)[1]
            return re.match(args.fix_file_ext_regex, ext) is not None

        for root, dirs, files in os.walk(args.fix_base_dir):
            dirs[:] = [dname for dname in dirs if not should_ignore(dname)]
            files = [fname for fname in files if not should_ignore(fname)]
            files = [fname for fname in files if is_ext_ok(fname)]

            for fname in files:
                filename = os.path.join(root, fname)

                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                def callback(matchobj):
                    # 0-th position of matchobj is the original string
                    text, link = matchobj.group(1), matchobj.group(2)
                    # ignore link with a scheme, like 'http/https/file'
                    if urlparse(link).scheme:
                        return f'[{text}][{link}]'
                    # the link is relative of current dir, that is, root
                    target_filename = os.path.join(root, link)
                    # must: ask OS to do the simplification
                    target_filename = os.path.realpath(target_filename)
                    # compute the relative path to base dir
                    target_relname = os.path.relpath(
                        target_filename, args.fix_base_dir)
                    # replace \\ to /
                    if args.fix_convert_path_sep:
                        target_relname = target_relname.replace('\\', '/')
                    return f'[{text}]({target_relname})'

                content = re.sub(r'\[(.*?)\]\((.+?)\)', callback, content)

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)


class GenSideBarComponent(IComponent):

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--gen-side-bar', action='store_true',
                            default=False, help='Turn on SidebarGenerator.')

        parser.add_argument('--gen-base-dir', type=str,
                            default='.', help='From where to start generate sidebar, default to current directory; '
                                              'Tips: several bases dirs with --gen-output-behavior="append", '
                                              'could generate sidebar semi-automatically.')
        parser.add_argument('--gen-file-ext-regex', type=str,
                            default=r'\.md', help='Which extensions of file to generate, using regex; '
                                                  'If want everything(even no ext), using ".*".')
        # noneed:
        # parser.add_argument('--gen-max-depth', type=int,
        #                     default=3, help='File/Dir deeper than max_depth will be flattened, consider root as 1.')
        # todo: how to check time in git
        parser.add_argument('--gen-sort-by', type=str,
                            choices=['name', 'name_desc', 'created',
                                     'created_desc', 'modified', 'modified_desc'],
                            default='name',
                            const='name',
                            nargs='?',
                            help='How to sort items of current depth.')
        # always:
        # parser.add_argument('--gen-readme-on-branch', action='store_true',
        #                     default=True, help='Do not generate leaf of README.md, instead, move it to the branch.')
        parser.add_argument('--gen-convert-path-sep', action='store_true',
                            default=True, help='Whether to replace \\ in link to /.')
        parser.add_argument('--gen-output', type=str,
                            default='_sidebar.md', help='Specify the output sidebar file.')
        parser.add_argument('--gen-output-behavior', type=str,
                            choices=('overwrite', 'append', 'skip'),
                            default='overwrite',
                            const='overwrite',
                            nargs='?',
                            help='The behavior of generate output; '
                                 'overwrite always write to output; '
                                 'append will append to exist output (useful to combine manual and automatic); '
                                 'skip will only create when the output does not exist')

    def run(self, args: argparse.Namespace):

        if args.gen_output_behavior == 'skip' and os.path.exists(args.gen_output):
            return

        # key: dir relpath to args.gen_base_dir, e.g. args.gen_base_dir='.', key='.\\abc\\def'
        # value: (its dirs, its files), relpath, same format as key
        # dir2ls is used to express all subdirs in a flattened way
        dir2ls = {}

        def should_ignore(basename):
            return re.match(args.ignore_regex, basename) is not None

        def is_ext_ok(fname):
            ext = os.path.splitext(fname)[1]
            return re.match(args.gen_file_ext_regex, ext) is not None

        # first ret of os.walk is **not** always absolute
        for root, dirs, files in os.walk(args.gen_base_dir):
            # to filter dirs to be visited by os.walk, remove items in `dirs`(**same object**)
            dirs[:] = [dname for dname in dirs if not should_ignore(dname)]
            files = [fname for fname in files if not should_ignore(fname)]
            files = [fname for fname in files if is_ext_ok(fname)]

            dirnames = [os.path.join(root, dname) for dname in dirs]
            filenames = [os.path.join(root, fname) for fname in files]

            dir2ls[root] = (dirnames, filenames)

        # convert to URL-compatible
        def clean_path(path: str) -> str:
            if args.gen_convert_path_sep:
                path = path.replace('\\', '/')
            path = quote(path)
            return path

        def get_sort_key_and_reverse():
            is_reverse = (args.gen_sort_by.rfind('_desc') != -1)
            criterion = None
            if args.gen_sort_by.find('name') != -1:
                criterion = lambda fname: fname
            elif args.gen_sort_by.find('created') != -1:
                criterion = lambda fname: os.stat(os.path.join(args.gen_base_dir), fname).st_ctime
            elif args.gen_sort_by.find('modified') != -1:
                criterion = lambda fname: os.stat(os.path.join(args.gen_base_dir), fname).st_mtime
            return criterion, is_reverse

        # Generate markdown bullet list sidebar, DFS
        # Final markdown string to write
        towrite = ''
        criterion, is_reverse = get_sort_key_and_reverse()

        def gen_bullet_list_worker(root: str, indent: int = 0):
            nonlocal towrite
            # sort dirnames and filenames this level altogether
            dirnames, filenames = dir2ls[root]
            names = sorted(dirnames + filenames, key=criterion, reverse=is_reverse)
            for name in names:
                basename = os.path.basename(name)
                basename_noext = os.path.splitext(basename)[0]

                line = '\t' * indent + f'- [{basename_noext}]({clean_path(name)})'
                towrite += line + '\n'
                # recursively searching. using 'name in dirnames' to decide whether it's a file of dir
                # since generally dirs are less than files
                if name in dirnames:
                    gen_bullet_list_worker(name, indent + 1)

        gen_bullet_list_worker(args.gen_base_dir)

        if args.gen_output_behavior in ['skip', 'overwrite']:
            flag = 'w'
        elif args.gen_output_behavior == ['append']:
            flag = 'a'

        with open(args.gen_output, flag, encoding='utf-8') as f:
            if flag == 'a':
                f.write('\n')
            f.write(towrite)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--ignore-regex', type=str, default=r'^\..+|^_|node_modules',
                        help='Which files do not operate(decided by each component), '
                             'default to file/dirs start with dot(.xxx) or underscore(_) and notorious node_modules.')

    FixLocalLinkComponent.add_arguments(parser)
    GenSideBarComponent.add_arguments(parser)

    args = parser.parse_args()

    if args.fix_local_link:
        obj = FixLocalLinkComponent()
        obj.run(args)

    if args.gen_side_bar:
        obj = GenSideBarComponent()
        obj.run(args)
