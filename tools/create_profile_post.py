#!/usr/bin/env python3
"""Create a Hexo profile-footprint post from founder, website, and links."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "source" / "_posts"
CONFIG_PATH = ROOT / "_config.yml"


@dataclass
class WebsiteContext:
    title: str = ""
    description: str = ""
    headings: list[str] | None = None


class HomepageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.heading_level: str | None = None
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.headings: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag in {"h1", "h2"}:
            self.heading_level = tag
            self.heading_parts = []
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description" or prop == "og:description":
                content = clean_text(attrs_dict.get("content", ""))
                if content and not self.description:
                    self.description = content

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == self.heading_level:
            heading = clean_text(" ".join(self.heading_parts))
            if heading:
                self.headings.append(heading)
            self.heading_level = None
            self.heading_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.heading_level:
            self.heading_parts.append(data)

    def context(self) -> WebsiteContext:
        return WebsiteContext(
            title=clean_text(" ".join(self.title_parts)),
            description=self.description,
            headings=self.headings[:6],
        )


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_homepage_description(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""

    cta_pattern = re.compile(
        r"\b(start|try|sign up|signup|get started|book|unlock|claim|join)\b.*"
        r"\b(today|now|free trial|demo)\b|\bfree trial\b",
        re.IGNORECASE,
    )
    sentences = re.split(r"(?<=[.!?])\s+", value)
    filtered = [sentence for sentence in sentences if sentence and not cta_pattern.search(sentence)]
    return " ".join(filtered or sentences[:1])


def ensure_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("URL cannot be empty")
    if not value.startswith(("http://", "https://")):
        return f"https://{value}"
    return value


def fetch_context(url: str, timeout: int) -> WebsiteContext:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read(400_000).decode(charset, errors="replace")

    parser = HomepageParser()
    parser.feed(html)
    return parser.context()


def infer_product_name(website: str, context: WebsiteContext) -> str:
    candidates = []
    if context.title:
        title = context.title
        for separator in (" | ", " - ", " – ", " — ", ": "):
            title = title.split(separator, 1)[0]
        candidates.append(title)
    if context.headings:
        candidates.extend(context.headings[:2])

    for candidate in candidates:
        candidate = clean_text(candidate)
        if 2 <= len(candidate) <= 48 and not candidate.lower().startswith(("home", "welcome")):
            return candidate

    host = urlparse(website).hostname or website
    label = host.removeprefix("www.").split(".", 1)[0]
    return re.sub(r"[-_]+", " ", label).title()


def offering_sentence(product_name: str, context: WebsiteContext, fallback: str | None) -> str:
    if fallback:
        return fallback.rstrip(".!?") + "."

    if context.description:
        description = clean_homepage_description(context.description)
        return f"From the outside, {product_name} presents itself like this: {description.rstrip('.!?')}."

    headings = [heading for heading in (context.headings or []) if heading.lower() != product_name.lower()]
    if headings:
        return f"The homepage points at {', '.join(headings[:3]).rstrip('.')}."

    return f"The homepage gives the main product story, but the surrounding profile pages add useful context."


def yaml_string(value: str) -> str:
    if re.search(r"[:#>{}\\[\\],&*]|^\\s|\\s$", value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", normalized).strip("-")
    return slug or "profile-footprint"


def hostname(url: str) -> str:
    return (urlparse(ensure_url(url)).hostname or "").lower()


def link_label(url: str, founder_name: str) -> str:
    host = hostname(url)
    if host.endswith("figma.com"):
        return "Figma community file"
    if host == "cal.com":
        return "Cal.com page"
    if host == "topmate.io":
        return "Topmate profile"
    if host == "webflow.com":
        return "Webflow showcase page"
    if host == "linktr.ee":
        return f"{founder_name}'s Linktree"
    return host.removeprefix("www.")


def markdown_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def markdown_link_with_article(label: str, url: str) -> str:
    article = "an" if label[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
    return f"{article} {markdown_link(label, url)}"


def split_links(links: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "showcase": [],
        "contact": [],
        "hub": [],
        "other": [],
    }
    for link in links:
        host = hostname(link)
        if host.endswith("figma.com") or host == "webflow.com":
            groups["showcase"].append(link)
        elif host in {"cal.com", "topmate.io"}:
            groups["contact"].append(link)
        elif host in {"linktr.ee", "bio.link", "beacons.ai"}:
            groups["hub"].append(link)
        else:
            groups["other"].append(link)
    return groups


def sentence_list(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def render_link_paragraphs(founder_name: str, product_name: str, links: list[str]) -> list[str]:
    groups = split_links(links)
    paragraphs = []

    showcase_links = [markdown_link(link_label(link, founder_name), link) for link in groups["showcase"]]
    if showcase_links:
        verb = "give" if len(showcase_links) > 1 else "gives"
        paragraphs.append(
            f"The {sentence_list(showcase_links)} {verb} another angle on the product work: "
            "how it is presented, designed, or packaged outside the main homepage."
        )

    contact_links = [markdown_link_with_article(link_label(link, founder_name), link) for link in groups["contact"]]
    if contact_links:
        verb = "give" if len(contact_links) > 1 else "gives"
        paragraphs.append(
            f"For direct contact, scheduling and expert-profile pages are still surprisingly practical. "
            f"{product_name} has {sentence_list(contact_links)}, which {verb} someone a lightweight path "
            f"to reach out or learn more from the founder."
        )

    hub_links = [markdown_link(link_label(link, founder_name), link) for link in groups["hub"]]
    if hub_links:
        paragraphs.append(
            f"The compact version of this is a link hub. {sentence_list(hub_links)} gathers the important "
            "public links in one place, which is often enough when someone just wants the shortest path "
            "to the relevant profiles."
        )

    other_links = [markdown_link(link_label(link, founder_name), link) for link in groups["other"]]
    if other_links:
        paragraphs.append(
            f"I also found {sentence_list(other_links)} while following the public footprint around "
            f"{product_name}."
        )

    return paragraphs


def render_post(
    founder_name: str,
    product_name: str,
    website: str,
    links: list[str],
    context: WebsiteContext,
    offering: str | None,
    now: dt.datetime,
) -> tuple[str, str]:
    title = f"{founder_name} and the public footprint around {product_name}"
    paragraphs = [
        "I like looking at the small public trail around indie products. The homepage tells you the main story, "
        "but the surrounding profile pages often show how the founder thinks about the product, which communities "
        "they care about, and where someone can actually reach them.",
        f"One example I came across is {founder_name} and {markdown_link(product_name, website)}. "
        f"{offering_sentence(product_name, context, offering)} "
        "That is the kind of product surface area where the public profile pages around it become useful context.",
        *render_link_paragraphs(founder_name, product_name, links),
        f"None of this replaces a real homepage, of course. But when I research small products, I usually check "
        f"these secondary pages as well. For a product like {product_name}, the surrounding footprint helps me "
        "understand how the founder packages the same idea across different places.",
    ]

    frontmatter = "\n".join([
        "---",
        f"title: {yaml_string(title)}",
        f"date: {now:%Y-%m-%d %H:%M:%S}",
        "tags:",
        "---",
    ]) + "\n\n"
    content = frontmatter + "\n\n".join(paragraphs) + "\n"
    return title, content


def add_nofollow_exclusions(config_path: Path, urls: list[str]) -> list[str]:
    hosts = []
    for url in urls:
        host = hostname(url)
        if host and host not in hosts:
            hosts.append(host)

    if not hosts:
        return []

    lines = config_path.read_text().splitlines()
    existing = set()
    exclude_line = None
    last_list_line = None

    for index, line in enumerate(lines):
        if re.match(r"\s*exclude:\s*$", line):
            exclude_line = index
            continue
        if exclude_line is not None:
            if re.match(r"\s*-\s+", line):
                value = line.split("-", 1)[1].strip()
                existing.add(value)
                last_list_line = index
            elif line.strip() and not line.startswith((" ", "\t")):
                break

    if exclude_line is None:
        raise RuntimeError("Could not find nofollow.exclude in _config.yml")

    missing = [host for host in hosts if host not in existing]
    if not missing:
        return []

    insert_at = (last_list_line + 1) if last_list_line is not None else (exclude_line + 1)
    for offset, host in enumerate(missing):
        lines.insert(insert_at + offset, f"    - {host}")

    config_path.write_text("\n".join(lines) + "\n")
    return missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--founder-name", required=True)
    parser.add_argument("--website", required=True)
    parser.add_argument("--link", action="append", default=[], help="Resource/profile URL. Repeat for multiple links.")
    parser.add_argument("--product-name", help="Override product name inferred from the homepage.")
    parser.add_argument("--offering", help="Override homepage-derived offering sentence.")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--date", help="Post date as 'YYYY-MM-DD HH:MM:SS'. Defaults to now.")
    parser.add_argument("--slug", help="Override output file slug.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing post with the same slug.")
    parser.add_argument("--dry-run", action="store_true", help="Print the post instead of writing files.")
    parser.add_argument("--no-update-config", action="store_true", help="Do not update nofollow.exclude.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    website = ensure_url(args.website)
    links = [ensure_url(link) for link in args.link]

    try:
        context = fetch_context(website, args.timeout)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        if not args.offering and not args.product_name:
            print(f"Could not fetch {website}: {exc}", file=sys.stderr)
            print("Pass --product-name and --offering to generate without homepage research.", file=sys.stderr)
            return 1
        context = WebsiteContext()

    product_name = args.product_name or infer_product_name(website, context)
    now = (
        dt.datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S")
        if args.date
        else dt.datetime.now().replace(microsecond=0)
    )
    title, content = render_post(
        founder_name=args.founder_name,
        product_name=product_name,
        website=website,
        links=links,
        context=context,
        offering=args.offering,
        now=now,
    )

    slug = args.slug or slugify(title)
    output_path = POSTS_DIR / f"{slug}.md"

    if args.dry_run:
        print(content)
        return 0

    if output_path.exists() and not args.force:
        print(f"Post already exists: {output_path}. Use --force to overwrite.", file=sys.stderr)
        return 1

    output_path.write_text(content)
    print(f"Wrote {output_path}")

    if not args.no_update_config:
        added = add_nofollow_exclusions(CONFIG_PATH, [website, *links])
        if added:
            print("Added nofollow exclusions: " + ", ".join(added))
        else:
            print("No new nofollow exclusions needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
