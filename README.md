<h1 align="center">🎵 TikTok Skills</h1>

<p align="center">
  Agent skills for TikTok data extraction. Zero external API dependency.
</p>

<p align="center">
  <a href="https://skills.sh/yulin7645/tiktok-skills/tiktok-collection-scraper">
    <img src="https://img.shields.io/badge/skills.sh-listed-blue?style=flat-square" alt="skills.sh" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License: MIT" />
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome" />
  </a>
</p>

---

## Install

```bash
npx skills add yulin7645/tiktok-skills
```

Works with **39 agents** including Claude Code, OpenClaw, Cursor, Copilot, Windsurf, Cline, Codex, Gemini CLI, and more.

## Available Skills

| Skill | Description |
|-------|-------------|
| [tiktok-collection-scraper](tiktok-collection-scraper/) | Scrape all collection folders and videos for any TikTok user with full metadata |

## tiktok-collection-scraper

Batch extract TikTok user collection folders and their video links — including play counts, likes, comments, and shares.

### Features

- 🔓 **No login required** — works without cookies for public collections (~80% coverage)
- 🔑 **Full access with cookie** — get all collections including private ones (100%)
- 🚀 **Zero external API** — only needs `curl_cffi`, no TikHub/RapidAPI/paid services
- 📥 **7 input formats** — username, @username, profile URL, video URL, short link, user_id, secUid
- 📊 **Rich metadata** — plays, likes, comments, shares per video
- ⚡ **Fast** — 50 collections + 300 videos in ~40 seconds

### Quick Start

```bash
# Install dependency
pip install curl_cffi

# Scrape by username (guest mode, no cookie needed)
python3 scripts/scrape_collections.py chengfeng_yulin -o result.json

# Scrape with cookie (full access)
python3 scripts/scrape_collections.py chengfeng_yulin --cookie cookie.txt -o result.json
```

### Supported Input Formats

| Format | Example |
|--------|---------|
| Username | `chengfeng_yulin` |
| @Username | `@chengfeng_yulin` |
| Profile URL | `https://www.tiktok.com/@chengfeng_yulin` |
| Video URL | `https://www.tiktok.com/@user/video/7602514407133941000` |
| Short link | `https://vm.tiktok.com/ZMkVKQxsb/` |
| User ID | `6811802142106764293` |
| secUid | `MS4wLjABAAAA...` |

### Output

```json
{
  "totalCollections": 50,
  "totalVideos": 308,
  "collections": [
    {
      "name": "收藏夹名称",
      "items": [
        {
          "id": "7602514407133941000",
          "url": "https://www.tiktok.com/@author/video/7602514407133941000",
          "desc": "Video description...",
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

### How It Works

Under the hood, the skill uses TikTok's internal web APIs with `curl_cffi` for Chrome TLS fingerprint impersonation:

1. **Resolve user** — any input format → `secUid` (via TikTok's own redirects and page parsing)
2. **Fetch collections** — `GET /api/user/collection_list/` (no auth needed)
3. **Fetch videos** — `GET /api/collection/item_list/` with `sourceType=113` (the undocumented key parameter)

> `sourceType=113` is an undocumented parameter discovered through browser request interception. Without it, the API returns success with empty results.

## Contributing

PRs welcome! If you've built a TikTok-related skill or found improvements, open a pull request.

## License

[MIT](LICENSE)
