#!/usr/bin/env python3

import argparse
import datetime
import logging
import os
import shutil
import watchfiles


NAV_OVERRIDES = {
    'index': ('hey', '/'),
    'imprint': ('imprint', None),
}


OUTPUT_OVERRIDES = {
    'index': "index.html"
}


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument("-w", "--watch", action='store_true',
                   help="Watch source directory for changes and rebuild")
    p.add_argument("-s", "--source", default="src",
                   help="Source directory")
    p.add_argument("-o", "--output", default="dist",
                   help="Output directory")
    p.add_argument("-l", "--log-level", default=2, type=int,
                   help="Set log level of the default logger. "
                   "(default 1)")

    return p.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=(args.log_level * 10),
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if args.watch:
        watch(args.source, args.output)
        return

    rebuild(args.source, args.output)


def watch(source_dir: str, output_dir: str):
    logging.info(f"Start watching {source_dir} ...")
    for changes in watchfiles.watch(source_dir, raise_interrupt=False):
        for (m, f) in changes:
            logging.info(f"Change detected: {m.name} {f}")
        rebuild(source_dir, output_dir)


def rebuild(source_dir: str, output_dir: str):
    public_dir = os.path.join(source_dir, "public")
    pages_dir = os.path.join(source_dir, "pages")
    template_dir = os.path.join(source_dir, "templates")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    shutil.copytree(public_dir, os.path.join(output_dir, "public"))

    pages = []
    for filename in sorted(os.listdir(pages_dir)):
        name = strip_before_first(strip_after_last(filename, '.'), '_')
        pages.append((name, os.path.join(pages_dir, filename)))

    for (pagename, pagepath) in pages:
        pagecontent = get_file_contents(pagepath)
        parsedcontent = parse_templates(
            pagecontent, pagename, [p for (p, _) in pages], template_dir)

        outpath = os.path.join(output_dir, pagename, "index.html")
        if pagename in OUTPUT_OVERRIDES:
            outpath = os.path.join(output_dir, OUTPUT_OVERRIDES[pagename])

        outdir = os.path.dirname(outpath)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with open(outpath, "w", encoding="utf-8") as out:
            out.write(parsedcontent)


def parse_templates(content: str, pagename: str, pages: list[str], template_dir: str):
    template = find_next_template(content)

    while True:
        template = find_next_template(content)
        if not template:
            return content

        (start, end, id, args) = template

        if id == "extends":
            if len(args) == 0:
                raise Exception(
                    "template 'extends' needs at least one argument")
            content = content[:start] + content[end+1:]
            ext_template = args[0]
            template_contents = get_file_contents(
                template_dir, f"{ext_template}.html")
            (start, end, _) = find_template(template_contents, "pagecontent")
            content = template_contents[:start] + \
                content + template_contents[end+1:]
            content = parse_templates(content, pagename, pages, template_dir)
        elif id == "use":
            if len(args) == 0:
                raise Exception(
                    "template 'use' needs at least one argument")
            use_template = args[0]
            template_contents = get_file_contents(
                template_dir, f"{use_template}.html")
            template_contents = parse_templates(
                template_contents, pagename, pages, template_dir)
            content = content[:start] + template_contents + content[end+1:]
        elif id == "pagename":
            name = pagename
            if pagename in NAV_OVERRIDES:
                (name, _) = NAV_OVERRIDES[pagename]
            content = content[:start] + name + content[end+1:]
        elif id == "navitems":
            nav_items = []
            for page in pages:
                name = page
                path = '/' + page
                if page in NAV_OVERRIDES:
                    (name, path) = NAV_OVERRIDES[page]
                    if path == None:
                        continue
                active = ' class="active"' if page == pagename else ""
                nav_items.append(f'<a href="{path}"{active}>{name}</a>')
            content = content[:start] + "\n".join(nav_items) + content[end+1:]
        elif id == "currentyear":
            year = datetime.datetime.now().year
            content = content[:start] + str(year) + content[end+1:]
        else:
            raise Exception(f"unsupported template '{id}'")


def strip_after_last(v: str, delim: str):
    if delim not in v:
        return v
    i = v.rindex(delim)
    return v[:i]


def strip_before_first(v: str, delim: str):
    if delim not in v:
        return v
    i = v.index(delim)
    return v[i+1:]


def get_file_contents(*dirs):
    with open(os.path.join(*dirs), encoding="utf-8") as f:
        return str(f.read())


def find_next_template(content: str):
    if "{{" not in content:
        return None

    start = content.index("{{")
    end = content.index("}}") + 1
    split = content[start+2:end-1].strip().split()
    if len(split) < 1:
        raise Exception("invalid template format")
    return (start, end, split[0], split[1:])


def find_template(content: str, target_id: str):
    offset = 0
    while True:
        template = find_next_template(content[offset:])
        if not template:
            return None
        (start, end, id, args) = template
        if id == target_id:
            return (start+offset, end+offset, args)
        offset += end+1


if __name__ == "__main__":
    main()
