#!/usr/bin/env python3

WIDTH = 600


def thumbnail_url(id: str, width: int):
    return f"https://dvbkeaxv2fqwj.cloudfront.net/images/{id}/thumbnail?width={width}"


def gallery_url(id: str):
    return f"https://gallery.zekro.de/images/{id}"


def img_element(id: str, width: int):
    tn_url = thumbnail_url(id, width)
    g_url = gallery_url(id)
    return (
        f'<a href="{g_url}" target="_blank">'
        f'<div style="background-image: url({tn_url})"></div>'
        "</a>"
    )


def main():
    with open(0) as f:
        for id in f.readlines():
            print(img_element(id[:-1], WIDTH))


if __name__ == "__main__":
    main()
