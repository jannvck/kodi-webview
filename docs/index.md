---
layout: default
title: kodi-webview
---

# kodi-webview

A simple Kodi launcher plug-in that opens a configurable website from a top-level menu entry.

## Download

<p id="download-section">
  <a id="download-btn" href="https://github.com/jannvck/kodi-webview/releases/latest" class="btn">
    Download latest release
  </a>
  <span id="release-meta"></span>
</p>

<script>
fetch('https://api.github.com/repos/jannvck/kodi-webview/releases/latest')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var asset = data.assets && data.assets.find(function(a) { return a.name.endsWith('.zip'); });
    var btn = document.getElementById('download-btn');
    var meta = document.getElementById('release-meta');
    if (asset) {
      btn.href = asset.browser_download_url;
      btn.textContent = 'Download ' + data.tag_name + ' (' + asset.name + ')';
      meta.textContent = ' — ' + (asset.size / 1024).toFixed(1) + ' KB';
    } else if (data.tag_name) {
      btn.href = data.html_url;
      btn.textContent = 'Download ' + data.tag_name;
    }
  })
  .catch(function() {});
</script>

## Features

- **Top-level menu entry** — the addon appears under *Programs* in the Kodi main menu.
- **App-mode browser** — opens the website in Chromium/Chrome `--app` mode, hiding all browser controls (tabs, address bar, toolbar) so only the page content is visible. Falls back to the system default browser when Chromium is not available.
- **Configurable URL** — set any website URL in the addon settings.
- **Configurable menu label** — set the label shown in the navigation bar and used for a home-screen shortcut.

## Installation

1. Download the zip from the **Download** button above.
2. In Kodi open *Settings → Add-ons → Install from zip file* and select the downloaded zip.
3. The addon appears under *Add-ons → Programs → WebView*.

## Configuration

Open *Add-ons → Programs → WebView → ⚙ Settings* and set:

| Setting | Default | Description |
|---|---|---|
| **Website URL** | `https://example.com` | The website to open |
| **Menu Label** | `WebView` | Label shown in the navigation bar and home-screen shortcut |

## Requirements

| Requirement | Notes |
|---|---|
| Kodi 18 (Leia) or later | Earlier versions may work but are untested |
| Chromium or Google Chrome | Used for app mode; falls back to the system browser |

## Source

Source code is available on [GitHub](https://github.com/jannvck/kodi-webview).
