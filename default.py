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
5. The addon remains useful as a Kodi launcher while avoiding unsupported
   embedded-browser window creation paths.
"""

from __future__ import unicode_literals

import json
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


def _open_external_browser(url):
    try:
        return webbrowser.open(url)
    except Exception as exc:
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
        '{}: Kodi Python addons do not support an embedded browser control; opening {} in the system browser'.format(
            ADDON_ID, url
        ),
        xbmc.LOGINFO,
    )
    _open_external_browser(url)

    if handle >= 0:
        xbmcplugin.endOfDirectory(handle)


if __name__ == '__main__':
    main()
