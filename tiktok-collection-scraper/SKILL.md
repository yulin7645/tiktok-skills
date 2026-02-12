---
name: tiktok-collection-scraper
description: Scrape TikTok user collection folders and their video links with metadata (plays, likes, comments, shares). Use when user asks to get/scrape/fetch/extract TikTok collections, favorites, saved videos, or collection folder contents for any TikTok account. Supports any user identifier — username, @username, profile URL, video URL, short link (vm.tiktok.com), user_id, or secUid. Zero external API dependency, only requires curl_cffi.
---

# TikTok Collection Scraper

Scrape all collection folders and videos for any TikTok user using `curl_cffi` only. No external APIs, no login cookie required for public collections.

## Prerequisites

Ensure `curl_cffi` is installed:

```bash
pip install curl_cffi
```

## Quick Start

Run the bundled script. All paths below are relative to this skill's directory.

```bash
# Guest mode (public collections, ~80% coverage)
python3 scripts/scrape_collections.py <target> -o /tmp/result.json

# Login mode (all collections, 100% coverage)
python3 scripts/scrape_collections.py <target> --cookie /path/to/cookie.txt -o /tmp/result.json
```

`<target>` accepts any of:
- `chengfeng_yulin` — username
- `@chengfeng_yulin` — @username
- `https://www.tiktok.com/@user` — profile URL
- `https://www.tiktok.com/@user/video/123` — video URL (resolves to video author)
- `https://vm.tiktok.com/xxx` — short link
- `6811802142106764293` — user_id (numeric, >10 digits)
- `MS4wLjABAAAA...` — secUid direct

## Output Format

JSON with structure:

```json
{
  "target": "chengfeng_yulin",
  "secUid": "MS4wLjAB...",
  "uid": "68118...",
  "uniqueId": "chengfeng_yulin",
  "mode": "guest",
  "totalCollections": 50,
  "totalVideos": 308,
  "elapsedSeconds": 40.0,
  "collections": [
    {
      "collectionId": "760379...",
      "name": "收藏夹名称",
      "expected": 3,
      "actual": 3,
      "items": [
        {
          "id": "760251...",
          "url": "https://www.tiktok.com/@author/video/760251...",
          "desc": "Video description...",
          "author": "author_username",
          "plays": 2000000,
          "likes": 25100,
          "comments": 632,
          "shares": 85000
        }
      ]
    }
  ]
}
```

## Cookie

- **Not needed** for public collections (status=3, typically ~50% of folders, ~80% of videos)
- **Needed** for private collections (status=1) — must be the target account's own login cookie
- Cookie format: raw cookie string from browser (semicolon-separated key=value pairs)

## Key Technical Details

See `references/api-notes.md` for full API documentation. Critical points:

- `sourceType=113` is the essential undocumented parameter for `item_list` API
- `curl_cffi` with `impersonate='chrome'` bypasses TikTok's TLS fingerprint detection
- Status field is counter-intuitive: `status=3` = public, `status=1` = private

## Error Handling

- `⚠️` = fewer videos than expected (likely deleted videos)
- `❌` = zero videos returned (video removed or API issue)
- Script retries failed requests up to 3 times with 5s backoff
- Progress is printed to stderr; JSON output goes to stdout (or file with `-o`)
