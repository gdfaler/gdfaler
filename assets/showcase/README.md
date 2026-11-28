# Profile showcase

Original SVG artwork for this profile. The composition takes inspiration from [guilyx's profile](https://github.com/guilyx): an identity screen followed by engineering scenes, with a compact navigation row. No artwork, animation frames, source code or biographical copy from that profile is reused.

The four scenes show:

1. Egor / gdfaler, CS student at BMSTU, native apps and technical interests.
2. DynamicIsland: an original schematic of notch-based music controls and timers.
3. HWMonitor: a capability diagram for temperatures, power, processes and frequency.
4. TorrentPlayer: a schematic of BitTorrent pieces, buffering and playback, labelled as an early MVP.

Motion is coordinated across the 28-second cycle:

- Identity: name reveal, staggered facts, traced laptop outline, scanning highlight and app icon entrances.
- DynamicIsland: contraction and expansion between music, timer and alert modes.
- HWMonitor: packets follow the diagram connections into the app, with polling highlights and a processor pulse.
- TorrentPlayer: incoming pieces, a shifting buffer, outgoing packets and moving schematic video frames.

The reduced-motion layout disables all active animation and shows the complete identity immediately.

The diagrams illustrate actual project capabilities. They contain no live telemetry, fabricated GitHub statistics, temperature samples, transfer rates or media metadata. The app icons come from the applications' own sources; see [app icon sources](../apps/README.md).

Rebuild deterministically with Python's standard library:

```sh
python3 scripts/profile_showcase.py
python3 -m unittest discover -s tests -v
```

The showcase has light/dark variants, separate mobile layouts, accessible descriptions and a reduced-motion fallback showing the identity screen. All information and project links also appear in the README's expandable text section. Assets are self-contained: no JavaScript, remote fonts, third-party widgets or external SVG resources. No background refresh is needed or promised for these authored illustrations.

The existing Contribution World generator, publishing workflow and output branch remain unchanged. Its image stays available in a separate expandable section.

Hero image references include content-version queries so a changed animation does not reuse a previous cached image. Refresh these queries when regenerating changed hero files.
