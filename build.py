import datetime
import os
import shutil


SRC_DIR = "src"
TEMPLATE_DIR = os.path.join(SRC_DIR, "templates")
PUBLIC_DIR = os.path.join(SRC_DIR, "public")
PAGES_DIR = os.path.join(SRC_DIR, "pages")

OUTPUT_DIR = "dist"


NAV_OVERRIDES = {
    'index': ('hey', '/'),
    'imprint': ('imprint', None),
}


OUTPUT_OVERRIDES = {
    'index': "index.html"
}


def main():

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(PUBLIC_DIR, os.path.join(OUTPUT_DIR, "public"))

    pages = []
    for filename in os.listdir(PAGES_DIR):
        name = strip_before_first(strip_after_last(filename, '.'), '_')
        pages.append((name, os.path.join(PAGES_DIR, filename)))

    for (pagename, pagepath) in pages:
        pagecontent = get_file_contents(pagepath)
        parsedcontent = parse_templates(
            pagecontent, pagename, [p for (p, _) in pages])

        outpath = os.path.join(OUTPUT_DIR, pagename, "index.html")
        if pagename in OUTPUT_OVERRIDES:
            outpath = os.path.join(OUTPUT_DIR, OUTPUT_OVERRIDES[pagename])

        outdir = os.path.dirname(outpath)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with open(outpath, "w", encoding="utf-8") as out:
            out.write(parsedcontent)


def parse_templates(content: str, pagename: str, pages: list[str]):
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
                TEMPLATE_DIR, f"{ext_template}.html")
            (start, end, _) = find_template(template_contents, "pagecontent")
            content = template_contents[:start] + \
                content + template_contents[end+1:]
            content = parse_templates(content, pagename, pages)
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
