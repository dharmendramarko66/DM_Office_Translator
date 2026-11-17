#!/usr/bin/env python3
"""Translation providers with automatic fallback — DM Office Translator v3.1.9.

समस्या जिसके लिए यह बना:
  कुछ कार्यालय नेटवर्क पर Google `translate.googleapis.com` को
  "automated queries" मानकर HTML वाला "Sorry..." पेज लौटा देता है।
  तब अनुवाद चुपचाप fail होकर transliteration पर चला जाता था।

अब क्रम से तीन providers आज़माए जाते हैं:
  1. Google gtx      — translate.googleapis.com/translate_a/single
  2. Google clients5 — clients5.google.com/translate_a/t (dict-chrome-ex)
  3. MyMemory        — api.mymemory.translated.net (मुफ़्त, बिना key)

किसी एक के सफल होते ही अनुवाद मिल जाता है; सब fail हों तो कारण
`TranslationUnavailable` में लौटता है (UI उसे notification में दिखाता है)।
"""

import requests

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 DM-Office-Translator"
)

GOOGLE_GTX_URL = "https://translate.googleapis.com/translate_a/single"
GOOGLE_CLIENTS5_URL = "https://clients5.google.com/translate_a/t"
MYMEMORY_URL = "https://api.mymemory.translated.net/get"


class BlockedError(Exception):
    """Google ने HTML "Sorry..." पेज लौटाया — नेटवर्क/IP ब्लॉक।"""


class TranslationUnavailable(Exception):
    """कोई भी provider काम नहीं कर सका; message में कारण होता है।"""


def looks_blocked(body):
    """HTML ब्लॉक पेज पहचानें।"""
    head = (body or "")[:600].lower()
    return (
        "<html" in head
        or "sorry..." in head
        or "automated queries" in head
        or "unusual traffic" in head
    )


def _get(session, url, params, timeout):
    return session.get(
        url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT}
    )


def google_gtx(text, source, target, session, timeout):
    response = _get(
        session,
        GOOGLE_GTX_URL,
        {"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text},
        timeout,
    )

    if response.status_code == 429:
        raise RuntimeError("rate-limit")

    if looks_blocked(getattr(response, "text", "") or ""):
        raise BlockedError("google gtx blocked")

    response.raise_for_status()
    data = response.json()

    parts = []
    if isinstance(data, list) and data and isinstance(data[0], list):
        for item in data[0]:
            if isinstance(item, list) and item and isinstance(item[0], str):
                parts.append(item[0])

    result = "".join(parts).strip()
    if not result:
        raise RuntimeError("empty")
    return result


def google_clients5(text, source, target, session, timeout):
    response = _get(
        session,
        GOOGLE_CLIENTS5_URL,
        {"client": "dict-chrome-ex", "sl": source, "tl": target, "q": text},
        timeout,
    )

    if looks_blocked(getattr(response, "text", "") or ""):
        raise BlockedError("google clients5 blocked")

    response.raise_for_status()
    data = response.json()

    result = ""

    if isinstance(data, list):
        if data and isinstance(data[0], str):
            result = " ".join(part for part in data if isinstance(part, str))
        elif data and isinstance(data[0], list):
            result = " ".join(
                item[0] for item in data
                if isinstance(item, list) and item and isinstance(item[0], str)
            )
    elif isinstance(data, dict):
        sentences = data.get("sentences") or []
        result = " ".join(
            sentence.get("trans", "")
            for sentence in sentences
            if isinstance(sentence, dict)
        )

    result = result.strip()
    if not result:
        raise RuntimeError("empty")
    return result


def mymemory(text, source, target, session, timeout):
    response = _get(
        session,
        MYMEMORY_URL,
        {"q": text, "langpair": f"{source}|{target}"},
        timeout,
    )
    response.raise_for_status()
    data = response.json()

    payload = (data or {}).get("responseData") or {}
    result = (payload.get("translatedText") or "").strip()

    if not result:
        raise RuntimeError("empty")
    return result


PROVIDERS = (
    ("google", google_gtx),
    ("google-clients5", google_clients5),
    ("mymemory", mymemory),
)


def translate(text, source, target, session=None, timeout=8):
    """क्रम से providers आज़माएँ।

    लौटाता है: (translated_text, provider_name)
    सब fail हों तो TranslationUnavailable उठाता है।
    """
    active_session = session if session is not None else requests
    reasons = []
    blocked = 0

    for name, provider in PROVIDERS:
        try:
            return provider(text, source, target, active_session, timeout), name
        except BlockedError:
            blocked += 1
            reasons.append(f"{name}: blocked")
        except Exception as exc:  # noqa: BLE001 — हर provider अलग तरह से fail हो सकता है
            reasons.append(f"{name}: {type(exc).__name__}")

    raise TranslationUnavailable(
        f"blocked={blocked}; " + "; ".join(reasons)
    )
