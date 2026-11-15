# Synth Cook Book 🐈

<p align="center"><a href="https://ko-fi.com/studio87"><img src="https://raw.githubusercontent.com/SpeakingColors/.github/main/assets/kofi-banner.svg" alt="Support Studio 87 on Ko-fi" width="440"></a></p>

<img src="assets/icon.svg" width="96" align="right" alt="icon">

Preset cookbook (recipe book) for hardware synths that cannot save sounds: Behringer Pro-1, CAT, TD-3-MO, TD-3, MODEL D and POLY D; Moog Mother-32, DFAM, Subharmonicon, Grandmother and Minimoog Model D; Arturia MicroBrute; Korg volca bass and volca keys. Works on Linux, macOS and Windows.

<p align="center"><img src="docs/screenshot.png" alt="Synth Cook Book recipe book showing the Pro-1 panel" width="900"></p>
<p align="center"><sub>Screenshot of docs/recipe-book.html in a browser.</sub></p>

## Status
Usable: the Synth Cook Book (`docs/recipe-book.html`) draws a panel for each of the 14 synths above (pick one in the Synth menu; the first four are drawn from photos, the other ten from the manuals' control lists) and stores your recipes in the browser; the release zip has it as an offline file with a short manual. No plugin build yet. Some knob values were read from a photo and are marked in the page (dashed ring: estimate, yellow ?: low confidence). The page links Google Fonts for its typeface, its only network request; offline it falls back to another font.

<p align="center">
  <a href="https://ko-fi.com/studio87"><img src="https://img.shields.io/badge/Support_Studio_87-on_Ko--fi-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white" alt="Support Studio 87 on Ko-fi"></a>
</p>

☕ Free and open source, made by one person. If it helps your music, a coffee on [Ko-fi](https://ko-fi.com/studio87) keeps it coming. 💜

## Docs
- [Overview page](docs/about.html): screenshot, status and links.
- Manual: built by `tools/make_manual.py` in the release workflow, with an interface tour. Regenerate the tour data and screenshot with `python3 tools/shoot_tour.py` (needs Playwright), then rebuild the PDF.
- [Device notes](docs/DEVICE-NOTES.md): what is confirmed from manuals, and what is still missing.
- [TD-3-MO notes](docs/TD-3-MO-NOTES.md): what the guide confirms; only CC 74 (cutoff) is known, so there is no TD-3-MO controller plugin.
- [Roadmap](ROADMAP.md)

## Patch book site
Browse and share patches in the browser: `docs/index.html` (GitHub Pages from `/docs`). Format: [docs/PATCH-FORMAT.md](docs/PATCH-FORMAT.md). How to share and switch Pages on: [docs/SHARING.md](docs/SHARING.md).

## License
AGPL-3.0-or-later, see [LICENSE](LICENSE).

Not affiliated with or endorsed by Behringer, Music Tribe, Moog Music, Arturia or Korg. All trademarks belong to their owners.
