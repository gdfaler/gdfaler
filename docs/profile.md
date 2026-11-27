# Profile generation

The profile is a **dated public snapshot**, not a live dashboard. No third-party statistics widgets, scripts, web fonts or external SVG resources are used. All new SVGs include title/description, explicit light/dark variants, mobile layouts and reduced-motion styles. If animations are suppressed, the first Island state remains readable; every state and chart value is also available in [snapshot.md](../assets/profile/snapshot.md).

## Reproduce before merge

```sh
# Offline, byte-for-byte reproduction from the checked-in real snapshot:
python3 scripts/profile.py
python3 -m unittest discover -s tests -v

# Fresh public data; optional GH_TOKEN increases the API rate limit:
python3 scripts/profile.py --fetch

# Local SVG composition preview (open work/profile-preview.html):
python3 scripts/preview_profile.py
```

The new workflow runs on pushes to `feat/profile-under-the-hood`, on pull requests to validate committed assets, and manually **after the workflow becomes registered on the default branch**. Before merge, the push run uploads a fresh preview artifact and does not commit anywhere. Scheduled Actions only run from the default branch: **there is no scheduled refresh of this review branch before merge**.

After merge, the schedule refreshes the fixed `profile-assets` branch only. It never commits to main, the review branch or `contribution-world`. The README points to `profile-assets`, manually seeded with the exact checked-in snapshot for this review. The committed copies in `assets/profile` also support offline reproduction and local preview. Before merge, this output branch is a frozen dated preview; after merge the scheduled workflow can refresh it without changing main.

The compact Monitor shows four featured repositories; its language distribution and activity use the full set of owned public non-fork repositories. The full per-repository table remains in the text snapshot.

## Sources and definitions

All API endpoints are under `https://api.github.com`. The snapshot stores no credentials, private repository metadata, email addresses or raw commit payloads.

- **Repositories:** paginated `/users/gdfaler/repos?type=owner`, public, owned and non-fork; archived repositories are included. Empty repositories are included in language counts, with `Unclassified` for null languages.
- **Languages:** one repository, one vote for its GitHub primary language. The denominator is all selected repositories, including the profile itself. This is neither code-byte distribution nor a claim of proficiency. TorrentPlayer is classified as C++ by GitHub despite its Swift UI.
- **Latest commit:** first REST commit matching `author=gdfaler` on each repository's default branch; the most recent returned author timestamp across repositories is shown. This excludes other branches and private work. REST orders history by commit topology, so rebased/backdated author timestamps may differ from push order.
- **Activity:** paginated `/repos/{owner}/{repo}/commits?sha={default_branch}&author=gdfaler&since={30-day-start}`. Group by UTC **author date**, restricted to 30 dates ending on the snapshot day. The last seven calendar dates form weekly activity; the current day is partial. GitHub's `since` filter also applies commit timestamps, so backdated/rebased history can differ from a full historical author-date scan. Counts are per repository (a shared commit across two independent repositories can count twice). These are authored commits, **not GitHub contributions**, pushes, hours worked or lines of code. Merge commits can count. Contribution World keeps its separate existing GraphQL contribution calendar.
- **Releases:** all pages of `/repos/{owner}/{repo}/releases`, published stable releases only (no drafts or prereleases). Latest is chosen by publication time.
- **Downloads:** sum of GitHub `download_count` for all assets attached to those stable releases, including checksums/source bundles if uploaded as assets. Automatic source ZIP/tar downloads are excluded. This is not unique users, installs or app launches. Zero means a real zero in the returned data.
- **CI:** latest Actions run returned for the default branch, across all workflow types. Shows its exact conclusion/status; `No runs` means an empty API result; `Unavailable` means HTTP 403/404. This can be a documentation workflow, does not summarize the test suite, and is not an overall pass rate. Run name/time/link remain in JSON. Other HTTP/network failures abort generation and preserve the last good files.

Core endpoint errors fail the whole refresh; no fabricated zeros or synthetic preview data are substituted. Collection is sequential, not an atomic GitHub transaction. Snapshot time is collection start (UTC), so counters can move during collection.

## Contribution World compatibility

The existing generator, tests, workflow, `contribution-world` branch and absolute image URLs are unchanged. New automation uses a separate concurrency group, artifact and output branch. The new workflow does not fetch private contribution data or need the `CONTRIBUTIONS_TOKEN` secret.

## Content corrections

The profile retains the owner's self-reported education and achievements from the previous README; this work does not independently certify awards. Hardware claims are scoped to supported capabilities rather than promising 115 sensors or a temperature reduction on every Mac. DynamicIsland uses documented facilities by default, but has an optional experimental MediaRemote integration. TorrentPlayer is an MVP using third-party libraries; it is not grouped under a zero-dependency claim. The previous fixed line/test counts and tiny training-corpus claim have been removed because they age quickly.
