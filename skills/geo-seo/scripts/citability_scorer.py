#!/usr/bin/env python3
"""
Citability Scorer — Analyzes content blocks for AI citation readiness.
Scores passages on how likely AI models are to cite them (0-100).

Based on research: optimal AI-cited passages are 134-167 words,
self-contained, fact-rich, and directly answer questions.

Usage:
    python3 citability_scorer.py <url>
    python3 citability_scorer.py --text "Your passage here"

Ported from geo-seo-claude (MIT License).
"""

import sys
import json
import re
import argparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install beautifulsoup4 requests lxml")
    sys.exit(1)


def score_passage(text: str, heading: str = None) -> dict:
    """Score a single passage for AI citability (0-100)."""
    words = text.split()
    word_count = len(words)
    if word_count < 10:
        return {"score": 0, "grade": "F", "reason": "Too short", "dimensions": {}}

    scores = {}

    # === 1. Answer Block Quality (30pts max) ===
    abq = 0
    definition_patterns = [
        r"\b\w+\s+is\s+(?:a|an|the)\s",
        r"\b\w+\s+refers?\s+to\s",
        r"\b\w+\s+means?\s",
        r"\b\w+\s+(?:can be |are )?defined\s+as\s",
    ]
    for p in definition_patterns:
        if re.search(p, text, re.IGNORECASE):
            abq += 15
            break

    first_60 = " ".join(words[:60])
    if any(re.search(p, first_60, re.IGNORECASE) for p in [
        r"\b(?:is|are|was|were|means?|refers?)\b", r"\d+%", r"\$[\d,]+",
        r"\d+\s+(?:million|billion|thousand)",
    ]):
        abq += 15

    if heading and heading.strip().endswith("?"):
        abq += 10

    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    short_clear = sum(1 for s in sentences if 5 <= len(s.split()) <= 25)
    if sentences:
        abq += int((short_clear / len(sentences)) * 10)

    if re.search(r"(?:according to|research shows|stud(?:y|ies) (?:show|found|indicate))", text, re.IGNORECASE):
        abq += 10

    scores["answer_block_quality"] = min(abq, 30)

    # === 2. Self-Containment (25pts max) ===
    sc = 0
    if 134 <= word_count <= 167:
        sc += 10
    elif 100 <= word_count <= 200:
        sc += 7
    elif 80 <= word_count <= 250:
        sc += 4
    elif 30 <= word_count <= 400:
        sc += 2

    pronouns = len(re.findall(
        r"\b(?:it|they|them|their|this|that|these|those|he|she|his|her)\b", text, re.IGNORECASE
    ))
    if word_count > 0:
        ratio = pronouns / word_count
        if ratio < 0.02:
            sc += 8
        elif ratio < 0.04:
            sc += 5
        elif ratio < 0.06:
            sc += 3

    proper_nouns = len(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text))
    if proper_nouns >= 3:
        sc += 7
    elif proper_nouns >= 1:
        sc += 4

    scores["self_containment"] = min(sc, 25)

    # === 3. Structural Readability (20pts max) ===
    sr = 0
    avg_sentence_len = word_count / max(len(sentences), 1)
    if 10 <= avg_sentence_len <= 20:
        sr += 10
    elif 8 <= avg_sentence_len <= 25:
        sr += 6
    elif avg_sentence_len <= 30:
        sr += 3

    if re.search(r"(?:^|\n)\s*[-•●]\s", text):
        sr += 5
    if re.search(r"(?:^|\n)\s*\d+[.)]\s", text):
        sr += 5

    if len(sentences) >= 3:
        sr += 5

    scores["structural_readability"] = min(sr, 20)

    # === 4. Statistical Density (15pts max) ===
    sd = 0
    if re.search(r"\d+%", text):
        sd += 4
    if re.search(r"\$[\d,]+", text):
        sd += 4
    if re.search(r"\b\d{4}\b", text):
        sd += 3
    if re.search(r"\d+(?:\.\d+)?\s*(?:x|times|percent|million|billion|thousand)", text, re.IGNORECASE):
        sd += 4
    if re.search(r"(?:according to|per|via|source:)\s", text, re.IGNORECASE):
        sd += 4

    scores["statistical_density"] = min(sd, 15)

    # === 5. Uniqueness Signals (10pts max) ===
    us = 0
    if re.search(r"\b(?:our|my)\s+(?:research|data|analysis|study|findings)\b", text, re.IGNORECASE):
        us += 4
    if re.search(r"\b(?:we found|we discovered|our team)\b", text, re.IGNORECASE):
        us += 3
    if re.search(r"\b(?:case study|real-world|first-hand)\b", text, re.IGNORECASE):
        us += 3
    if re.search(r"\b(?:proprietary|exclusive|original)\b", text, re.IGNORECASE):
        us += 3

    scores["uniqueness_signals"] = min(us, 10)

    total = sum(scores.values())
    if total >= 80:
        grade = "A"
    elif total >= 65:
        grade = "B"
    elif total >= 50:
        grade = "C"
    elif total >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": total,
        "grade": grade,
        "word_count": word_count,
        "dimensions": scores,
    }


def analyze_url(url: str) -> dict:
    """Fetch a URL and score all content blocks."""
    try:
        resp = requests.get(url, headers={"User-Agent": "GEO-SEO-Audit/1.0"}, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    blocks = []
    current_heading = None

    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "div", "section", "article"]):
        if element.name in ("h1", "h2", "h3", "h4"):
            current_heading = element.get_text(strip=True)
            continue

        text = element.get_text(separator=" ", strip=True)
        if len(text.split()) < 20:
            continue

        result = score_passage(text, current_heading)
        result["heading"] = current_heading
        result["text_preview"] = text[:200] + "..." if len(text) > 200 else text
        blocks.append(result)

    # Sort by score descending
    blocks.sort(key=lambda x: x["score"], reverse=True)

    # Calculate averages
    if blocks:
        avg_score = sum(b["score"] for b in blocks) / len(blocks)
        high_citability = sum(1 for b in blocks if b["score"] >= 80)
        low_citability = sum(1 for b in blocks if b["score"] < 35)
    else:
        avg_score = 0
        high_citability = 0
        low_citability = 0

    return {
        "url": url,
        "total_blocks": len(blocks),
        "average_score": round(avg_score, 1),
        "high_citability_blocks": high_citability,
        "low_citability_blocks": low_citability,
        "top_blocks": blocks[:5],
        "worst_blocks": blocks[-3:] if len(blocks) >= 3 else [],
    }


def main():
    parser = argparse.ArgumentParser(description="AI Citability Scorer")
    parser.add_argument("url", nargs="?", help="URL to analyze")
    parser.add_argument("--text", help="Score a single text passage")
    args = parser.parse_args()

    if args.text:
        result = score_passage(args.text)
        print(json.dumps(result, indent=2))
    elif args.url:
        url = args.url if args.url.startswith("http") else f"https://{args.url}"
        result = analyze_url(url)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: citability_scorer.py <url> or --text 'passage'")
        sys.exit(1)


if __name__ == "__main__":
    main()
