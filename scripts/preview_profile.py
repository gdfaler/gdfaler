#!/usr/bin/env python3
"""Standalone local visual QA page; no runtime dependencies."""
from pathlib import Path
import html
import subprocess
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'work'; out.mkdir(exist_ok=True)
world={name:subprocess.check_output(['git','show','origin/contribution-world:'+name],cwd=ROOT).decode() for name in ('world-dark.svg','world-light.svg')}
for name,content in world.items(): (out/name).write_text(content)
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>gdfaler · profile preview</title><style>body{margin:0;font:16px system-ui}main{max-width:900px;margin:auto;padding:24px}img{max-width:100%;height:auto}section{padding:24px 0}h1{font-size:42px}p{line-height:1.7}.dark{background:#0d1117;color:#e6edf3}.light{background:#fff;color:#1d352d}a{color:#479d72}.cards{display:flex;flex-wrap:wrap;gap:12px}.cards img{width:420px}</style>']
for theme in ('dark','light'):
 parts += [f'<section class="{theme}"><main>',f'<img src="../assets/profile/island-{theme}.svg"><h1>Heya, I’m Egor.</h1><p>Building things. Breaking things. Understanding things.</p><p>CS student at BMSTU. Native macOS apps, systems, machine learning and the occasional reinvention.</p><p>Selected work: HWMonitor · DynamicIsland · TorrentPlayer · ClipShot</p>']
 parts += ['<h2>Developer Monitor</h2>',f'<img src="../assets/profile/monitor-{theme}.svg"><h2>Contribution World</h2><img src="world-{theme}.svg"><h2>One more process</h2><img src="../assets/profile/terminal-{theme}.svg"></main></section>']
(out/'profile-preview.html').write_text('\n'.join(parts))
print(out/'profile-preview.html')
