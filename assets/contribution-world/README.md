# Monthly contribution preview

The checked-in calendar is a real GitHub GraphQL snapshot for gdfaler. Both SVGs are generated from the same saved calendar; no demonstration data is used here.

The slate-to-violet palette, grid, frame and typography match the profile showcase. A maximum of twelve monthly panels replaces the large calendar grid. Each panel has its month or month range, actual contribution total, and exact first/last date. Days run left to right with one raised 3D column per active day and a flat marker per zero day. When the trailing year spans thirteen months, the first month fragment is combined with the next and both months are named. Every date is preserved exactly once. One shared logarithmic height scale applies to all panels; cap colors follow GitHub activity levels. There are no weekday axes or decorative terrain elements.

Reproduce without network access:

```sh
python3 scripts/contribution_world.py --input assets/contribution-world/calendar.json --output-dir assets/contribution-world
python3 -m unittest discover -s tests -v
```

To refresh from GitHub, set GH_TOKEN or GITHUB_TOKEN in your environment and omit `--input`. Refresh the README image version queries if the rendered files change.

This preview references the local snapshot so the existing image branch and default branch stay untouched. It does not update on a schedule. After the renderer is merged into the default branch, run the existing workflow. Confirm its restyled images and then switch the README image references back to `https://raw.githubusercontent.com/gdfaler/gdfaler/contribution-world/world-{dark,light}.svg` after confirming the new images. Scheduled workflows use the default branch; merging the generator is required for future scheduled renders in this style.
