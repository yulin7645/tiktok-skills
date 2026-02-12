# TikTok Collection API — Technical Reference

## Endpoints

### 1. Collection List

```
GET https://www.tiktok.com/api/user/collection_list/
```

Minimum params: `secUid`, `aid=1988`, `count=30`, `cursor=0`

Returns: `{collectionList, cursor, hasMore, total, status_code}`

Each collection: `{collectionId, name, total (string), status, cover, userId, userName}`

### 2. Collection Items

```
GET https://www.tiktok.com/api/collection/item_list/
```

**Critical param: `sourceType=113`** — without it, API returns empty `itemList` with `status_code=0` (looks successful but no data).

Minimum params: `collectionId`, `sourceType=113`, `aid=1988`, `count=30`, `cursor=0`, `device_platform=web_pc`, `channel=tiktok_web`

Returns: `{itemList, cursor, hasMore, statusCode, status_code}`

Each item: `{id, desc, author{uniqueId, id}, stats{playCount, diggCount, commentCount, shareCount}, video{playAddr, duration}, createTime}`

## Status Field Meaning

| status | Without Cookie | With Cookie | Meaning |
|--------|---------------|-------------|---------|
| 3 | ✅ visible + readable | ✅ visible + readable | Public collection |
| 1 | ❌ invisible | ✅ visible + readable | Private collection (owner-only) |

Counter-intuitive: status=3 is public, status=1 is private.

## User Resolution Paths

| Input | Method | API calls |
|-------|--------|-----------|
| username | GET `/@{username}` → parse HTML | 1 |
| @username | Strip `@`, same as above | 1 |
| Profile URL | Extract `@username` from path → parse | 1 |
| Video URL | Extract `@username` from path → GET profile | 1 |
| Short link | Follow 302 redirect → extract username → profile | 2 |
| user_id | GET `/share/user/{uid}` → 301 to `/@username` → profile | 2 |
| secUid | Direct use | 0 |

## Rate Limits

- Request interval: ≥300ms
- Batch pause: 1s every 10 requests
- Timeout: 15s
- Max retries: 3

## Known Issues

- `total` field in collection metadata doesn't update when videos are deleted
- Some videos return `id` as integer (JavaScript precision loss for large IDs)
- Short links may redirect to URLs with empty `@` — fall back to page parsing
