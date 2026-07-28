#!/usr/bin/env python3
"""
llms.txt validator and generator.

The llms.txt standard (llmstxt.org) helps AI crawlers understand site structure.

Usage:
    python3 llmstxt_generator.py <url> --validate   # Check existing llms.txt
    python3 llmstxt_generator.py <url> --generate    # Generate from site crawl

Ported from geo-seo-claude (MIT License).
"""

import sys
import json
import re
import argparse
from urllib.parse import urlparse, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4 requests lxml")
    sys.exit(1)

HEADERS = {"User-Agent": "GEO-SEO-Audit/1.0"}
TIMEOUT = 30


def validate_llmstxt(url: str) -> dict:
    """Fetch and validate /llms.txt against the spec."""
    parsed = urlparse(url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"

    try:
        resp = requests.get(llms_url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return {
                "url": llms_url,
                "exists": False,
                "status_code": resp.status_code,
                "score": 0,
                "issues": ["No llms.txt file found at site root"],
                "recommendation": "Generate and deploy an llms.txt file",
            }

        text = resp.text
        issues = []
        score = 100

        # Check for title (# line)
        if not re.search(r"^#\s+.+", text, re.MULTILINE):
            issues.append("Missing title line (# Title)")
            score -= 20

        # Check for description (> line)
        if not re.search(r"^>\s+.+", text, re.MULTILINE):
            issues.append("Missing description line (> description)")
            score -= 15

        # Check for sections (## lines)
        sections = re.findall(r"^##\s+(.+)", text, re.MULTILINE)
        if not sections:
            issues.append("No sections found (## Section Name)")
            score -= 20

        # Check for links (- [text](url))
        links = re.findall(r"^-\s+\[.+?\]\(.+?\)", text, re.MULTILINE)
        if not links:
            issues.append("No linked resources found (- [text](url))")
            score -= 20

        # Check content length
        if len(text) < 100:
            issues.append("Content is very short — consider adding more sections")
            score -= 10

        # Validate link URLs
        broken_links = []
        for link_match in re.finditer(r"\[.+?\]\((.+?)\)", text):
            link_url = link_match.group(1)
            if not link_url.startswith("http"):
                link_url = urljoin(url, link_url)
            try:
                link_resp = requests.head(link_url, headers=HEADERS, timeout=10, allow_redirects=True)
                if link_resp.status_code >= 400:
                    broken_links.append({"url": link_url, "status": link_resp.status_code})
            except Exception:
                broken_links.append({"url": link_url, "status": "timeout"})

        if broken_links:
            issues.append(f"{len(broken_links)} broken link(s) in llms.txt")
            score -= len(broken_links) * 5

        return {
            "url": llms_url,
            "exists": True,
            "score": max(0, score),
            "sections": sections,
            "link_count": len(links),
            "broken_links": broken_links,
            "issues": issues,
            "content_preview": text[:500],
        }

    except Exception as e:
        return {"url": llms_url, "error": str(e)}


def generate_llmstxt(url: str) -> dict:
    """Generate an llms.txt file by crawling the site."""
    parsed = urlparse(url)
    _ = f"{parsed.scheme}://{parsed.netloc}"  # base URL for future crawl expansion

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "lxml")

    # Extract site info
    title = soup.title.string.strip() if soup.title and soup.title.string else parsed.netloc
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    # Categorize internal links
    categories = {
        "Main": [],
        "Products": [],
        "Resources": [],
        "Company": [],
        "Support": [],
        "Documentation": [],
    }

    product_patterns = re.compile(r"(?:product|feature|solution|service|pricing|plan)", re.IGNORECASE)
    resource_patterns = re.compile(r"(?:blog|resource|guide|tutorial|learn|article|news|case.?stud)", re.IGNORECASE)
    company_patterns = re.compile(r"(?:about|team|career|contact|press|partner|investor)", re.IGNORECASE)
    support_patterns = re.compile(r"(?:help|support|faq|status|community|forum)", re.IGNORECASE)
    docs_patterns = re.compile(r"(?:doc|api|reference|developer|sdk|changelog)", re.IGNORECASE)

    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
            continue

        full_url = urljoin(url, href)
        link_parsed = urlparse(full_url)
        if link_parsed.netloc != parsed.netloc:
            continue

        path = link_parsed.path.rstrip("/")
        if path in seen or not path:
            continue
        seen.add(path)

        link_text = a.get_text(strip=True) or path.split("/")[-1].replace("-", " ").title()
        entry = f"- [{link_text}]({full_url})"

        combined = f"{link_text} {path}"
        if docs_patterns.search(combined):
            categories["Documentation"].append(entry)
        elif product_patterns.search(combined):
            categories["Products"].append(entry)
        elif resource_patterns.search(combined):
            categories["Resources"].append(entry)
        elif company_patterns.search(combined):
            categories["Company"].append(entry)
        elif support_patterns.search(combined):
            categories["Support"].append(entry)
        else:
            categories["Main"].append(entry)

    # Build llms.txt
    lines = [f"# {title}"]
    if meta_desc:
        lines.append(f"\n> {meta_desc}")
    lines.append("")

    for section, entries in categories.items():
        if entries:
            lines.append(f"## {section}\n")
            for entry in entries[:15]:
                lines.append(entry)
            lines.append("")

    content = "\n".join(lines)

    return {
        "generated_content": content,
        "sections": {k: len(v) for k, v in categories.items() if v},
        "total_links": sum(len(v) for v in categories.values()),
    }


def main():
    parser = argparse.ArgumentParser(description="llms.txt validator and generator")
    parser.add_argument("url", help="Website URL")
    parser.add_argument("--validate", action="store_true", help="Validate existing llms.txt")
    parser.add_argument("--generate", action="store_true", help="Generate new llms.txt")
    args = parser.parse_args()

    url = args.url if args.url.startswith("http") else f"https://{args.url}"

    if args.validate:
        result = validate_llmstxt(url)
    elif args.generate:
        result = generate_llmstxt(url)
    else:
        # Default: validate first, suggest generation if missing
        result = validate_llmstxt(url)
        if not result.get("exists"):
            result["suggestion"] = "Run with --generate to create one"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
