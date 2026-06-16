"""
plugin.program.webview — default.py
====================================
Entry point for the WebView Kodi addon.

Lifecycle
---------
1. Kodi calls this script via ``plugin://plugin.program.webview/``.
2. Settings (URL, menu_label) are read from the addon configuration.
3. On the very first run the user is offered an optional home-screen
   shortcut (Kodi Favourite) so the addon appears as a top-level
   menu entry directly on the home screen.
4. The configured website URL is opened in the system default browser.
5. The addon remains useful as a Kodi launcher while avoiding embedded
   webview window creation paths that fail on current Kodi setups.
"""

from __future__ import unicode_literals

import json
import os
import shutil
import subprocess
import sys
import webbrowser

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo('name')

_DEFAULT_URL = 'https://example.com'
_DEFAULT_LABEL = ADDON_NAME

_SETTING_FIRST_RUN = 'first_run_done'


# ── Helpers ──────────────────────────────────────────────────────────


def _get_setting(key, fallback=''):
    value = ADDON.getSetting(key)
    return value if value else fallback


def get_url():
    return _get_setting('url', _DEFAULT_URL)


def get_label():
    return _get_setting('menu_label', _DEFAULT_LABEL)


def _localise(string_id):
    return ADDON.getLocalizedString(string_id)


def _find_chromium():
    """Return the path to a Chromium or Chrome executable, or *None*."""
    candidates = [
        # Linux
        'chromium-browser',
        'chromium',
        'google-chrome',
        'google-chrome-stable',
        'google-chrome-beta',
        # macOS
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        # Windows (64-bit and 32-bit Program Files)
        os.path.join(
            os.environ.get('PROGRAMFILES', r'C:\Program Files'),
            r'Google\Chrome\Application\chrome.exe',
        ),
        os.path.join(
            os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'),
            r'Google\Chrome\Application\chrome.exe',
        ),
        os.path.join(
            os.environ.get('LOCALAPPDATA') or '',
            r'Google\Chrome\Application\chrome.exe',
        ) if os.environ.get('LOCALAPPDATA') else None,
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        if os.path.isabs(candidate):
            if os.path.isfile(candidate):
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def _open_chromium_app(url):
    """
    Launch Chromium/Chrome in app mode for *url*.

    App mode (``--app=URL``) hides the tab strip, address bar, toolbar
    (back/forward/refresh) and bookmarks bar so only the website content
    is visible.  Returns *True* on success, *False* if no Chromium
    executable was found or the process could not be started.
    """
    exe = _find_chromium()
    if not exe:
        return False
    try:
        subprocess.Popen(
            [exe, '--app={}'.format(url)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        xbmc.log(
            '{}: opened {} in Chromium app mode ({})'.format(
                ADDON_ID, url, exe
            ),
            xbmc.LOGINFO,
        )
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        xbmc.log(
            '{}: failed to launch Chromium app mode for {} ({})'.format(
                ADDON_ID, url, exc
            ),
            xbmc.LOGWARNING,
        )
        return False


def _open_external_browser(url):
    if _open_chromium_app(url):
        return True
    xbmc.log(
        '{}: Chromium not found, falling back to system browser for {}'.format(
            ADDON_ID, url
        ),
        xbmc.LOGINFO,
    )
    try:
        return webbrowser.open(url)
    except OSError as exc:
        xbmc.log(
            '{}: failed to open external browser for {} ({})'.format(
                ADDON_ID, url, exc
            ),
            xbmc.LOGERROR,
        )
        xbmcgui.Dialog().ok(
            _localise(32020),   # "Cannot open browser"
            _localise(32021),   # "No supported browser…"
        )
        return False


# ── Home-screen shortcut (Kodi Favourites) ───────────────────────────


def _add_favourite(label, plugin_url):
    """Add *plugin_url* to Kodi Favourites with the given *label*."""
    payload = json.dumps({
        'jsonrpc': '2.0',
        'method': 'Favourites.AddFavourite',
        'params': {
            'title': label,
            'type': 'media',
            'path': plugin_url,
        },
        'id': 1,
    })
    xbmc.executeJSONRPC(payload)


def _maybe_offer_shortcut(label):
    """
    On the very first run, ask the user whether to add a home-screen
    shortcut.  The choice is persisted so the dialog only appears once.
    """
    if ADDON.getSetting(_SETTING_FIRST_RUN) == 'true':
        return

    ADDON.setSetting(_SETTING_FIRST_RUN, 'true')

    dialog = xbmcgui.Dialog()
    if dialog.yesno(
        _localise(32010),   # "Add home screen shortcut"
        _localise(32011),   # "Would you like to add a shortcut …"
        yeslabel=_localise(32012),
        nolabel=_localise(32013),
    ):
        plugin_url = 'plugin://{}/'.format(ADDON_ID)
        _add_favourite(label, plugin_url)


# ── Entry point ───────────────────────────────────────────────────────


def main():
    try:
        handle = int(sys.argv[1]) if len(sys.argv) > 1 else -1
    except ValueError:
        handle = -1

    url = get_url()
    label = get_label()

    _maybe_offer_shortcut(label)

    xbmc.log(
        '{}: opening {} in the system browser'.format(
            ADDON_ID, url
        ),
        xbmc.LOGINFO,
    )
    _open_external_browser(url)

    if handle >= 0:
        xbmcplugin.endOfDirectory(handle)


if __name__ == '__main__':
    main()
