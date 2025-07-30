import csv
import json
import sqlite3
from pathlib import Path

from urllib.parse import urlparse

import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("Missing dependency: beautifulsoup4. Run `pip install beautifulsoup4`.")


def remove_boilerplate_prefix(pages, delimiter: str):
    """
    For each PageData-like object, removes everything before and including the first occurrence
    of the delimiter in text_content. Returns a new list of modified objects.
    """
    cleaned_pages = []
    for page in pages:
        text = page.text_content
        index = text.find(delimiter)
        if index != -1:
            new_text = text[index + len(delimiter):]
        else:
            new_text = text  # leave unchanged if delimiter not found

        cleaned_page = page.__class__(
            id=page.id,
            url=page.url,
            domain=page.domain,
            timestamp=page.timestamp,
            bulk_search_id=page.bulk_search_id,
            api_key_used=page.api_key_used,
            search_type=page.search_type,
            text_content=new_text,
            html_content=page.html_content,
            internal_links=page.internal_links,
            external_links=page.external_links,
            latency_ms=page.latency_ms,
            complete=page.complete,
            created_at=page.created_at
        )
        cleaned_pages.append(cleaned_page)

    return cleaned_pages


def remove_boilerplate_suffix(pages, delimiter: str):
    """
    For each PageData-like object, removes everything at and after the first occurrence
    of the delimiter in text_content. Returns a new list of modified objects.
    """
    cleaned_pages = []
    for page in pages:
        text = page.text_content
        index = text.find(delimiter)
        if index != -1:
            new_text = text[:index]
        else:
            new_text = text  # leave unchanged if delimiter not found

        cleaned_page = page.__class__(
            id=page.id,
            url=page.url,
            domain=page.domain,
            timestamp=page.timestamp,
            bulk_search_id=page.bulk_search_id,
            api_key_used=page.api_key_used,
            search_type=page.search_type,
            text_content=new_text,
            html_content=page.html_content,
            internal_links=page.internal_links,
            external_links=page.external_links,
            latency_ms=page.latency_ms,
            complete=page.complete,
            created_at=page.created_at
        )
        cleaned_pages.append(cleaned_page)

    return cleaned_pages


def remove_duplicate_pages(pages):
    """
    Removes duplicate PageData-like objects based on identical text_content.
    Keeps only the first occurrence of each unique text.
    """
    seen = set()
    unique_pages = []
    for page in pages:
        if page.text_content not in seen:
            seen.add(page.text_content)
            unique_pages.append(page)
    return unique_pages


def save_to_csv(pages, filepath: str, mode: str = "w"):
    """
    Saves a list of PageData-like objects to a CSV file.

    Args:
        pages: List of PageData-like objects.
        filepath (str): Destination path for the CSV file.
        mode (str): "w" to overwrite or "a" to append. Default is "w".
    """
    if mode not in {"w", "a"}:
        raise ValueError("mode must be 'w' or 'a'")

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    file_exists = Path(filepath).exists()

    with open(filepath, mode=mode, newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        if mode == "w" or not file_exists:
            writer.writerow([
                "url",
                "domain",
                "timestamp",
                "bulk_search_id",
                "search_type",
                "latency_ms",
                "depth",
                "text_content"
            ])

        for page in pages:
            writer.writerow([
                getattr(page, "url", ""),
                getattr(page, "domain", ""),
                getattr(page, "timestamp", ""),
                getattr(page, "bulk_search_id", ""),
                getattr(page, "search_type", ""),
                getattr(page, "latency_ms", ""),
                getattr(page, "depth", ""),
                page.text_content.replace("\n", " ").strip()
            ])


def save_to_json(pages, filepath: str, mode: str = "w"):
    """
    Saves a list of PageData-like objects to a JSON file.

    Args:
        pages: List of PageData-like objects.
        filepath (str): Destination path for the JSON file.
        mode (str): "w" to overwrite or "a" to append. Default is "w".
    """
    if mode not in {"w", "a"}:
        raise ValueError("mode must be 'w' or 'a'")

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    new_data = []
    for page in pages:
        new_data.append({
            "url": getattr(page, "url", ""),
            "domain": getattr(page, "domain", ""),
            "timestamp": getattr(page, "timestamp", ""),
            "bulk_search_id": getattr(page, "bulk_search_id", ""),
            "search_type": getattr(page, "search_type", ""),
            "latency_ms": getattr(page, "latency_ms", ""),
            "depth": getattr(page, "depth", ""),
            "text_content": page.text_content.strip()
        })

    if mode == "w" or not Path(filepath).exists():
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
    else:
        with open(filepath, "r+", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    raise ValueError("Existing JSON must be a list.")
            except json.JSONDecodeError:
                existing_data = []

            combined = existing_data + new_data
            f.seek(0)
            json.dump(combined, f, ensure_ascii=False, indent=2)
            f.truncate()


def save_to_sqlite(pages, db_path: str, table_name: str = "pages", append: bool = True):
    """
    Saves a list of PageData-like objects into an SQLite database.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if not append:
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            url TEXT PRIMARY KEY,
            domain TEXT,
            timestamp TEXT,
            bulk_search_id TEXT,
            search_type TEXT,
            latency_ms INTEGER,
            depth INTEGER,
            text_content TEXT
        )
    """)

    for page in pages:
        cur.execute(f"""
            INSERT OR REPLACE INTO {table_name} (
                url, domain, timestamp, bulk_search_id,
                search_type, latency_ms, depth, text_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            getattr(page, "url", ""),
            getattr(page, "domain", ""),
            getattr(page, "timestamp", ""),
            getattr(page, "bulk_search_id", ""),
            getattr(page, "search_type", ""),
            getattr(page, "latency_ms", None),
            getattr(page, "depth", None),
            page.text_content.strip()
        ))

    conn.commit()
    conn.close()


def filter_by_url_substring(pages, substring: str):
    """
    Filters a list of PageData-like objects, keeping only those whose URL contains the given substring.

    Args:
        pages: List of PageData-like objects.
        substring (str): Substring to match in the URL.

    Returns:
        List of filtered PageData-like objects.
    """
    return [page for page in pages if substring in getattr(page, "url", "")]


def extract_link_graph(pages, include_external_links: bool = False, only_include_crawled_pages: bool = False):
    """
    Extracts (source_url, destination_url) edges from PageData-like objects.

    Args:
        pages: List of PageData-like objects with .internal_links populated.
        include_external_links (bool): If False, skips links to other domains.
        only_include_crawled_pages (bool): If True, restricts to known crawled URLs only.

    Returns:
        List[Tuple[str, str]]: Directed (source → destination) link edges.
    """
    edges = []
    crawled_urls = {getattr(page, "url", "") for page in pages}

    for page in pages:
        source_url = getattr(page, "url", "")
        source_domain = urlparse(source_url).netloc
        links = getattr(page, "internal_links", [])

        for link in links:
            if not link:
                continue

            dest_domain = urlparse(link).netloc

            if not include_external_links and dest_domain != source_domain:
                continue

            if only_include_crawled_pages and link not in crawled_urls:
                continue

            edges.append((source_url, link))

    return edges


def compute_text_stats(page):
    """
    Computes basic text and link stats from a PageData-like object.

    Returns:
        Dict with:
            - url
            - word_count
            - sentence_count
            - unique_word_ratio
            - link_density
    """
    text = getattr(page, "text_content", "") or ""
    html = getattr(page, "html_content", "") or ""

    word_list = re.findall(r'\b\w+\b', text.lower())
    word_count = len(word_list)
    sentence_count = len(re.findall(r'[.!?]', text))
    unique_words = set(word_list)
    unique_word_ratio = len(unique_words) / word_count if word_count else 0

    return {
        "url": getattr(page, "url", ""),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "unique_word_ratio": round(unique_word_ratio, 3),
    }


