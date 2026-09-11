#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ------------------------------------------------------------
# DM Office Tools — Google IPv4 bootstrap/cache
# ------------------------------------------------------------

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/dm-office-tools"
CACHE_FILE="$CACHE_DIR/google_ipv4_cache"

mkdir -p "$CACHE_DIR" 2>/dev/null || true

is_valid_ipv4() {
    [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

GOOGLE_IPV4=""

# ------------------------------------------------------------
# 1. FAST PATH — persistent user cache
# ------------------------------------------------------------

if [[ -f "$CACHE_FILE" ]]; then
    CACHED_IPV4="$(head -n 1 "$CACHE_FILE" 2>/dev/null | tr -d '[:space:]')"

    if is_valid_ipv4 "$CACHED_IPV4"; then
        GOOGLE_IPV4="$CACHED_IPV4"
        echo "[सूचना] Google Input Tools cached IPv4: $GOOGLE_IPV4"
    else
        rm -f "$CACHE_FILE" 2>/dev/null || true
    fi
fi

# ------------------------------------------------------------
# 2. BOOTSTRAP PATH
# ------------------------------------------------------------
# DNS को translation से पहले block नहीं करना है।
#
# यह केवल known-good bootstrap IPv4 है।
# Background DNS refresh बाद में cache को update करेगा।

if [[ -z "$GOOGLE_IPV4" ]]; then
    GOOGLE_IPV4="192.178.174.118"
    echo "[सूचना] Google Input Tools bootstrap IPv4: $GOOGLE_IPV4"
fi

# ------------------------------------------------------------
# 3. BACKGROUND DNS REFRESH
# ------------------------------------------------------------
# Translation शुरू होने में DNS का इंतज़ार नहीं होगा।
#
# केवल पहला valid IPv4 मिलने पर cache update करें।

(
    if command -v timeout >/dev/null 2>&1; then
        REFRESH_IPV4="$(
            timeout --signal=KILL 2s \
                getent ahostsv4 inputtools.google.com 2>/dev/null |
                awk 'NR==1 {print $1}'
        )"
    else
        REFRESH_IPV4="$(
            getent ahostsv4 inputtools.google.com 2>/dev/null |
            awk 'NR==1 {print $1}'
        )"
    fi

    if is_valid_ipv4 "$REFRESH_IPV4"; then
        printf '%s\n' "$REFRESH_IPV4" > "$CACHE_FILE"
        chmod 600 "$CACHE_FILE" 2>/dev/null || true
    fi
) >/dev/null 2>&1 &

# ------------------------------------------------------------
# 4. PASS IPv4 TO PYTHON
# ------------------------------------------------------------

if is_valid_ipv4 "$GOOGLE_IPV4"; then
    export GOOGLE_IPV4
else
    unset GOOGLE_IPV4
fi

exec python3 "$SCRIPT_DIR/english_to_hindi_hybrid.py"
