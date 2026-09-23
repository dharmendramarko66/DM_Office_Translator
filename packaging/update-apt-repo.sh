#!/bin/bash
# =========================================================
# DM Office Translator — apt रेपो (GitHub Pages) publish helper
#
# नई .deb को apt-repo में publish करने का एक ही command:
#   bash packaging/update-apt-repo.sh
#
# यह करता है:
#   1. नई .deb build करता है (packaging/build-deb.sh)
#   2. उसे apt-repo/pool/main/d/dm-office-tools/ में copy करता है
#   3. dists/noble/main/binary-amd64/Packages(.gz) फिर से
#      generate करता है
#   4. dists/noble/Release की checksums फिर से बनाता है
#
# जो यह नहीं कर सकता (GPG private key चाहिए):
#   - InRelease / Release.gpg को sign करना। नीचे के instructions
#     देखें — sign करने के बाद ही apt update करने वाले users को
#     नया version दिखेगा।
# =========================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

APT_DIR="$PROJECT_DIR/apt-repo"
SUITE="noble"
COMPONENT="main"
ARCH="amd64"

VERSION="$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR/stable')
import soht_version
print(soht_version.APP_VERSION)
")"

DEB_NAME="dm-office-tools_${VERSION}_${ARCH}.deb"
DEB_PATH="$PROJECT_DIR/$DEB_NAME"
POOL_DIR="$APT_DIR/pool/$COMPONENT/d/dm-office-tools"
DIST_BIN="$APT_DIR/dists/$SUITE/$COMPONENT/binary-$ARCH"

echo "========================================"
echo " DM Office Translator — apt repo update"
echo "========================================"
echo "Version : $VERSION"
echo

# ---------------------------------------------------------
# 1. Build the .deb (fresh)
# ---------------------------------------------------------
bash "$SCRIPT_DIR/build-deb.sh"

if [[ ! -f "$DEB_PATH" ]]; then
    echo "[ERROR] Build ने .deb नहीं बनाया: $DEB_PATH"
    exit 1
fi

# ---------------------------------------------------------
# 2. Copy into the pool
# ---------------------------------------------------------
mkdir -p "$POOL_DIR"
cp -f "$DEB_PATH" "$POOL_DIR/"
echo "[OK] Copied: $POOL_DIR/$DEB_NAME"

# पुरानी .deb files pool में रह सकती हैं — apt सबसे नई उठाता है।
# पुरानी हटानी हों तो पहले pool से delete करके यह script दोबारा चलाएँ।

# ---------------------------------------------------------
# 3. Regenerate Packages index
#    (मूल convention: project root से scan, Filename में
#    apt-repo/ prefix — पुराने Packages file जैसा ही)
# ---------------------------------------------------------
if ! command -v dpkg-scanpackages >/dev/null 2>&1; then
    echo "[ERROR] dpkg-scanpackages नहीं मिला — पहले install करें:"
    echo "        sudo apt install dpkg-dev"
    exit 1
fi

cd "$PROJECT_DIR"
dpkg-scanpackages --arch "$ARCH" "apt-repo/pool/$COMPONENT" \
    > "$DIST_BIN/Packages" 2>/dev/null

gzip -9 -c "$DIST_BIN/Packages" > "$DIST_BIN/Packages.gz"

echo "[OK] Regenerated: dists/$SUITE/$COMPONENT/binary-$ARCH/Packages(.gz)"

# ---------------------------------------------------------
# 4. Regenerate Release (checksums, relative paths के साथ)
# ---------------------------------------------------------
gen_hash() {
    # $1 = algorithm (md5sum/sha1sum/sha256sum)
    # $2 = file (absolute), $3 = Release के relative path
    local sum size
    sum="$($1 "$2" | cut -d' ' -f1)"
    size="$(stat -c%s "$2")"
    printf '  %s %s %s\n' "$sum" "$size" "$3"
}

PACKAGES_REL="$COMPONENT/binary-$ARCH/Packages"
PACKAGES_GZ_REL="$COMPONENT/binary-$ARCH/Packages.gz"

{
    echo "Architectures: $ARCH"
    echo "Codename: $SUITE"
    echo "Components: $COMPONENT"
    echo "Date: $(date -u '+%a, %d %b %Y %H:%M:%S +0000')"
    echo "Suite: $SUITE"
    echo "MD5Sum:"
    gen_hash md5sum    "$DIST_BIN/Packages"    "$PACKAGES_REL"
    gen_hash md5sum    "$DIST_BIN/Packages.gz" "$PACKAGES_GZ_REL"
    echo "SHA1:"
    gen_hash sha1sum   "$DIST_BIN/Packages"    "$PACKAGES_REL"
    gen_hash sha1sum   "$DIST_BIN/Packages.gz" "$PACKAGES_GZ_REL"
    echo "SHA256:"
    gen_hash sha256sum "$DIST_BIN/Packages"    "$PACKAGES_REL"
    gen_hash sha256sum "$DIST_BIN/Packages.gz" "$PACKAGES_GZ_REL"
} > "$APT_DIR/dists/$SUITE/Release"

echo "[OK] Regenerated: dists/$SUITE/Release"

# ---------------------------------------------------------
# 5. Signing instructions
# ---------------------------------------------------------
cat <<'SIGNING_INFO'

========================================
 अब SIGN करना ज़रूरी है (private key से)
========================================

apt repo को valid बनाए रखने के लिए Release files को अपनी
GPG key से sign करें (script यह नहीं कर सकती — private key
कभी script/repo में न रखें):

  cd apt-repo/dists/noble

  # InRelease (clearsigned):
  gpg --default-key <KEY-ID> --clearsign -o InRelease Release

  # Release.gpg (detached signature):
  gpg --default-key <KEY-ID> -abs -o Release.gpg Release

फिर changes commit करके gh-pages branch पर push करें।
Users को नया version तभी दिखेगा जब वे apt update चलाएँगे।

========================================
 DONE (unsigned)
========================================
SIGNING_INFO
