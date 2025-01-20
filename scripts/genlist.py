#!/usr/bin/env python3

import yaml


def main():
    with open(0, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for list in data:
        print("<section>")
        print(f"<h3>{list["title"]}</h3>")
        print("<ul>")
        for item in list["items"]:
            if link := item.get("link"):
                print(f'<li><a target="_blank" rel="noopener" href="{
                      link}">{item["name"]}</a></li>')
            else:
                print(f'<li>{item["name"]}</li>')
        print("</ul>")
        print("</section>")


if __name__ == "__main__":
    main()
