#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required: https://www.python.org/downloads/macos/"
  exit 1
fi

python3 -m venv .venv-macos
.venv-macos/bin/python -m pip install --upgrade pip
.venv-macos/bin/python -m pip install -r requirements.txt

.venv-macos/bin/python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name GuofengDesktopPet \
  --osx-bundle-identifier com.local.guofengdesktoppet \
  --add-data "assets/guofeng_frames:assets/guofeng_frames" \
  main.py

APP_PATH="dist/GuofengDesktopPet.app"
PLIST_PATH="$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Delete :LSUIElement" "$PLIST_PATH" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST_PATH"
/usr/libexec/PlistBuddy -c "Delete :NSHighResolutionCapable" "$PLIST_PATH" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :NSHighResolutionCapable bool true" "$PLIST_PATH"
codesign --force --deep --sign - "$APP_PATH"

DMG_PATH="dist/GuofengDesktopPet.dmg"
if [ -e "$DMG_PATH" ]; then
  rm -f "$DMG_PATH"
fi
hdiutil create \
  -volname "GuofengDesktopPet" \
  -srcfolder "$APP_PATH" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo "Built: $APP_PATH"
echo "Built: $DMG_PATH"
