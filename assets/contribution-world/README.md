# Contribution calendar preview

The checked-in calendar is a real GitHub GraphQL snapshot for gdfaler. Both SVGs are generated from the same saved calendar; no demonstration data is used here.

The slate-to-violet palette, grid, frame and typography match the profile showcase. A front-facing rectangular calendar replaces the diagonal projection. Weeks share a horizontal axis and seven weekday labels align to fixed rows. Month brackets use the exact week-column boundaries (boundary weeks can include days from two months). Active days are narrow 3D columns; zero days are flat outlined markers. Column height is limited to the space in each row so a bar cannot obscure the day above it. Height remains logarithmic in the actual count and cap colors follow the five GitHub activity levels. There are no terrain caps, vegetation, clouds or decorative towers. The small summary shows the actual count of active days and the maximum daily count. The subtle edge pulse is decorative and does not simulate data updates.

Reproduce without network access:

```sh
python3 scripts/contribution_world.py --input assets/contribution-world/calendar.json --output-dir assets/contribution-world
python3 -m unittest discover -s tests -v
```

To refresh from GitHub, set GH_TOKEN or GITHUB_TOKEN in your environment and omit `--input`. Refresh the README image version queries if the rendered files change.

This preview references the local snapshot so the existing image branch and default branch stay untouched. It does not update on a schedule. After the renderer is merged into the default branch, run the existing workflow. Confirm its restyled images and then switch the README image references back to `https://raw.githubusercontent.com/gdfaler/gdfaler/contribution-world/world-{dark,light}.svg` after confirming the new images. Scheduled workflows use the default branch; merging the generator is required for future scheduled renders in this style.
