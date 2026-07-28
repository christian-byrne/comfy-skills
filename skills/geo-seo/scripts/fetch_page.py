#!/usr/bin/env python3
"""
Fetch page HTML, parse robots.txt for AI crawlers, crawl sitemaps, extract metadata.

Usage:
    python3 fetch_page.py <url> [--robots] [--sitemap] [--meta] [--all]

Ported from geo-seo-claude (MIT License).
"""

import sys
import json
import re
import time
import argparse
from urllib.parse import urlparse, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4 requests lxml")
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GEO-SEO-Audit/1.0)"
}
TIMEOUT = 30

AI_CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "anthropic-ai", "PerplexityBot",
    "CCBot", "Bytespider", "cohere-ai",
    "Google-Extended", "GoogleOther",
    "Applebot-Extended", "FacebookBot", "Amazonbot",
]

CRITICAL_CRAWLERS = {"GPTBot", "ClaudeBot", "PerplexityBot", "ChatGPT-User", "Google-Extended"}


def fetch_html(url: str) -> dict:
    """Fetch a page and return parsed data."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return {
            "url": str(resp.url),
            "status_code": resp.status_code,
            "html": resp.text,
            "content_type": resp.headers.get("Content-Type", ""),
            "headers": dict(resp.headers),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


def fetch_robots_txt(url: str) -> dict:
    """Fetch and parse robots.txt for AI crawler access."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return {
                "url": robots_url,
                "status": "NO_ROBOTS_TXT",
                "crawlers": {c: "NOT_MENTIONED" for c in AI_CRAWLERS},
                "score": 90,
                "raw": "",
            }

        text = resp.text
        results = {}
        lines = text.strip().split("\n")

        for crawler in AI_CRAWLERS:
            status = "NOT_MENTIONED"
            current_agent = None

            for line in lines:
                line = line.strip()
                if line.lower().startswith("user-agent:"):
                    current_agent = line.split(":", 1)[1].strip()

                if current_agent and current_agent.lower() in (crawler.lower(), "*"):
                    if line.lower().startswith("disallow:"):
                        path = line.split(":", 1)[1].strip()
                        if path == "/" or path == "/*":
                            if current_agent.lower() == crawler.lower():
                                status = "BLOCKED"
                            elif current_agent == "*" and status == "NOT_MENTIONED":
                                status = "BLOCKED_BY_WILDCARD"
                    elif line.lower().startswith("allow:"):
                        path = line.split(":", 1)[1].strip()
                        if path == "/" or path == "/*":
                            if current_agent.lower() == crawler.lower():
                                status = "ALLOWED"

            results[crawler] = status

        # Calculate score
        score = 100
        has_sitemap = "sitemap:" in text.lower()
        if not has_sitemap:
            score -= 10

        for crawler, status in results.items():
            if status in ("BLOCKED", "BLOCKED_BY_WILDCARD"):
                if crawler in CRITICAL_CRAWLERS:
                    score -= 15
                else:
                    score -= 5

        return {
            "url": robots_url,
            "status": "FOUND",
            "crawlers": results,
            "has_sitemap_directive": has_sitemap,
            "score": max(0, score),
            "raw": text[:2000],
        }

    except Exception as e:
        return {"url": robots_url, "error": str(e), "score": 0}


def crawl_sitemap(url: str, max_pages: int = 50) -> dict:
    """Crawl sitemap.xml and extract page URLs."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    sitemap_urls_to_try = [
        f"{base}/sitemap.xml",
        f"{base}/sitemap_index.xml",
        f"{base}/sitemap.xml.gz",
    ]

    pages = []
    for sitemap_url in sitemap_urls_to_try:
        try:
            resp = requests.get(sitemap_url, headers=HEADERS, timeout=TIMEOUT)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "lxml-xml")

            # Check for sitemap index
            sitemaps = soup.find_all("sitemap")
            if sitemaps:
                for sm in sitemaps[:5]:
                    loc = sm.find("loc")
                    if loc:
                        try:
                            sub_resp = requests.get(loc.text.strip(), headers=HEADERS, timeout=TIMEOUT)
                            sub_soup = BeautifulSoup(sub_resp.text, "lxml-xml")
                            for url_tag in sub_soup.find_all("url"):
                                loc_tag = url_tag.find("loc")
                                if loc_tag and len(pages) < max_pages:
                                    pages.append(loc_tag.text.strip())
                            time.sleep(1)
                        except Exception:
                            pass

            # Direct URL entries
            for url_tag in soup.find_all("url"):
                loc = url_tag.find("loc")
                if loc and len(pages) < max_pages:
                    pages.append(loc.text.strip())

            if pages:
                break

        except Exception:
            continue

    return {
        "sitemap_found": len(pages) > 0,
        "pages_found": len(pages),
        "pages": pages[:max_pages],
    }


def extract_metadata(html: str, url: str) -> dict:
    """Extract SEO/GEO metadata from HTML."""
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    # Headings
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        if tags:
            headings[f"h{level}"] = [t.get_text(strip=True) for t in tags[:10]]

    # Word count (main content)
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    word_count = len(text.split())

    # Schema.org
    schemas = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                schemas.append(data.get("@type", "Unknown"))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        schemas.append(item.get("@type", "Unknown"))
        except (json.JSONDecodeError, TypeError):
            pass

    # Links
    internal_links = 0
    external_links = 0
    parsed_url = urlparse(url)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        link_parsed = urlparse(urljoin(url, href))
        if link_parsed.netloc == parsed_url.netloc:
            internal_links += 1
        else:
            external_links += 1

    # Images
    images_total = len(soup.find_all("img"))
    images_with_alt = len(soup.find_all("img", alt=True))

    # Open Graph
    og_tags = {}
    for meta in soup.find_all("meta", property=True):
        prop = meta.get("property", "")
        if prop.startswith("og:"):
            og_tags[prop] = meta.get("content", "")

    # SSR detection
    is_likely_csr = False
    root_divs = soup.find_all("div", id=re.compile(r"^(root|app|__next|__nuxt)$"))
    if root_divs and word_count < 200:
        for div in root_divs:
            if len(div.get_text(strip=True)) < 50:
                is_likely_csr = True

    # Security headers (from fetch)
    canonical = ""
    canon_tag = soup.find("link", rel="canonical")
    if canon_tag:
        canonical = canon_tag.get("href", "")

    return {
        "title": title,
        "meta_description": meta_desc,
        "canonical": canonical,
        "headings": headings,
        "word_count": word_count,
        "schemas": schemas,
        "internal_links": internal_links,
        "external_links": external_links,
        "images_total": images_total,
        "images_with_alt": images_with_alt,
        "images_missing_alt": images_total - images_with_alt,
        "og_tags": og_tags,
        "is_likely_csr": is_likely_csr,
    }


def main():
    parser = argparse.ArgumentParser(description="GEO-SEO page fetcher and analyzer")
    parser.add_argument("url", help="URL to analyze")
    parser.add_argument("--robots", action="store_true", help="Check robots.txt for AI crawlers")
    parser.add_argument("--sitemap", action="store_true", help="Crawl sitemap.xml")
    parser.add_argument("--meta", action="store_true", help="Extract page metadata")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    args = parser.parse_args()

    url = args.url
    if not url.startswith("http"):
        url = f"https://{url}"

    results = {"url": url}

    if args.robots or args.all:
        results["robots"] = fetch_robots_txt(url)

    if args.sitemap or args.all:
        results["sitemap"] = crawl_sitemap(url)

    if args.meta or args.all:
        page = fetch_html(url)
        if "error" not in page:
            results["metadata"] = extract_metadata(page["html"], url)
            results["status_code"] = page["status_code"]
        else:
            results["fetch_error"] = page["error"]

    if not (args.robots or args.sitemap or args.meta or args.all):
        # Default: fetch and show basic info
        page = fetch_html(url)
        if "error" not in page:
            results["metadata"] = extract_metadata(page["html"], url)
            results["status_code"] = page["status_code"]
        else:
            results["fetch_error"] = page["error"]

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
