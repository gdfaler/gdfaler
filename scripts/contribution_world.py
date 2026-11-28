#!/usr/bin/env python3
"""Contribution World: dependency-free GitHub GraphQL → accessible animated SVG."""
import argparse
import calendar
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

QUERY = '''query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}'''
LEVELS = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']


def bounds(end):
    # Inclusive 365/366-day interval, including the current UTC date.
    year = end.year - 1
    start = dt.date(year, end.month, min(end.day, calendar.monthrange(year, end.month)[1])) + dt.timedelta(days=1)
    return start, end


def fetch(login, end, token):
    start, end = bounds(end)
    variables = dict(login=login, **{'from': start.isoformat()+'T00:00:00Z', 'to': end.isoformat()+'T23:59:59Z'})
    request = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps(dict(query=QUERY, variables=variables)).encode(),
        headers={'Authorization': 'Bearer '+token, 'Content-Type': 'application/json',
                 'User-Agent': 'contribution-world/1.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get('errors'):
                raise ValueError('GitHub GraphQL returned errors; no output updated')
            user = payload.get('data', {}).get('user')
            if not user or user['login'].lower() != login.lower():
                raise ValueError('GitHub user not found or mismatched')
            return {'login': user['login'], 'source': 'github-graphql',
                    'calendar': user['contributionsCollection']['contributionCalendar']}
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == 2:
                raise ValueError('GitHub HTTP %s; check token permissions/rate limit' % error.code) from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise ValueError('GitHub network request failed; no output updated') from None
        time.sleep(2 ** attempt)


def demo():
    start, end = bounds(dt.date(2026, 11, 27))
    days = []
    for i in range((end-start).days+1):
        date = start + dt.timedelta(days=i)
        n = int(24 * max(0, math.sin(i*.043)+.25*math.sin(i*.31)) ** 2)
        if i % 11 < 3:
            n = 0
        level = 0 if not n else min(4, 1+int(math.log2(n+1)/1.4))
        days.append(dict(date=date.isoformat(), weekday=(date.weekday()+1)%7,
                         contributionCount=n, contributionLevel=LEVELS[level]))
    weeks = []
    for day in days:
        if not weeks or day['weekday'] == 0:
            weeks.append(dict(contributionDays=[]))
        weeks[-1]['contributionDays'].append(day)
    return dict(login='gdfaler', source='synthetic-demo', calendar=dict(
        totalContributions=sum(d['contributionCount'] for d in days), weeks=weeks))


def validate(data):
    if data.get('source') not in ('github-graphql', 'synthetic-demo'):
        raise ValueError('Missing or unsupported data source')
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}', data.get('login', '')):
        raise ValueError('Invalid login')
    days = [d for w in data['calendar']['weeks'] for d in w['contributionDays']]
    if not 1 <= len(days) <= 366:
        raise ValueError('Expected 1–366 calendar days')
    dates = []
    for day in days:
        date = dt.date.fromisoformat(day['date'])
        count = day['contributionCount']
        if type(count) is not int or count < 0 or day['contributionLevel'] not in LEVELS:
            raise ValueError('Invalid count or contribution level')
        if day['weekday'] != (date.weekday()+1)%7:
            raise ValueError('Invalid weekday')
        if (count == 0) != (day['contributionLevel'] == 'NONE'):
            raise ValueError('Count and level disagree')
        dates.append(date)
    if dates != sorted(set(dates)) or any((b-a).days != 1 for a,b in zip(dates,dates[1:])):
        raise ValueError('Dates must be unique, consecutive, and ascending')
    if data['calendar']['totalContributions'] != sum(d['contributionCount'] for d in days):
        raise ValueError('Calendar total does not match daily counts')
    return days


def height(count):
    return 3 if count == 0 else 9 + 11 * math.log2(count+1)


def render(data, theme):
    days = validate(data)
    dark = theme == 'dark'
    bg, fg, muted, line, accent = ('#0d1017','#e8eaf2','#9aa4b8','#30384b','#a69bf7') if dark else ('#f4f5fa','#202638','#59677b','#bfc9dc','#6756b3')
    top = ['#252c3c','#6b6397','#8175bb','#a69bf7','#d6cffb'] if dark else ['#dde2ed','#b6acd9','#9b8cc9','#7c69b7','#6756b3']
    left, right = ('#393449','#242337') if dark else ('#b4a9d0','#9382b7')
    origin = dt.date.fromisoformat(days[0]['date'])
    origin -= dt.timedelta(days=(origin.weekday()+1)%7)
    weeks = (dt.date.fromisoformat(days[-1]['date'])-origin).days//7+1
    step = 960 / weeks
    scale = min(1.0, 26 / max(height(d['contributionCount']) for d in days))
    def point(w,r): return (116+(w+.5)*step, 290+r*42)
    def poly(points, fill, opacity=1):
        return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" fill-opacity="{opacity}" stroke="{line}" stroke-width=".65" stroke-linejoin="round"/>'
    parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 680" width="1120" height="680" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(data['login'])} / Contribution calendar</title>
<desc id="desc">{'SYNTHETIC DEMO, not real activity. ' if data['source']=='synthetic-demo' else 'GitHub GraphQL contribution calendar. '}A front-facing calendar grid with raised 3D columns, one position per day. Week columns run horizontally from left to right. Seven labelled weekday rows run vertically, Sunday to Saturday. Month brackets align with the week containing each month's first included date; boundary weeks can contain days from both months. Zero days are flat outlined markers. Nonzero column height is logarithmic in the real count; top-face color follows the five GitHub activity levels. No decorative terrain or simulated data.</desc>
<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{line}" stroke-width=".45"/></pattern><linearGradient id="column-left" x2="0" y2="1"><stop stop-color="{left}" stop-opacity=".95"/><stop offset="1" stop-color="{left}" stop-opacity=".25"/></linearGradient><linearGradient id="column-right" x2="0" y2="1"><stop stop-color="{right}" stop-opacity=".95"/><stop offset="1" stop-color="{right}" stop-opacity=".3"/></linearGradient></defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.heading{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}}.array-scan{{animation:scan 12s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes scan{{0%,100%{{opacity:.08}}50%{{opacity:.5}}}}@media(prefers-reduced-motion:reduce){{.array-scan{{animation:none;opacity:.25}}}}</style>
<rect x=".5" y=".5" width="1119" height="679" rx="16" fill="{bg}" stroke="{line}"/>
<rect x="18" y="52" width="1084" height="518" fill="url(#grid)" opacity=".35"/>
<path d="M16 34V16h18M1086 16h18v18M16 646v18h18M1086 664h18v-18" fill="none" stroke="{line}" stroke-width="1.2"/>
<text x="44" y="53" fill="{accent}" font-size="11" letter-spacing="2">ACTIVITY / CONTRIBUTION CALENDAR</text>
<text x="44" y="94" fill="{fg}" font-size="30" font-weight="650" class="heading">Contribution calendar</text>
<text x="44" y="124" fill="{muted}" font-size="12">{days[0]['date']} — {days[-1]['date']} / {sum(d['contributionCount'] for d in days):,} contributions</text>''']
    label='SYNTHETIC DEMO · NOT REAL ACTIVITY' if data['source']=='synthetic-demo' else 'GITHUB GRAPHQL · SNAPSHOT'
    parts.append(f'<text x="1076" y="53" text-anchor="end" fill="{muted}" font-size="10">{label}</text>')
    active=sum(d['contributionCount']>0 for d in days)
    peak=max(d['contributionCount'] for d in days)
    for x,value,label in [(44,active,'ACTIVE DAYS'),(236,peak,'PEAK / DAY')]:
        parts.append(f'<path d="M{x} 154v37" stroke="{accent}" stroke-opacity=".55"/><text x="{x+13}" y="170" fill="{fg}" font-size="19">{value}</text><text x="{x+13}" y="188" fill="{muted}" font-size="9" letter-spacing="1">{label}</text>')
    parts.append(f'<text x="1076" y="181" text-anchor="end" fill="{muted}" font-size="11">ONE POSITION / ONE DAY</text>')
    parts.append(f'<text x="1076" y="213" text-anchor="end" fill="{muted}" font-size="10">WEEKS → / DAYS ↓</text>')
    # Familiar calendar coordinates. Depth belongs to the bars, not the time axes.
    for w in range(weeks+1):
        x=116+w*step
        parts.append(f'<path d="M{x:.2f} 258V552" stroke="{line}" stroke-width=".6" fill="none" opacity=".4"/>')
    for r in range(8):
        y=258+r*42
        parts.append(f'<path d="M116 {y}H1076" stroke="{line}" stroke-width=".6" fill="none" opacity=".6"/>')
    # Each month starts at the week containing its first included date, as on GitHub.
    # Brackets share the exact grid column boundaries rather than floating in space.
    months=[]
    for day in days:
        date=dt.date.fromisoformat(day['date'])
        if not months or (date.year,date.month)!=months[-1][0]:
            week=(date-origin).days//7
            months.append(((date.year,date.month),week,date.strftime('%b')))
    for i,((year,month),start,label) in enumerate(months):
        end=months[i+1][1] if i+1<len(months) else weeks
        if end<=start:continue
        x1,x2=116+start*step+2,116+end*step-2
        if month==1:label+=f" ’{str(year)[-2:]}"
        parts.append(f'<g class="month" data-start-week="{start}" data-end-week="{end}"><title>{year}-{month:02d}: week-column range; month boundaries can share a week</title><text x="{(x1+x2)/2:.2f}" y="235" fill="{muted}" font-size="10" text-anchor="middle">{label}</text><path d="M{x1:.2f} 242v5H{x2:.2f}v-5" fill="none" stroke="{line}" stroke-width="1"/></g>')
    for r,label in enumerate(('SUN','MON','TUE','WED','THU','FRI','SAT')):
        _,y=point(0,r)
        parts.append(f'<text class="weekday" data-weekday="{r}" x="98" y="{y-9}" fill="{muted}" font-size="10" text-anchor="end">{label}</text>')
    tiles=[]
    for day in days:
        date=dt.date.fromisoformat(day['date']);w=(date-origin).days//7;r=day['weekday']
        tiles.append((r,w,r,day))
    for _,w,r,day in sorted(tiles):
        n=day['contributionCount'];level=LEVELS.index(day['contributionLevel']);x,y=point(w,r)
        z=height(n)*scale if n else 0
        half,depth=4.8,3.4
        # Front and right faces plus the shallow top face form a small 3D pillar.
        a,b,c,d=(x-half,y-z),(x+half,y-z),(x+half+depth,y-z-depth),(x-half+depth,y-z-depth)
        parts.append(f'<g data-date="{day["date"]}" data-count="{n}" data-level="{level}" data-height="{z:.3f}" data-week="{w}" data-weekday="{r}" data-x="{x:.3f}" data-baseline="{y:.3f}"><title>{day["date"]}: {n} contributions</title>')
        if n:
            parts.append(poly([a,b,(x+half,y),(x-half,y)],'url(#column-left)'))
            parts.append(poly([b,c,(x+half+depth,y-depth),(x+half,y)],'url(#column-right)'))
            parts.append(poly([a,b,c,d],top[level]))
            parts.append(f'<path d="M{x-half} {y-z}H{x+half}l{depth}-{depth}" fill="none" stroke="{accent}" stroke-width=".8" opacity=".65"/>')
        else:
            parts.append(poly([a,b,c,d],top[0],.22))
        parts.append('</g>')
    parts.append(f'<path class="array-scan" d="M1076 258V552" stroke="{accent}" stroke-width="1.3" fill="none"/>')
    parts.append(f'<path d="M44 578H1076" stroke="{line}"/><text x="44" y="606" fill="{fg}" font-size="12">COLUMN HEIGHT / log₂(contributions + 1)</text>')
    for i,label in enumerate(['0 / none','1 / low','2 / medium','3 / high','4 / peak']):
        x=44+i*167
        parts.append(f'<rect x="{x}" y="626" width="10" height="10" rx="2" fill="{top[i]}"/><text x="{x+18}" y="635" font-size="11" fill="{muted}">{label}</text>')
    parts.append(f'<text x="1076" y="654" text-anchor="end" fill="{muted}" font-size="10">Height: 9 + 11 × log₂(n + 1), uniformly scaled to fit / color: GitHub levels</text></svg>')
    return '\n'.join(parts)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--login',default='gdfaler')
    source=p.add_mutually_exclusive_group()
    source.add_argument('--demo',action='store_true')
    source.add_argument('--input',type=Path,help='Previously saved normalized calendar JSON')
    p.add_argument('--end',type=dt.date.fromisoformat,default=dt.datetime.now(dt.timezone.utc).date())
    p.add_argument('--output-dir',type=Path,default=Path('assets/contribution-world'))
    args=p.parse_args(argv)
    try:
        if not re.fullmatch(r'[A-Za-z0-9-]{1,39}',args.login):
            raise ValueError('Invalid login')
        if args.demo:
            data=demo()
        elif args.input:
            data=json.loads(args.input.read_text())
        else:
            token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
            if not token:
                raise ValueError('Set GH_TOKEN or GITHUB_TOKEN; use --demo only for synthetic previews')
            data=fetch(args.login,args.end,token)
        if data['login'].lower()!=args.login.lower():
            raise ValueError('Input login does not match --login')
        validate(data)
        outputs={f'world-{theme}.svg':render(data,theme) for theme in ('dark','light')}
        outputs['calendar.json']=json.dumps(data,indent=2)+'\n'
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for name,content in outputs.items():
            temporary=args.output_dir/(name+'.tmp')
            temporary.write_text(content,encoding='utf-8')
            temporary.replace(args.output_dir/name)
        print(f'Generated {data["source"]} world in {args.output_dir}')
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(f'Contribution World: {error}',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
