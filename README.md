# kodi-webview

A simple Kodi launcher plug-in that opens a configurable website from a
top-level menu entry.

## Features

* **Top-level menu entry** — the addon appears under *Programs* in the Kodi
  main menu.  On first launch you are offered the option to add a home-screen
  shortcut (Kodi *Favourite*) so it is reachable directly from the home screen
  with the label of your choice.
* **Reliable browser launch** — the website is opened in the system default
  browser instead of relying on unsupported embedded webview controls.
* **Configurable URL** — set any website URL in the addon settings.
* **Configurable menu label** — set the label shown in the navigation bar and
  used for the home-screen shortcut.

## Requirements

| Requirement | Notes |
|---|---|
| Kodi 18 (Leia) or later | Earlier versions may work but are untested |
| System web browser | The addon opens the configured URL via Python's `webbrowser` module |

## Installation

1. Download or clone this repository.
2. In Kodi open *Settings → Add-ons → Install from zip file* and select the
   directory / zip.
3. The addon appears under *Add-ons → Programs → WebView*.

## Configuration

Open *Add-ons → Programs → WebView → ⚙ Settings* (or long-press the addon
entry) and set:

| Setting | Default | Description |
|---|---|---|
| **Website URL** | `https://example.com` | The website to display |
| **Menu Label** | `WebView` | Label shown in the navigation bar and home-screen shortcut |

## Usage

1. Launch the addon from *Programs* (or your home-screen shortcut).
2. The website opens in your system default browser.
3. Return to Kodi normally after closing or switching away from the browser.

## Addon structure

```
plugin.program.webview/
├── addon.xml                          # Addon metadata & extension points
├── default.py                         # Main addon script
└── resources/
    ├── settings.xml                   # Addon settings (URL, label)
    ├── language/
    │   └── English/
    │       └── strings.po             # Localised strings
    └── skins/
        └── Default/
            ├── 720p/
            │   └── webview.xml        # Window layout (720p)
            └── 1080i/
                └── webview.xml        # Window layout (1080i)
```
