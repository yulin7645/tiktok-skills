#!/usr/bin/env python3
"""
TikTok Collection Scraper v1.0

Scrape all collection folders and their videos for any TikTok user.
Zero external API dependency — only requires curl_cffi.

Usage:
    python3 scrape_collections.py <target> [--cookie <file>] [--output <file>]

    target: username | @username | profile URL | video URL | short link | user_id | secUid
"""

import argparse
import json
import re
import sys
import time
from urllib.parse import unquote

try:
    from curl_cffi import requests
except ImportError:
    print("ERROR: curl_cffi not installed. Run: pip install curl_cffi", file=sys.stderr)
    sys.exit(1)

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

RATE = {'interval': 0.3, 'batch_pause': 1.0, 'batch_size': 10, 'timeout': 15, 'retries': 3}

ITEM_PARAMS = {
    'aid': '1988', 'device_platform': 'web_pc', 'channel': 'tiktok_web',
    'sourceType': '113', 'count': '30', 'os': 'windows', 'region': 'US', 'language': 'en',
}

HEADERS = {'accept': '*/*', 'referer': 'https://www.tiktok.com/', 'user-agent': UA}


# ── User resolution ──────────────────────────────────────────

def resolve_user(target: str) -> dict:
    """Resolve any TikTok user identifier to {secUid, uid, uniqueId}."""
    target = target.strip()

    if target.startswith('MS4wLjAB'):
        return {'secUid': target, 'uid': None, 'uniqueId': None}

    if target.isdigit() and len(target) > 10:
        resp = requests.get(f'https://www.tiktok.com/share/user/{target}',
                            impersonate='chrome', timeout=RATE['timeout'], allow_redirects=False)
        m = re.search(r'@([^/?]+)', resp.headers.get('location', ''))
        if m:
            return _profile(m.group(1))
        raise ValueError(f'Cannot resolve user_id: {target}')

    if re.match(r'https?://(vm|vt)\.tiktok\.com/', target):
        resp = requests.get(target, impersonate='chrome', timeout=RATE['timeout'], allow_redirects=False)
        loc = resp.headers.get('location', '')
        m = re.search(r'@([^/?"]+)', loc)
        if m and m.group(1):
            return _profile(m.group(1))
        return _page(loc)

    if 'tiktok.com' in target:
        m = re.search(r'@([^/?"]+)', target)
        if m and m.group(1):
            return _profile(unquote(m.group(1)))
        return _page(target)

    return _profile(target.lstrip('@'))


def _profile(username: str) -> dict:
    resp = requests.get(f'https://www.tiktok.com/@{username}',
                        impersonate='chrome', timeout=RATE['timeout'])
    return _parse(resp.text, username)


def _page(url: str) -> dict:
    resp = requests.get(url, impersonate='chrome', timeout=RATE['timeout'], allow_redirects=True)
    return _parse(resp.text)


def _parse(html: str, fallback: str = None) -> dict:
    s = re.search(r'"secUid":"([^"]+)"', html)
    u = re.search(r'"user":\s*\{[^}]*"id":"(\d+)"', html)
    n = re.search(r'"uniqueId":"([^"]+)"', html)
    if not s:
        raise ValueError('Cannot extract secUid from page')
    return {'secUid': s.group(1), 'uid': u.group(1) if u else None,
            'uniqueId': n.group(1) if n else fallback}


# ── Collection list ──────────────────────────────────────────

def get_collections(sec_uid: str, cookies: dict = None) -> list:
    result = []
    cursor = 0
    while True:
        kw = {'impersonate': 'chrome', 'timeout': RATE['timeout']}
        if cookies:
            kw['cookies'] = cookies
        resp = requests.get('https://www.tiktok.com/api/user/collection_list/',
                            params={'secUid': sec_uid, 'aid': '1988', 'count': '30',
                                    'cursor': str(cursor)}, **kw)
        data = resp.json()
        result.extend(data.get('collectionList', []))
        if not data.get('hasMore') or not data.get('collectionList'):
            break
        cursor = data.get('cursor', 0)
        time.sleep(RATE['interval'])
    return result


# ── Collection items ─────────────────────────────────────────

def get_items(collection_id: str, cookies: dict = None) -> list:
    items = []
    cursor = 0
    while True:
        params = {**ITEM_PARAMS, 'collectionId': collection_id, 'cursor': str(cursor)}
        kw = {'impersonate': 'chrome', 'timeout': RATE['timeout']}
        if cookies:
            kw['cookies'] = cookies
        for attempt in range(RATE['retries']):
            try:
                resp = requests.get('https://www.tiktok.com/api/collection/item_list/',
                                    params=params, headers=HEADERS, **kw)
                data = resp.json()
                break
            except Exception:
                if attempt == RATE['retries'] - 1:
                    return items
                time.sleep(5)

        if data.get('status_code') != 0:
            break
        for it in data.get('itemList', []):
            author = it.get('author', {}).get('uniqueId', '')
            stats = it.get('stats', {})
            items.append({
                'id': it.get('id', ''),
                'url': f"https://www.tiktok.com/@{author}/video/{it.get('id', '')}",
                'desc': it.get('desc', ''),
                'author': author,
                'plays': stats.get('playCount', 0),
                'likes': stats.get('diggCount', 0),
                'comments': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
            })
        if not data.get('hasMore') or not data.get('itemList'):
            break
        cursor = int(data.get('cursor', 0))
        time.sleep(RATE['interval'])
    return items


# ── Main ─────────────────────────────────────────────────────

def scrape(target: str, cookie_str: str = None, output: str = None) -> dict:
    start = time.time()
    cookies = None
    if cookie_str:
        cookies = {}
        for part in cookie_str.split('; '):
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k.strip()] = v.strip()

    print(f'[1/3] Resolving user: {target}', file=sys.stderr)
    user = resolve_user(target)
    print(f'      secUid: {user["secUid"][:30]}...', file=sys.stderr)

    print(f'[2/3] Fetching collections...', file=sys.stderr)
    collections = get_collections(user['secUid'], cookies)
    print(f'      Found {len(collections)} collections', file=sys.stderr)

    print(f'[3/3] Fetching videos...', file=sys.stderr)
    results = []
    total = 0
    for i, col in enumerate(collections):
        items = get_items(col['collectionId'], cookies)
        total += len(items)
        expected = int(col.get('total', 0))
        results.append({
            'collectionId': col['collectionId'], 'name': col.get('name', ''),
            'expected': expected, 'actual': len(items), 'items': items,
        })
        icon = '✅' if len(items) >= expected else '⚠️' if items else '❌'
        print(f'  [{i+1:3d}/{len(collections)}] {icon} {col.get("name","")[:30]:30s} '
              f'expected={expected:3d} actual={len(items):3d}', file=sys.stderr)
        if (i + 1) % RATE['batch_size'] == 0:
            time.sleep(RATE['batch_pause'])
        else:
            time.sleep(RATE['interval'])

    elapsed = round(time.time() - start, 1)
    result = {
        'target': target, 'secUid': user['secUid'], 'uid': user.get('uid'),
        'uniqueId': user.get('uniqueId'), 'mode': 'login' if cookies else 'guest',
        'totalCollections': len(results), 'totalVideos': total,
        'elapsedSeconds': elapsed, 'collections': results,
    }

    if output:
        with open(output, 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f'\n✅ Done: {len(results)} collections, {total} videos, {elapsed}s → {output}', file=sys.stderr)
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print(f'\n✅ Done: {len(results)} collections, {total} videos, {elapsed}s', file=sys.stderr)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TikTok Collection Scraper')
    parser.add_argument('target', help='username / URL / user_id / secUid')
    parser.add_argument('--cookie', help='Path to cookie file')
    parser.add_argument('--output', '-o', help='Output JSON path')
    args = parser.parse_args()

    cookie_str = None
    if args.cookie:
        with open(args.cookie) as f:
            cookie_str = f.read().strip()

    scrape(args.target, cookie_str, args.output)
