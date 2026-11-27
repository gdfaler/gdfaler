#!/usr/bin/env python3
"""Public GitHub data -> deterministic, dependency-free profile SVGs and fallback."""
import argparse
from collections import Counter
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

API = 'https://api.github.com'
OWNER = 'gdfaler'
ROOT = Path(__file__).resolve().parents[1]


def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'gdfaler-profile',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urllib.request.urlopen(urllib.request.Request(API + path, headers=headers), timeout=30) as response:
        return json.load(response)


def pages(path):
    result = []
    for page in range(1, 1001):
        batch = api(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise ValueError('Pagination limit reached; refusing partial data')


def collect():
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    start = now.date() - dt.timedelta(days=29)
    repos = sorted((r for r in pages(f'/users/{OWNER}/repos?type=owner')
                    if not r['private'] and not r['fork']), key=lambda r: r['name'].lower())
    rows, latest, releases = [], [], []
    daily = Counter({(start + dt.timedelta(days=i)).isoformat(): 0 for i in range(30)})
    for r in repos:
        base = f'/repos/{OWNER}/{r["name"]}'
        commits = pages(base + f'/commits?sha={r["default_branch"]}&author={OWNER}&since={start}T00:00:00Z') if r['size'] else []
        for c in commits:
            # Authored-date bucketing; REST since also filters by committer date.
            date = c['commit']['author']['date'][:10]
            if date in daily:
                daily[date] += 1
        last = api(base + f'/commits?sha={r["default_branch"]}&author={OWNER}&per_page=1') if r['size'] else []
        if last:
            c = last[0]
            latest.append(dict(repo=r['name'], sha=c['sha'], url=c['html_url'],
                               date=c['commit']['author']['date'], message=c['commit']['message'].splitlines()[0]))
        rs = pages(base + '/releases')
        published = [x for x in rs if not x['draft'] and not x['prerelease']]
        for x in published:
            releases.append(dict(repo=r['name'], tag=x['tag_name'], date=x['published_at'], url=x['html_url']))
        # Only stable published releases, uploaded release assets; source ZIP/tar downloads are not counted.
        downloads = sum(a['download_count'] for x in published for a in x['assets'])
        ci = dict(label='Unavailable', url=r['html_url'] + '/actions')
        try:
            runs = api(base + f'/actions/runs?branch={r["default_branch"]}&per_page=1')['workflow_runs']
            if runs:
                run = runs[0]
                ci = dict(label=run['conclusion'] or run['status'], url=run['html_url'],
                          name=run['name'], date=run['updated_at'])
            else:
                ci['label'] = 'No runs'
        except urllib.error.HTTPError as error:
            if error.code not in (403, 404):
                raise
        rows.append(dict(name=r['name'], url=r['html_url'], branch=r['default_branch'],
                         language=r['language'], releases=len(published), downloads=downloads, ci=ci))
    return dict(schema=1, owner=OWNER, as_of=now.isoformat(), repos=rows,
                latest_commit=max(latest, key=lambda x:x['date']) if latest else None,
                latest_release=max(releases, key=lambda x:x['date']) if releases else None,
                activity=[dict(date=k, commits=v) for k,v in sorted(daily.items())])


def validate(data):
    if data['schema'] != 1 or data['owner'] != OWNER or not data['repos']:
        raise ValueError('Invalid snapshot')
    end = dt.datetime.fromisoformat(data['as_of']).date()
    dates = [dt.date.fromisoformat(x['date']) for x in data['activity']]
    if dates != [end - dt.timedelta(days=29-i) for i in range(30)]:
        raise ValueError('Expected 30 consecutive UTC days ending at snapshot date')
    for day in data['activity']:
        if type(day['commits']) is not int or day['commits'] < 0:
            raise ValueError('Invalid activity')
    for r in data['repos']:
        if not r['url'].startswith('https://github.com/gdfaler/'):
            raise ValueError('Unexpected repository URL')
        if any(type(r[k]) is not int or r[k] < 0 for k in ('releases','downloads')):
            raise ValueError('Invalid release counters')


def esc(value):
    return html.escape(str(value), quote=True)


def short(value, n):
    return value if len(value) <= n else value[:n-1] + '…'


def text(x,y,value, size=14, cls='', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{esc(value)}</text>'


def svg(theme, width, height, title, desc, body, css=''):
    dark = theme == 'dark'
    bg, fg, muted, line, panel = ('#0d141d','#e6edf3','#9aafc2','#2a3a48','#15212d') if dark else ('#f4f7f3','#1d352d','#536b61','#c6d5cd','#e7eee8')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;fill:{fg}}}.muted{{fill:{muted}}}.accent{{fill:{'#8adead' if dark else '#26704d'}}}.line{{stroke:{line}}}.panel{{fill:{panel}}}{css}</style>
<rect width="{width}" height="{height}" rx="24" fill="{bg}"/>{body}</svg>'''


def island(data, theme, mobile=False):
    w=420 if mobile else 900
    commit=data['latest_commit']; release=data['latest_release']
    weekly=sum(d['commits'] for d in data['activity'][-7:])
    states=[('LATEST COMMIT', f'{commit["repo"]} · {commit["sha"][:7]}' if commit else 'No public commits',
             short(commit['message'],37 if mobile else 72) if commit else 'Not available in this snapshot'),
            ('LATEST RELEASE', f'{release["repo"]} · {release["tag"]}' if release else 'No stable releases',
             release['date'][:10] + ' · stable public release' if release else 'No release data available'),
            ('WEEKLY ACTIVITY', f'{weekly} authored commits · 7 UTC days',
             f'{data["activity"][-7]["date"]} → {data["activity"][-1]["date"]}')]
    body=text(24,28,'GDFALER / UNDER THE HOOD',10,'muted', 'letter-spacing="2"')
    body+=f'<rect class="island panel" x="18" y="43" width="{w-36}" height="116" rx="45"/>'
    for i,(label,value,detail) in enumerate(states):
        body+=f'<g class="state s{i}"><circle class="pulse" cx="42" cy="73" r="4" fill="#62bd88"/>'
        body+=text(57,77,label,10,'muted','letter-spacing="2"')+text(40,108,short(value,36 if mobile else 76),16,'')+text(40,132,detail,11,'muted')+'</g>'
    body+=text(w-24,181,'PUBLIC SNAPSHOT · '+data['as_of'][:10],9,'muted','text-anchor="end"')
    css='''.island{transform-box:fill-box;transform-origin:center;animation:breathe 18s ease-in-out infinite}.state{opacity:0;animation:cycle 18s infinite}.s0{opacity:1}.s1{animation-delay:6s}.s2{animation-delay:12s}@keyframes cycle{0%,30%{opacity:1}33%,100%{opacity:0}}@keyframes breathe{0%,30%,36%,63%,69%,96%,100%{transform:scaleX(1)}33%,66%,99%{transform:scaleX(.94)}}.pulse{animation:pulse 2s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}@media(prefers-reduced-motion:reduce){.state,.island,.pulse{animation:none}.s0{opacity:1}.s1,.s2{opacity:0}}'''
    return svg(theme,w,196,'GitHub Dynamic Island','Cycles through latest authored default-branch commit, latest stable release and seven-day authored commit count. Public snapshot, not a live connection.',body,css)


def monitor(data,theme,mobile=False):
    w=420 if mobile else 900
    body=text(24,31,'DEVELOPER MONITOR',12,'muted','letter-spacing="2"')+text(24,62,f'{len(data["repos"])} public repos · {sum(r["releases"] for r in data["repos"])} stable releases',18)
    body+=text(24,86,'SNAPSHOT / '+data['as_of'][:19].replace('T',' ')+' UTC',10,'muted')
    body+=f'<path d="M24 103H{w-24}" class="line"/>'
    if mobile:
        body+=text(24,129,'REPOSITORY / STABLE RELEASES / ASSET DOWNLOADS',9,'muted')
    else:
        for x,v in [(24,'REPOSITORY'),(300,'PRIMARY LANGUAGE'),(510,'RELEASES'),(620,'DOWNLOADS'),(744,'LATEST CI RUN')]:
            body+=text(x,129,v,10,'muted')
    step=53 if mobile else 30
    shown=[r for name in ('HWMonitor','DynamicIsland','TorrentPlayer','ClipShot') for r in data['repos'] if r['name']==name]
    for i,r in enumerate(shown):
        y=157+i*step
        body+=f'<a href="{esc(r["url"])}">'+text(24,y,r['name'],13)+'</a>'
        if mobile:
            body+=text(24,y+20,f'{r["language"] or "Unclassified"} · {r["releases"]} rel · {r["downloads"]:,} dl',10,'muted')
            body+=text(w-24,y,short(r['ci']['label'],15),10,'accent','text-anchor="end"')
        else:
            body+=text(300,y,r['language'] or 'Unclassified',12,'muted')+text(535,y,r['releases'],12)+text(620,y,f'{r["downloads"]:,}',12)
            body+=f'<a href="{esc(r["ci"]["url"])}">'+text(744,y,short(r['ci']['label'],17),11,'accent')+'</a>'
    y=155+len(shown)*step
    body+=f'<path d="M24 {y}H{w-24}" class="line"/>'
    counts=Counter(r['language'] or 'Unclassified' for r in data['repos'])
    body+=text(24,y+30,'LANGUAGES / ONE REPOSITORY, ONE VOTE',11,'muted')
    colors=['#479d72','#5b91be','#a485c5','#c38c51','#8b9a9e']
    x=24
    for i,(lang,n) in enumerate(sorted(counts.items(),key=lambda p:(-p[1],p[0]))):
        bw=(w-48)*n/len(data['repos'])
        body+=f'<rect x="{x:.2f}" y="{y+44}" width="{bw:.2f}" height="8" fill="{colors[i%len(colors)]}"/>'
        x+=bw
    for i,(lang,n) in enumerate(sorted(counts.items(),key=lambda p:(-p[1],p[0]))):
        col=i%2 if mobile else i; row=i//2 if mobile else 0
        body+=text(24+col*(190 if mobile else 172),y+77+row*22,f'{lang} {n}/{len(data["repos"])}',11,'muted')
    y+=140 if mobile else 110
    body+=text(24,y,'ACTIVITY / 30 UTC DAYS',11,'muted')
    values=[d['commits'] for d in data['activity']]; peak=max(values) or 1
    bw=(w-48)/30
    for i,d in enumerate(data['activity']):
        h=70*d['commits']/peak
        body+=f'<rect x="{24+i*bw:.2f}" y="{y+90-h:.2f}" width="{max(1,bw-3):.2f}" height="{max(1,h):.2f}" fill="{colors[0]}" opacity="{1 if d["commits"] else .2}"><title>{d["date"]}: {d["commits"]} authored commits</title></rect>'
    body+=text(24,y+111,data['activity'][0]['date'],10,'muted')+text(w-24,y+111,data['activity'][-1]['date'],10,'muted','text-anchor="end"')
    body+=text(24,y+137,f'{sum(values)} commits · daily peak {max(values)} · default branches',10,'muted')
    body+=text(24,y+159,'Featured projects above · all repositories in text version.',9,'muted')
    return svg(theme,w,y+180,'Developer Monitor', 'Public owned non-fork repositories. Languages counted by primary repository language, not lines of code. Stable release asset downloads exclude source archives. CI is the latest default-branch Actions run. Activity is authored commits from the REST default-branch history over 30 UTC dates.',body)


def terminal(theme,mobile=False):
    w=420 if mobile else 900
    lines=['$ whoami','Egor / building things from scratch','$ ./life.sh','[OK] learn → build → break → repeat','[WARN] sleep: dependency not found']
    body=text(24,29,'TERMINAL / gdfaler — zsh',10,'muted','letter-spacing="1"')
    for i,line in enumerate(lines):
        body+=f'<g class="type t{i}">'+text(24,61+i*24,line,13,'accent' if line.startswith('$') else '')+'</g>'
    body+='<rect class="cursor" x="24" y="174" width="8" height="14" fill="#479d72"/>'
    css=''.join(f'.t{i}{{animation-delay:{i*1.1}s}}' for i in range(5))
    css+='.type{animation:typing 10s steps(34,end) infinite;clip-path:inset(0 0 0 0)}@keyframes typing{0%{clip-path:inset(0 100% 0 0)}12%,100%{clip-path:inset(0 0 0 0)}}.cursor{animation:blink 1s steps(2,end) infinite}@keyframes blink{50%{opacity:0}}@media(prefers-reduced-motion:reduce){.type,.cursor{animation:none;clip-path:none}}'
    return svg(theme,w,208,'Developer Terminal','A humorous terminal: learn, build, break, repeat. Sleep dependency not found. Decorative animation, no live shell.',body,css)


def fallback(data):
    c=data['latest_commit']; r=data['latest_release']
    result=['# Public GitHub snapshot', '',f'As of {data["as_of"]}. Refresh with `python scripts/profile.py --fetch`.', '',
            f'- Latest authored commit: [{c["repo"]} / {c["sha"][:7]}]({c["url"]}) — {c["message"]}' if c else '- Latest commit: unavailable.',
            f'- Latest stable release: [{r["repo"]} / {r["tag"]}]({r["url"]})' if r else '- Latest release: unavailable.',
            f'- Seven UTC dates: {sum(d["commits"] for d in data["activity"][-7:])} authored commits.', '',
            '| Repository | Primary language | Stable releases | Asset downloads | Latest default-branch Actions run |',
            '|---|---|---:|---:|---|']
    for x in data['repos']:
        result.append(f'| [{x["name"]}]({x["url"]}) | {x["language"] or "Unclassified"} | {x["releases"]} | {x["downloads"]} | [{x["ci"]["label"]}]({x["ci"]["url"]}) |')
    result+=['', '## Daily authored commits (UTC)', '', '| Date | Commits |','|---|---:|']
    result += [f'| {d["date"]} | {d["commits"]} |' for d in data['activity']]
    result+=['', 'Methodology and limits: [profile generation](https://github.com/gdfaler/gdfaler/blob/feat/profile-under-the-hood/docs/profile.md).', '']
    return '\n'.join(result)


def generate(data,out):
    validate(data)
    outputs={'snapshot.json': json.dumps(data,indent=2,ensure_ascii=False)+'\n','snapshot.md':fallback(data)}
    for theme in ('dark','light'):
        for mobile in (False,True):
            suffix=f'{theme}{"-mobile" if mobile else ""}.svg'
            outputs['island-'+suffix]=island(data,theme,mobile)
            outputs['monitor-'+suffix]=monitor(data,theme,mobile)
            outputs['terminal-'+suffix]=terminal(theme,mobile)
    # Collect and render everything before replacing any files. Failed fetches preserve last good snapshot.
    out.mkdir(parents=True,exist_ok=True)
    for name,content in outputs.items():
        temp=out/(name+'.tmp'); temp.write_text(content,encoding='utf-8'); temp.replace(out/name)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fetch',action='store_true')
    p.add_argument('--input',type=Path,default=ROOT/'assets/profile/snapshot.json')
    p.add_argument('--output-dir',type=Path,default=ROOT/'assets/profile')
    a=p.parse_args()
    data=collect() if a.fetch else json.loads(a.input.read_text())
    generate(data,a.output_dir)
    print('Generated profile snapshot: '+data['as_of'])


if __name__ == '__main__':
    main()
