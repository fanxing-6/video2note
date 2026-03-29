#!/usr/bin/env python3
"""Resolve TikTok/Douyin media links through dlpanda HTML parsing."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


BASE_URL = "https://dlpanda.com/"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def normalize_url(url: str) -> str:
    url = html.unescape(url)
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return urllib.parse.urljoin(BASE_URL, url)
    return url


def extract_first(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return match.group(1)


def extract_token(home_html: str) -> str:
    token = extract_first(r'name="t0ken"[^>]*value="([^"]+)"', home_html)
    if not token:
        raise RuntimeError("Failed to extract dlpanda token from homepage HTML.")
    return token


def resolve_via_dlpanda(target_url: str) -> dict[str, str | None]:
    home_html = fetch_text(BASE_URL)
    token = extract_token(home_html)

    query = urllib.parse.urlencode({"url": target_url, "t0ken": token})
    result_url = f"{BASE_URL}?{query}"
    result_html = fetch_text(result_url)

    video_url = extract_first(r'<source\s+src="([^"]+)"\s+type="video/mp4">', result_html)
    if not video_url:
        video_url = extract_first(r"downVideo\('([^']+?is_play_url=1[^']*)'", result_html)

    audio_url = extract_first(r"downVideo\('([^']+?\.mp3[^']*)'", result_html)
    proxy_url = extract_first(r"downVideo2\('([^']+)'", result_html)
    filename = extract_first(r'download="([^"]+\.mp4)"', result_html)

    return {
        "input_url": target_url,
        "token": token,
        "result_url": result_url,
        "video_url": normalize_url(video_url) if video_url else None,
        "audio_url": normalize_url(audio_url) if audio_url else None,
        "proxy_url": normalize_url(proxy_url) if proxy_url else None,
        "filename": html.unescape(filename) if filename else None,
        "result_html": result_html,
    }


def download_file(url: str, output_path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        output_path.write_bytes(response.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="TikTok or Douyin share/canonical URL")
    parser.add_argument("--save-html", help="Path to save the resolved dlpanda result HTML")
    parser.add_argument("--download-video", help="Path to download the resolved direct MP4")
    args = parser.parse_args()

    result = resolve_via_dlpanda(args.url)

    if args.save_html:
        Path(args.save_html).write_text(str(result["result_html"]), encoding="utf-8")

    if args.download_video:
        if not result["video_url"]:
            raise RuntimeError("No direct video URL was extracted from dlpanda HTML.")
        download_file(str(result["video_url"]), Path(args.download_video))

    result.pop("result_html", None)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
