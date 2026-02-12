# TikTok Skills

Agent skills for TikTok data scraping and automation.

## Available Skills

### tiktok-collection-scraper

Scrape all collection folders and videos for any TikTok user. Zero external API dependency.

**Install:**
```bash
npx skills add yulin7645/tiktok-skills
```

**Features:**
- 7 input formats: username, @username, profile URL, video URL, short link, user_id, secUid
- Guest mode (no cookie needed, ~80% coverage) or login mode (100%)
- Outputs full JSON with video metadata (plays, likes, comments, shares)
- Only dependency: `curl_cffi`

## License

MIT
