#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import datetime
import logging
import os
import shutil
import watchfiles


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


@dataclass
class Page:
    name: str
    content: str
    config: dict


def rebuild(source_dir: str, output_dir: str):
    public_dir = os.path.join(source_dir, "public")
    pages_dir = os.path.join(source_dir, "pages")
    template_dir = os.path.join(source_dir, "templates")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    shutil.copytree(public_dir, os.path.join(output_dir, "public"))

    pages = []
    for pagepath in sorted(os.listdir(pages_dir)):
        pagecontent, cfg = parse_page_config(
            get_file_contents(pages_dir, pagepath))
        name = cfg.get("title") or \
            strip_before_first(strip_after_last(pagepath, '.'), '_')
        pages.append(Page(name=name, content=pagecontent.strip(), config=cfg))

    for page in pages:
        parsedcontent = parse_templates(
            page.content, page, pages, template_dir)

        outpath = os.path.join(output_dir, page.name, "index.html")
        if output := page.config.get("output"):
            outpath = os.path.join(output_dir, output)

        outdir = os.path.dirname(outpath)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with open(outpath, "w", encoding="utf-8") as out:
            out.write(parsedcontent)


def parse_page_config(content: str):
    if not content.startswith("+++"):
        return content, {}

    content = content[3:]

    if "+++" not in content:
        raise Exception("invalid page configuration")

    cfg = {}
    i = content.index("+++")
    cfgstr = content[:i]

    for line in cfgstr.splitlines():
        if len(line.strip()) == 0:
            continue
        [key, val] = [e.strip() for e in line.split("=", 2)]
        cfg[key] = val

    return content[i+4:], cfg


def parse_templates(content, page: Page, pages: list[Page], template_dir: str):
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
            tpl = find_template(template_contents, "pagecontent")
            if tpl == None:
                raise Exception("'pagecontent' not found in extended template")
            (start, end, _) = tpl
            content = template_contents[:start] + \
                content + template_contents[end+1:]
            content = parse_templates(content, page, pages, template_dir)
        elif id == "use":
            if len(args) == 0:
                raise Exception(
                    "template 'use' needs at least one argument")
            use_template = args[0]
            template_contents = get_file_contents(
                template_dir, f"{use_template}.html")
            template_contents = parse_templates(
                template_contents, page, pages, template_dir)
            content = content[:start] + template_contents + content[end+1:]
        elif id == "pagename":
            content = content[:start] + page.name + content[end+1:]
        elif id == "navitems":
            nav_items = []
            for p in pages:
                if strtobool(p.config.get("navignore")):
                    continue
                path = (p.config.get("path") or '/' + p.name)
                active = ' class="active"' if p.name == page.name else ""
                nav_items.append(f'<a href="{path}"{active}>{p.name}</a>')
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


def strtobool(s: str):
    return s is not None and s.strip().lower() in ["true", "1", "yes", "t", "on"]


if __name__ == "__main__":
    main()
