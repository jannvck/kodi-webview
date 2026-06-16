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
4. A :class:`WebViewWindow` dialog is opened, maximising the browser
   control below a slim navigation bar (label + close button).
5. On Kodi builds *without* CEF/Chromium embedded support the browser
   control is unavailable; the code falls back to
   ``webbrowser.open(url)`` so the site still opens in the system
   default browser.
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


# ── WebView window ────────────────────────────────────────────────────


class WebViewWindow(xbmcgui.WindowXMLDialog):
    """
    Dialog window that hosts the browser control.

    The browser control (control ID 100) fills the entire area below
    the navigation bar, giving the website as much display space as
    possible.  The navigation bar at the top keeps the Kodi chrome
    accessible at all times.

    On Kodi builds that do not include CEF/Chromium support the
    ``browser`` control is absent; :meth:`onInit` catches the error
    and opens the URL in the system default browser instead.
    """

    def __init__(self, *args, **kwargs):
        self._url = kwargs.pop('url', _DEFAULT_URL)
        self._label = kwargs.pop('label', _DEFAULT_LABEL)
        super(WebViewWindow, self).__init__(*args, **kwargs)

    def onInit(self):
        # Make url and label available to XML info-labels.
        self.setProperty('WebViewURL', self._url)
        self.setProperty('WebViewLabel', self._label)

        # Attempt to drive the embedded browser control.
        try:
            browser = self.getControl(100)
            browser.setPath(self._url)
        except (AttributeError, RuntimeError):
            # Browser control unavailable (non-CEF build).
            self.close()
            try:
                webbrowser.open(self._url)
            except Exception:
                xbmcgui.Dialog().ok(
                    _localise(32020),   # "Cannot open browser"
                    _localise(32021),   # "No supported browser…"
                )

    def onAction(self, action):
        if action.getId() in (
            xbmcgui.ACTION_PREVIOUS_MENU,
            xbmcgui.ACTION_NAV_BACK,
        ):
            self.close()

    def onClick(self, control_id):
        if control_id == 1:  # Close / back button (ID 1 in webview.xml)
            self.close()


# ── Entry point ───────────────────────────────────────────────────────


def main():
    try:
        handle = int(sys.argv[1]) if len(sys.argv) > 1 else -1
    except ValueError:
        handle = -1

    url = get_url()
    label = get_label()

    _maybe_offer_shortcut(label)

    window = WebViewWindow(
        'webview.xml',
        ADDON_PATH,
        'Default',
        '720p',
        url=url,
        label=label,
    )
    window.doModal()
    del window

    if handle >= 0:
        xbmcplugin.endOfDirectory(handle)


if __name__ == '__main__':
    main()
