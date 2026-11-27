#!/usr/bin/env python3
"""Contribution World: dependency-free GitHub GraphQL → accessible animated SVG."""
import argparse
import calendar
import datetime as dt
import hashlib
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
    bg, fg, muted = ('#0d141d','#e6edf3','#95a8ba') if dark else ('#f4f7f3','#1d352d','#536b61')
    colors = ['#407f9d','#a9cc74','#74b65b','#43914e','#b0bac0']
    origin = dt.date.fromisoformat(days[0]['date'])
    origin -= dt.timedelta(days=(origin.weekday()+1)%7)
    vertical_scale = min(1.0, 105 / max(height(d['contributionCount']) for d in days))
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 680" width="1120" height="680" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(data['login'])} / Contribution World</title>
<desc id="desc">{'SYNTHETIC DEMO, not real activity. ' if data['source']=='synthetic-demo' else 'GitHub GraphQL contribution calendar. '}One tile per day, weeks left to right, Sunday to Saturday frontward. Height is logarithmic in contributions; color follows GitHub contribution levels. Trees are decorative.</desc>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.cloud{{animation:drift 20s ease-in-out infinite alternate}}.cloud.slow{{animation-duration:28s}}@keyframes drift{{to{{transform:translateX(24px)}}}}@media(prefers-reduced-motion:reduce){{.cloud{{animation:none}}}}</style>
<rect width="1120" height="680" rx="24" fill="{bg}"/>
<text x="44" y="53" fill="{muted}" font-size="12" letter-spacing="3">GDFALER / UNDER THE HOOD</text>
<text x="44" y="94" fill="{fg}" font-size="30" font-weight="700">Contribution World</text>
<text x="44" y="124" fill="{muted}" font-size="12">{days[0]['date']} — {days[-1]['date']} · {sum(d['contributionCount'] for d in days):,} contributions</text>''']
    label = 'SYNTHETIC DEMO · NOT REAL ACTIVITY' if data['source']=='synthetic-demo' else 'LIVE DATA · GITHUB GRAPHQL'
    parts.append(f'<text x="1076" y="53" text-anchor="end" fill="{muted}" font-size="11">{label}</text>')
    def poly(points, color):
        return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{color}" stroke="{bg}" stroke-width=".45" stroke-linejoin="round"/>'
    def cube(x,y,z,rx,ry,depth,top,left,right):
        a,b,c,d=(x,y-z-ry),(x+rx,y-z),(x,y-z+ry),(x-rx,y-z)
        return poly([d,c,(c[0],c[1]+depth),(d[0],d[1]+depth)],left)+poly([c,b,(b[0],b[1]+depth),(c[0],c[1]+depth)],right)+poly([a,b,c,d],top)
    tiles=[]
    for day in days:
        date=dt.date.fromisoformat(day['date']); w=(date-origin).days//7; r=day['weekday']
        tiles.append((w+r,w,r,day))
    for _,w,r,day in sorted(tiles):
        n=day['contributionCount']; level=LEVELS.index(day['contributionLevel']); z=height(n)*vertical_scale
        x=180+(w-r)*15.5; y=205+(w+r)*5.8
        parts.append(f'<g data-date="{day["date"]}" data-count="{n}" data-level="{level}"><title>{day["date"]}: {n} contributions</title>')
        parts.append(cube(x,y,z,15.5,5.8,z+12,colors[level], '#665e52' if n else '#2b627c', '#494c48' if n else '#224d66'))
        if n:
            # A thin grass/stone cap leaves the earthen column visible.
            parts.append(cube(x,y,z,15.5,5.8,3,colors[level], '#537b47' if level<4 else '#7d8c94', '#3b643c' if level<4 else '#626f79'))
        else:
            parts.append(f'<path d="M{x-5:.2f} {y-z:.2f}l6 2 5-2" fill="none" stroke="#9acbd5" stroke-width=".8" opacity=".7"/>')
        seed=int(hashlib.sha256(day['date'].encode()).hexdigest()[:8],16)
        if level in (2,3) and seed%5==0:
            parts.append(cube(x,y-z-13,0,2.3,1.2,10,'#9b7751','#73533b','#543d30'))
            parts.append(cube(x,y-z-13,0,9,3.8,12,'#5c9d62','#2e714d','#23583e'))
            parts.append(cube(x,y-z-23,0,6,2.8,7,'#79b973','#438758','#316b4a'))
        if level==4:
            parts.append(poly([(x-5,y-z),(x,y-z-5),(x+5,y-z)],'#dde4df'))
        parts.append('</g>')
    # Clouds stay above the tallest terrain, with a static fallback and reduced-motion support.
    for x,y,klass in [(350,158,'cloud'),(770,183,'cloud slow'),(925,143,'cloud')]:
        parts.append(f'<g class="{klass}" opacity="{.45 if dark else .9}"><path d="M{x} {y}h64v-9h-13v-9h-29v7h-22z" fill="{ "#718799" if dark else "#d7e4df"}"/></g>')
    parts.append(f'<path d="M44 578H1076" stroke="{muted}" opacity=".2"/><text x="44" y="606" fill="{fg}" font-size="12">ONE DAY. ONE BLOCK. A WORLD BUILT BY SHOWING UP.</text>')
    for i,name in enumerate(['Water / 0','Grass / low','Meadow','Forest','Stone / high']):
        x=44+i*167
        parts.append(f'<rect x="{x}" y="626" width="10" height="10" rx="2" fill="{colors[i]}"/><text x="{x+18}" y="635" font-size="11" fill="{muted}">{name}</text>')
    parts.append(f'<text x="1076" y="662" text-anchor="end" fill="{muted}" font-size="10">log-scaled height · GitHub activity levels · decorative trees</text></svg>')
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
