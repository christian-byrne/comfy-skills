#!/usr/bin/env python3
"""
Brand Scanner — Check brand entity presence on AI-cited platforms.

Queries Wikipedia and Wikidata APIs for entity verification.
Other platforms (YouTube, Reddit, LinkedIn) produce structured check
instructions for the agent to execute via WebFetch.

Usage:
    python3 brand_scanner.py <brand_name>

Ported from geo-seo-claude (MIT License).
"""

import sys
import json
import argparse

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

TIMEOUT = 15


def check_wikipedia(brand: str) -> dict:
    """Search Wikipedia for brand entity."""
    try:
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": brand,
                "srlimit": 5,
                "format": "json",
            },
            timeout=TIMEOUT,
        )
        data = resp.json()
        results = data.get("query", {}).get("search", [])

        exact_match = None
        partial_matches = []
        for r in results:
            title = r.get("title", "")
            if title.lower() == brand.lower():
                exact_match = {
                    "title": title,
                    "snippet": r.get("snippet", ""),
                    "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                }
            else:
                partial_matches.append(title)

        return {
            "platform": "Wikipedia",
            "has_page": exact_match is not None,
            "exact_match": exact_match,
            "partial_matches": partial_matches[:3],
            "total_results": len(results),
        }
    except Exception as e:
        return {"platform": "Wikipedia", "error": str(e)}


def check_wikidata(brand: str) -> dict:
    """Search Wikidata for brand entity."""
    try:
        resp = requests.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": brand,
                "language": "en",
                "limit": 5,
                "format": "json",
            },
            timeout=TIMEOUT,
        )
        data = resp.json()
        results = data.get("search", [])

        entities = []
        for r in results:
            entities.append({
                "id": r.get("id", ""),
                "label": r.get("label", ""),
                "description": r.get("description", ""),
                "url": r.get("concepturi", ""),
            })

        return {
            "platform": "Wikidata",
            "has_entity": len(entities) > 0,
            "entities": entities[:3],
        }
    except Exception as e:
        return {"platform": "Wikidata", "error": str(e)}


def generate_check_instructions(brand: str) -> list:
    """Generate WebFetch check instructions for platforms without APIs."""
    return [
        {
            "platform": "YouTube",
            "check_url": f"https://www.youtube.com/results?search_query={brand}",
            "what_to_check": [
                "Does the brand have an official YouTube channel?",
                "How many subscribers?",
                "Are there recent videos (within 6 months)?",
                "Do third parties create content about this brand?",
            ],
        },
        {
            "platform": "Reddit",
            "check_url": f"https://www.reddit.com/search/?q={brand}",
            "what_to_check": [
                "Is there an official subreddit?",
                "How many members?",
                "Are there organic discussions mentioning the brand?",
                "What's the sentiment (positive/negative/neutral)?",
            ],
        },
        {
            "platform": "LinkedIn",
            "check_url": f"https://www.linkedin.com/company/{brand.lower().replace(' ', '-')}",
            "what_to_check": [
                "Does a company page exist?",
                "How many followers?",
                "Are there recent posts?",
                "Is the page claimed and verified?",
            ],
        },
        {
            "platform": "Crunchbase",
            "check_url": f"https://www.crunchbase.com/organization/{brand.lower().replace(' ', '-')}",
            "what_to_check": [
                "Is there a Crunchbase profile?",
                "What category is the company listed under?",
                "Is funding information available?",
            ],
        },
        {
            "platform": "G2 / Capterra",
            "check_url": f"https://www.g2.com/search?query={brand}",
            "what_to_check": [
                "Is the product listed on review sites?",
                "What's the rating?",
                "How many reviews?",
            ],
        },
    ]


def main():
    parser = argparse.ArgumentParser(description="Brand entity scanner")
    parser.add_argument("brand", help="Brand name to scan")
    args = parser.parse_args()

    brand = args.brand

    results = {
        "brand": brand,
        "api_checks": [
            check_wikipedia(brand),
            check_wikidata(brand),
        ],
        "manual_check_instructions": generate_check_instructions(brand),
    }

    # Summary
    wiki_has = results["api_checks"][0].get("has_page", False)
    wikidata_has = results["api_checks"][1].get("has_entity", False)

    results["summary"] = {
        "wikipedia_entity": wiki_has,
        "wikidata_entity": wikidata_has,
        "entity_strength": "strong" if (wiki_has and wikidata_has) else "moderate" if (wiki_has or wikidata_has) else "weak",
        "recommendation": (
            "Strong entity presence — focus on keeping Wikipedia page updated"
            if wiki_has
            else "No Wikipedia page found — consider creating one or building entity presence through third-party mentions"
        ),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
