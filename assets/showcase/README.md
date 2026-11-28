# Profile showcase

Original SVG artwork for this profile. The composition takes inspiration from [guilyx's profile](https://github.com/guilyx): an identity screen followed by engineering scenes, with a compact navigation row. No artwork, animation frames, source code or biographical copy from that profile is reused.

The four scenes show:

1. Egor / gdfaler, CS student at BMSTU, native apps and technical interests.
2. DynamicIsland: an original schematic of notch-based music controls and timers.
3. HWMonitor: a capability diagram for temperatures, power, processes and frequency.
4. TorrentPlayer: a schematic of BitTorrent pieces, buffering and playback, labelled as an early MVP.

Motion is coordinated across the 40-second cycle (7s identity, 19s DynamicIsland, 7s HWMonitor, 7s TorrentPlayer):

- Identity: name reveal, staggered facts, traced laptop outline, full-screen glass shading and a broad clipped diagonal reflection and app icon entrances.
- DynamicIsland: equal six-second slots for music, timer and alert modes. Each mode stays fully visible for 3.95 seconds, with the same reveal/fade timing and space for expansion/contraction. Content fades in only after expansion and fades out before contraction.
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

Contribution World uses the same slate/violet palette, background grid, frame and typography as the showcase. Activity is grouped into monthly panels, each with one raised column per active day and flat markers for zero days. Exact start/end dates label each panel; the first partial month is combined with the next if needed to fit twelve panels. Real activity determines height on one shared logarithmic scale. Its publishing workflow and output branch remain unchanged. For this preview, README uses the local real-data snapshot in `assets/contribution-world`; see its README for rebuilding and the merge handoff.

Hero image references include content-version queries so a changed animation does not reuse a previous cached image. Refresh these queries when regenerating changed hero files.
