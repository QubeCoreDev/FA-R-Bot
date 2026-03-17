"""Tools for fetching and parsing content from the official FAČR website (fotbal.cz)."""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

ALLOWED_DOMAINS = {"fotbal.cz", "www.fotbal.cz", "facr.fotbal.cz"}
BASE_URL = "https://www.fotbal.cz"
REQUEST_TIMEOUT = 10.0
MAX_CONTENT_LENGTH = 8_000


def _is_allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname is not None and any(
        parsed.hostname == d or parsed.hostname.endswith(f".{d}")
        for d in ALLOWED_DOMAINS
    )


def _normalize_url(url: str) -> str:
    if url.startswith("/"):
        return urljoin(BASE_URL, url)
    if not url.startswith("http"):
        return f"{BASE_URL}/{url}"
    return url


def _clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def _extract_tables(soup: BeautifulSoup) -> list[str]:
    """Extract tables as markdown."""
    results: list[str] = []
    for table in soup.find_all("table"):
        rows: list[str] = []
        for tr in table.find_all("tr"):
            cells = []
            for td in tr.find_all(["td", "th"]):
                cell_text = td.get_text(separator=" ", strip=True)
                link = td.find("a", href=True)
                if link and link.get("href", "").startswith("mailto:"):
                    email = link["href"].replace("mailto:", "").strip()
                    if email not in cell_text:
                        cell_text = f"{cell_text} ({email})"
                cells.append(cell_text)
            if any(c for c in cells):
                rows.append("| " + " | ".join(cells) + " |")
        if rows:
            results.append("\n".join(rows))
    return results


def _extract_main_content(soup: BeautifulSoup) -> str:
    """Extract main readable content from an HTML page."""
    for tag in soup.find_all(["script", "style", "nav", "footer", "noscript", "iframe"]):
        tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.find(class_=re.compile(r"content|article|main"))

    target: Tag | BeautifulSoup = main if isinstance(main, Tag) else soup

    parts: list[str] = []

    title_tag = soup.find("title")
    if title_tag:
        parts.append(f"# {title_tag.get_text(strip=True)}\n")

    tables = _extract_tables(target)
    if tables:
        parts.append("\n\n---\n\n".join(tables))

    for element in target.find_all(["h1", "h2", "h3", "h4", "p", "li", "dt", "dd"]):
        tag_name = element.name
        text = element.get_text(separator=" ", strip=True)
        if not text:
            continue

        if tag_name == "h1":
            parts.append(f"\n# {text}")
        elif tag_name == "h2":
            parts.append(f"\n## {text}")
        elif tag_name == "h3":
            parts.append(f"\n### {text}")
        elif tag_name == "h4":
            parts.append(f"\n#### {text}")
        elif tag_name == "li":
            parts.append(f"- {text}")
        else:
            parts.append(text)

    content = _clean_text("\n".join(parts))
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n\n[… obsah zkrácen]"
    return content


async def fetch_facr_page(url: str) -> dict[str, Any]:
    """Fetch a page from fotbal.cz and return parsed content."""
    url = _normalize_url(url)

    if not _is_allowed_url(url):
        return {"error": f"URL '{url}' není na doméně fotbal.cz. Mohu přistupovat pouze na stránky FAČR."}

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "FACR-Lvicek-Bot/1.0 (AI assistant)"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return {"error": f"Stránka vrátila chybu {exc.response.status_code}: {url}"}
    except httpx.RequestError as exc:
        return {"error": f"Nepodařilo se načíst stránku: {exc}"}

    soup = BeautifulSoup(response.text, "html.parser")
    content = _extract_main_content(soup)

    links: list[str] = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        text = a_tag.get_text(strip=True)
        if text and href.startswith("/") and len(text) > 3:
            full_url = urljoin(BASE_URL, href)
            links.append(f"- [{text}]({full_url})")
    links_section = "\n".join(links[:15]) if links else ""

    return {
        "url": url,
        "content": content,
        "related_links": links_section,
    }


async def search_facr_web(query: str) -> dict[str, Any]:
    """Search fotbal.cz using site-restricted Google search or direct navigation."""
    search_paths = [
        f"/facr/pravni-servis/predpisy/soubor-predpisu",
        f"/facr/kontakty/p68",
        f"/facr/organizacni-struktura-a-organy-facr",
    ]

    common_pages: dict[str, str] = {
        "kontakt": "/facr/kontakty/p68",
        "kontakty": "/facr/kontakty/p68",
        "telefon": "/facr/kontakty/p68",
        "email": "/facr/kontakty/p68",
        "předpisy": "/facr/pravni-servis/predpisy/soubor-predpisu",
        "predpisy": "/facr/pravni-servis/predpisy/soubor-predpisu",
        "stanovy": "/facr/pravni-servis/predpisy/soubor-predpisu",
        "struktura": "/facr/organizacni-struktura-a-organy-facr",
        "organizační": "/facr/organizacni-struktura-a-organy-facr",
        "výkonný výbor": "/facr/organizacni-struktura-a-organy-facr/vykonny-vybor",
        "předseda": "/facr/organizacni-struktura-a-organy-facr/predseda",
        "komise": "/facr/organizacni-struktura-a-organy-facr/komise-a-pracovni-skupiny",
        "reprezentace": "/reprezentace",
        "soutěže": "/souteze",
        "mládež": "/nas-fotbal",
        "ženský fotbal": "/zeny",
        "ženy": "/zeny",
        "futsal": "/futsal",
        "aktuality": "/aktuality",
        "integrity": "/facr/integrity/uvod",
        "gdpr": "/facr/pravni-servis/gdpr/zasady-ochrany-osobnich-udaju",
        "přestupy": "/facr/pravni-servis/prestupy",
        "whistleblowing": "/facr/pravni-servis/whistleblowing",
        "výroční zprávy": "/facr/zverejnovane-dokumenty/vyrocni-zpravy",
        "rozpočet": "/facr/zverejnovane-dokumenty/rozpocet",
        "dotace": "/facr/zverejnovane-dokumenty/dotace",
        "mapa klubů": "/facr/mapa-klubu",
        "vstupenky": "/fanousek",
        "ticketing": "/fanousek",
    }

    query_lower = query.lower()
    matched_path: str | None = None
    for keyword, path in common_pages.items():
        if keyword in query_lower:
            matched_path = path
            break

    if matched_path:
        return await fetch_facr_page(matched_path)

    return await fetch_facr_page(f"/facr/kontakty/p68")
