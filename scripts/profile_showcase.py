#!/usr/bin/env python3
"""Render the self-contained profile showcase. No network or live metrics."""
import argparse
import base64
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(x, y, value, size=14, cls='', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{html.escape(str(value))}</text>'


def image_uri(appdir, name):
    raw = (appdir / name).read_bytes()
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Expected a PNG app icon: ' + name)
    return 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')


def render(theme, mobile=False, appdir=None):
    appdir = appdir or ROOT / 'assets/apps'
    icons = {name: image_uri(appdir, name + '.png') for name in ('dynamic-island', 'hwmonitor', 'clipshot')}
    w, h = (420, 620) if mobile else (900, 500)
    dark = theme == 'dark'
    bg, panel, fg, muted, line, accent, green = (
        ('#0d1017', '#141924', '#e8eaf2', '#9aa4b8', '#30384b', '#a69bf7', '#86c7ae') if dark else
        ('#f4f5fa', '#e9edf5', '#202638', '#59677b', '#bfc9dc', '#6756b3', '#26715a'))
    def rect(x,y,width,height,rx=8,cls='panel',extra=''):
        return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" class="{cls}" {extra}/>'
    def icon(name,x,y,size):
        return f'<image href="{icons[name]}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    def path(d,cls='line',extra=''):
        return f'<path d="{d}" class="{cls}" fill="none" {extra}/>'
    def heading(index, name, lines):
        b=text(28 if mobile else 44,74,str(index).zfill(2)+' / '+name,24 if mobile else 27,'strong')
        for i,value in enumerate(lines):b+=text(28 if mobile else 44,104+i*23,value,14 if mobile else 16,'muted')
        return b
    def frame(index,body,footer):
        bar=''
        for j in range(4):
            x=28+j*(w-56)/4
            d=f'M{x:.1f} {h-37}h{(w-72)/4:.1f}'
            bar+=f'<path d="{d}" stroke="{line}" stroke-width="2"/>'
            if j==index:
                bar+=f'<path class="chapter-progress" d="{d}" pathLength="1" stroke="{accent}" stroke-width="2" style="animation-delay:{index*7}s"/>'
        return f'<g class="scene s{index}">{body}{bar}'+text(44,h-18,footer,9 if mobile else 10,'mono muted')+'</g>'

    body = rect(.5,.5,w-1,h-1,16,'background')
    body += '<rect x="18" y="52" width="'+str(w-36)+'" height="'+str(h-110)+'" fill="url(#grid)" opacity=".35"/>'
    for x,y,sx,sy in [(16,16,1,1),(w-16,16,-1,1),(16,h-16,1,-1),(w-16,h-16,-1,-1)]:
        body+=path(f'M{x} {y+18*sy}V{y}h{18*sx}',extra='stroke-width="1.2"')
    body+=text(w-28,32,'gdfaler',12,'mono muted','text-anchor="end"')

    # Identity. All copy is factual and also available as text below the image.
    x=28 if mobile else 48
    identity=text(x,79,'PROFILE / NATIVE APPS',10,'mono accent intro-kicker','letter-spacing="2"')
    identity+=f'<defs><clipPath id="name-mask"><rect class="name-mask" x="{x}" y="85" width="230" height="75"/></clipPath></defs>'
    identity+='<g clip-path="url(#name-mask)">'+text(x,145,'Egor',54 if mobile else 66,'strong')+'</g>'
    identity+=path(f'M{x} 168h{220 if mobile else 290}','accent-stroke intro-rule', 'stroke-width="1.5" pathLength="1"')
    identity+='<g class="intro-subtitle">'
    if mobile:
        identity+=text(x,202,'macOS apps. Systems.',18,'muted')+text(x,229,'Graphics. Machine learning.',18,'muted')
        start,gap,keyx,valx=279,31,28,120
    else:
        identity+=text(x,208,'macOS apps. Systems. Graphics. ML.',23,'muted')
        start,gap,keyx,valx=269,32,48,157
    identity+='</g>'
    for i,(key,value) in enumerate([('study','CS @ BMSTU'),('native','Swift / SwiftUI / AppKit'),('exploring','Java / Python / C++'),('projects','apps, a voxel engine, a transformer')]):
        if mobile and key=='projects':value='apps / graphics / ML'
        identity+=f'<g class="intro-fact" style="animation-delay:{.48+i*.24:.2f}s">'+text(keyx,start+i*gap,key,11,'mono muted')+text(valx,start+i*gap,value,11 if mobile else 13,'mono')+'</g>'
    lx,ly,lw,lh=(112,418,196,116) if mobile else (620,162,220,157)
    identity+='<g class="intro-laptop">'
    identity+=rect(lx,ly,lw,lh,9,'outline intro-trace','pathLength="1"')+rect(lx+lw*.33,ly,lw*.34,13,5,'notch')
    identity+=path(f'M{lx-12} {ly+lh+8}h{lw+24}l-10 8h-{lw+4}z','line intro-trace','pathLength="1"')
    identity+=f'<defs><clipPath id="screen-glass"><rect x="{lx+3}" y="{ly+15}" width="{lw-6}" height="{lh-18}" rx="6"/></clipPath><linearGradient id="glass-sheen"><stop offset="0" stop-color="{fg}" stop-opacity="0"/><stop offset=".48" stop-color="{fg}" stop-opacity=".035"/><stop offset=".6" stop-color="{fg}" stop-opacity=".12"/><stop offset="1" stop-color="{fg}" stop-opacity="0"/></linearGradient></defs>'
    identity+=f'<g clip-path="url(#screen-glass)"><path class="intro-screen-sheen" d="M{lx-lw} {ly}h{lw*.6}l-{lh*.5} {lh}h-{lw*.6}z" fill="url(#glass-sheen)" style="--sheen-travel:{lw*2.7}px"/></g>'
    identity+='</g>'
    if not mobile:
        for i in range(3):
            tx=658+i*72
            identity+=path(f'M{lx+lw/2} {ly+lh+16}v4H{tx}v5','line intro-wire','pathLength="1"')
    for i,name in enumerate(('dynamic-island','hwmonitor','clipshot')):
        identity+=f'<g class="intro-app" style="animation-delay:{.7+i*.22:.2f}s"><g class="app-float" style="animation-delay:-{i*.65:.2f}s">'+icon(name,(147.5 if mobile else 638)+i*(48 if mobile else 72),552 if mobile else 349,29 if mobile else 40)+'</g></g>'
    body+=frame(0,identity,'Egor / CS student at BMSTU')

    # DynamicIsland: schematic of real functions, without fictitious media metadata.
    stage=heading(1,'DynamicIsland',['Music, timers and alerts', 'around the MacBook notch.'] if mobile else ['Music, timers and alerts around the MacBook notch.'])
    sx,sy,sw,sh=(30,192,360,211) if mobile else (52,166,536,254)
    stage+=rect(sx,sy,sw,sh,12,'outline')
    stage+=path(f'M{sx-8} {sy+sh+9}h{sw+16}l-14 8H{sx+6}z','line')
    cx=sx+sw/2;ny=sy-1;nw=210 if mobile else 254
    stage+=rect(cx-45,ny,90,24,10,'notch')
    stage+=f'<g class="island-shell">'+rect(cx-nw/2,ny,nw,96,25,'island')+'</g>'
    stage+='<g class="music-mode">'+text(cx-30,ny+34,'Music',15,'light strong')
    for i,height in enumerate((14,26,36,22,30,12)):
        stage+=f'<rect class="equalizer q{i%3}" x="{cx-68+i*9}" y="{ny+72-height}" width="4" height="{height}" rx="2" fill="#a69bf7"/>'
    stage+=f'<path d="M{cx+22} {ny+51}v18l14-9z" fill="#e8eaf2"/>'
    stage+=path(f'M{cx+46} {ny+52}v16m6-16v16','light-stroke','stroke-width="2"')+'</g>'
    stage+='<g class="timer-mode">'+f'<circle cx="{cx-45}" cy="{ny+47}" r="21" fill="none" stroke="#77708f" stroke-width="3"/>'
    stage+=f'<circle class="timer-ring" cx="{cx-45}" cy="{ny+47}" r="21" fill="none" stroke="#a69bf7" stroke-width="3" stroke-dasharray="84 48"/>'
    stage+=text(cx-9,ny+53,'Timer',17,'light strong')+'</g>'
    stage+='<g class="alert-mode">'
    stage+=path(f'M{cx-68} {ny+39}v-9a13 13 0 0 1 26 0v9M{cx-68} {ny+33}h5v12h-5zM{cx-47} {ny+33}h5v12h-5z','light-stroke','stroke-width="2"')
    stage+=text(cx-27,ny+40,'Headphones',14,'light strong')+'</g>'
    stage+=path(f'M{cx} {sy+104}v34h-{90 if mobile else 140}','accent-stroke','stroke-dasharray="3 5"')
    stage+=text(sx+20,sy+159,'a useful notch',12,'mono muted')
    if mobile:
        stage+=text(28,464,'Music controls / timers / system alerts',12,'mono')
        stage+=text(28,494,'Swift · SwiftUI',13,'muted')
        stage+=text(28,530,'DynamicIsland',12,'mono accent')
    else:
        for y,label in [(185,'IN THE APP'),(230,'Music controls'),(269,'Timers'),(308,'System alerts')]:
            stage+=text(650,y,label,11 if y==185 else 15,'mono muted' if y==185 else '')
        stage+=text(650,376,'Swift / SwiftUI',12,'mono muted')
    body+=frame(1,stage,'DynamicIsland / interface schematic')

    # HWMonitor: interfaces and capabilities only, never sample temperatures or rates.
    stage=heading(2,'HWMonitor',['A closer look at', 'Apple Silicon.'] if mobile else ['A closer look at Apple Silicon.'])
    cx,cy=(210,309) if mobile else (334,290)
    core=112 if mobile else 136
    stage+=rect(cx-core/2-9,cy-core/2-9,core+18,core+18,14,'core-halo')
    stage+='<g class="hw-core">'+rect(cx-core/2,cy-core/2,core,core,9,'outline')
    for i in range(7):
        k=(i-3)*12
        stage+=path(f'M{cx-core/2-8} {cy+k}h8M{cx+core/2} {cy+k}h8M{cx+k} {cy-core/2-8}v8M{cx+k} {cy+core/2}v8','line')
    stage+=icon('hwmonitor',cx-41,cy-41,82)+'</g>'
    boxes=[(26,220,'temperature'),(292,220,'power'),(26,366,'processes'),(292,366,'frequency')] if mobile else [(48,192,'temperature'),(486,192,'power'),(48,346,'processes'),(486,346,'frequency')]
    for i,(bx,by,label) in enumerate(boxes):
        bw=102 if mobile else 134
        stage+=rect(bx,by,bw,46,7,'outline sensor-node',f'style="animation-delay:-{i*.6:.1f}s"')+text(bx+bw/2,by+28,label,10 if mobile else 12,'mono','text-anchor="middle"')
        left=i%2==0;port=cx+(-core/2 if left else core/2);yy=cy+(-18 if i<2 else 18)
        edge=bx+bw if left else bx;mid=(port+edge)/2
        d=f'M{port} {yy}H{mid}V{by+23}H{edge}'
        stage+=path(d,'line')+path(d,'signal','stroke-width="1.8"')
        for packet in range(3):
            stage+=f'<circle class="bus-packet" r="2.6" fill="{accent if packet%2==0 else green}" style="offset-path:path(\'{d}\');animation-delay:-{i*.41+packet*.83:.2f}s"/>'
    if mobile:
        stage+=text(28,472,'SMC / IOReport / process statistics',12,'mono')
        stage+=text(28,503,'Temperatures, power and processes.',14,'muted')
        stage+=text(28,531,'Native Swift / Apple Silicon',12,'mono muted')
    else:
        stage+=text(668,188,'UNDER THE HOOD',10,'mono muted')
        for i,label in enumerate(('SMC','IOReport','Process statistics')):stage+=text(668,234+i*40,label,14,'mono')
        stage+=text(668,377,'Native Swift',12,'mono muted')
    body+=frame(2,stage,'HWMonitor / capability diagram')

    # TorrentPlayer: visual explanation of streaming, with its actual MVP status.
    stage=heading(3,'TorrentPlayer',['Local video playback +', 'BitTorrent streaming.'] if mobile else ['Local video playback + BitTorrent streaming.'])
    px,py,step=(34,246,18) if mobile else (68,236,23)
    for row in range(4):
        for col in range(4):
            stage+=rect(px+col*step,py+row*step,step-5,step-5,2,'piece '+('filled' if (col+row)%3 else ''),extra=f'style="animation-delay:-{(row*4+col)*.17:.2f}s"')
    bx,by,bw,bh=(159,253,89,58) if mobile else (253,248,112,69)
    stage+=rect(bx,by,bw,bh,7,'outline')
    for i in range(4):stage+=rect(bx+12+i*(bw-24)/4,by+18,(bw-32)/4,22,3,'buffer-cell',f'style="animation-delay:-{i*.35:.2f}s"')
    vx,vy,vw,vh=(291,236,101,84) if mobile else (454,215,140,112)
    stage+=rect(vx,vy,vw,vh,8,'outline')
    reel_step=32 if mobile else 44
    stage+=f'<defs><clipPath id="video-window"><rect x="{vx+5}" y="{vy+5}" width="{vw-10}" height="{vh-10}" rx="4"/></clipPath></defs><g clip-path="url(#video-window)"><g class="video-reel" style="--reel-step:-{reel_step}px">'
    for i in range(7):
        rx=vx-10+i*reel_step
        stage+=rect(rx,vy+10,reel_step-7,vh-20,4,'video-cell')
    stage+='</g></g>'
    stage+=f'<path class="play-symbol" d="M{vx+vw*.42} {vy+vh*.3}v{vh*.4}l{vw*.24}-{vh*.2}z" fill="{accent}"/>'
    for ax,ay,end in [(px+step*4+3,by+bh/2,bx-10),(bx+bw+10,by+bh/2,vx-10)]:
        stage+=path(f'M{ax} {ay}H{end}m-5-4 5 4-5 4','accent-stroke','stroke-width="1.3"')
        for packet in range(2 if mobile else 3):
            stage+=f'<rect class="stream-packet" x="-3" y="-3" width="6" height="6" rx="1.5" fill="{green}" style="offset-path:path(\'M{ax} {ay}H{end}\');animation-delay:-{packet*.62:.2f}s"/>'
    for tx,label in [(px+(step*3+step-5)/2,'pieces'),(bx+bw/2,'buffer'),(vx+vw/2,'playback')]:stage+=text(tx,358 if mobile else 365,label,11,'mono muted','text-anchor="middle"')
    if mobile:
        stage+=text(28,450,'Swift / AppKit / C++',13,'mono')
        stage+=text(28,481,'libtorrent / mpv',13,'mono muted')
        stage+=text(28,530,'EARLY MVP',11,'mono accent','letter-spacing="2"')
    else:
        stage+=text(660,186,'NATIVE PLAYER',11,'mono muted')
        stage+=text(660,232,'Swift / AppKit',13,'mono')+text(660,270,'C++ / libtorrent',13,'mono')+text(660,308,'mpv playback',13,'mono')
        stage+=text(660,377,'EARLY MVP',11,'mono accent','letter-spacing="2"')
    body+=frame(3,stage,'TorrentPlayer / streaming · early MVP' if mobile else 'TorrentPlayer / streaming architecture · early MVP')

    css = f':root{{--fg:{fg};--muted:{muted};--line:{line};--accent:{accent};--panel:{panel};--bg:{bg}}}' + '''
text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;fill:var(--fg)}
.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.strong{font-weight:650}
.muted{fill:var(--muted)}.accent{fill:var(--accent)}.background{fill:var(--bg)}.panel{fill:var(--panel)}
.outline{fill:var(--panel);stroke:var(--line);stroke-width:1.2}.line{stroke:var(--line)}.accent-stroke{stroke:var(--accent)}
.light{fill:#e8eaf2}.light-stroke{stroke:#e8eaf2}.notch,.island{fill:#07090f}.island{stroke:#665b9d;stroke-width:1.3}
.scene{opacity:0;animation:scene 28s ease-in-out infinite}.s0{opacity:1}.s1{animation-delay:7s}.s2{animation-delay:14s}.s3{animation-delay:21s}
@keyframes scene{0%{opacity:0;transform:translateY(4px)}3%,21.5%{opacity:1;transform:translateY(0)}25%,100%{opacity:0;transform:translateY(-4px)}}
.chapter-progress{stroke-dasharray:1;animation:chapter 28s linear infinite}
@keyframes chapter{0%{stroke-dashoffset:1}25%,100%{stroke-dashoffset:0}}
/* All entrance sequences share the 28-second scene clock, so they replay on every loop. */
.intro-kicker,.intro-subtitle,.intro-fact{animation:intro-reveal 28s ease both infinite}
.intro-subtitle{animation-delay:.22s}
@keyframes intro-reveal{0%,2%{opacity:0;transform:translateY(10px)}5%,23%{opacity:1;transform:translateY(0)}25%,100%{opacity:0;transform:translateY(-3px)}}
.name-mask{animation:name-type 28s cubic-bezier(.22,.61,.36,1) infinite}
@keyframes name-type{0%,1%{width:0;opacity:0;transform:translateY(6px)}8%,24%{width:230px;opacity:1;transform:translateY(0)}25%,100%{width:0;opacity:0}}
.intro-trace,.intro-rule,.intro-wire{stroke-dasharray:1;animation:trace 28s ease both infinite}
@keyframes trace{0%,1%{stroke-dashoffset:1}8%,24%{stroke-dashoffset:0}25%,100%{stroke-dashoffset:1}}
.intro-laptop{animation:laptop-assemble 28s cubic-bezier(.2,.7,.2,1) both infinite;animation-delay:.1s;transform-box:fill-box;transform-origin:center}
@keyframes laptop-assemble{0%,2%{opacity:0;transform:translateY(22px) scale(.94)}6%,24%{opacity:1;transform:translateY(0) scale(1)}25%,100%{opacity:0;transform:translateY(0) scale(1)}}
.intro-screen-sheen{animation:screen-sheen 7s cubic-bezier(.4,0,.2,1) infinite}
@keyframes screen-sheen{0%,18%{transform:translateX(0);opacity:0}28%{opacity:1}75%{transform:translateX(var(--sheen-travel));opacity:0}100%{transform:translateX(var(--sheen-travel));opacity:0}}
.intro-app{animation:app-arrive 28s cubic-bezier(.16,.9,.25,1) both infinite;transform-box:fill-box;transform-origin:center}
@keyframes app-arrive{0%,2%{opacity:0;transform:translateY(10px) scale(.94)}8%,24%{opacity:1;transform:translateY(0) scale(1)}25%,100%{opacity:0;transform:translateY(0) scale(1)}}
.app-float{animation:app-float 3.8s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
@keyframes app-float{to{transform:translateY(1.5px)}}
/* The notch contracts between three actual feature modes rather than just crossfading text. */
.island-shell{transform-box:fill-box;transform-origin:50% 0;animation:notch-morph 7s cubic-bezier(.4,0,.15,1) infinite}
@keyframes notch-morph{0%,4%,100%{transform:scale(.36,.25)}14%,34%{transform:scale(1,1)}41%,45%{transform:scale(.36,.25)}52%,69%{transform:scale(.86,1)}76%,78%{transform:scale(.36,.25)}85%,97%{transform:scale(.9,.65)}}
.music-mode{animation:music 7s ease infinite}.timer-mode{opacity:0;animation:timer 7s ease infinite}.alert-mode{opacity:0;animation:alert 7s ease infinite}
@keyframes music{0%,15%{opacity:0;transform:translateY(3px)}21%,29%{opacity:1;transform:translateY(0)}34%,100%{opacity:0;transform:translateY(-2px)}}
@keyframes timer{0%,53%{opacity:0;transform:translateY(3px)}58%,64%{opacity:1;transform:translateY(0)}69%,100%{opacity:0;transform:translateY(-2px)}}
@keyframes alert{0%,86%{opacity:0;transform:translateY(3px)}90%,93%{opacity:1;transform:translateY(0)}97%,100%{opacity:0;transform:translateY(-2px)}}
.equalizer{transform-box:fill-box;transform-origin:bottom;animation:eq .6s ease-in-out infinite alternate}.q1{animation-delay:-.2s}.q2{animation-delay:-.4s}
@keyframes eq{to{transform:scaleY(.2)}}.timer-ring{transform-box:fill-box;transform-origin:center;animation:turn 2.4s linear infinite}@keyframes turn{to{transform:rotate(360deg)}}
/* Packets follow the real connection paths in the schematic; no telemetry values are displayed. */
.signal{stroke:var(--accent);stroke-dasharray:10 130;animation:signal 2.5s linear infinite;opacity:.55}@keyframes signal{to{stroke-dashoffset:140}}
.bus-packet{offset-distance:100%;offset-rotate:0deg;animation:bus-packet 2.5s linear infinite}
@keyframes bus-packet{0%{offset-distance:100%;opacity:0}8%,92%{opacity:1}100%{offset-distance:0%;opacity:0}}
.core-halo{fill:none;stroke:var(--accent);stroke-width:1;transform-box:fill-box;transform-origin:center;animation:core-halo 2.5s ease-out infinite}
@keyframes core-halo{0%{opacity:.4;transform:scale(.92)}100%{opacity:0;transform:scale(1.16)}}
.sensor-node{animation:sensor-poll 2.5s ease infinite}@keyframes sensor-poll{0%,100%{stroke:var(--line)}45%{stroke:var(--accent)}}
.piece{fill:var(--panel);stroke:var(--line);stroke-width:1;animation:piece 2.8s ease-in-out infinite}.filled{fill:var(--accent)}
@keyframes piece{0%,100%{fill:var(--panel);opacity:.5}45%,60%{fill:var(--accent);opacity:1}}
.buffer-cell{fill:var(--accent);animation:buffer-shift 1.4s ease-in-out infinite}@keyframes buffer-shift{0%,100%{opacity:.2}50%{opacity:.9}}
.stream-packet{offset-distance:0%;offset-rotate:0deg;animation:stream-packet 1.8s linear infinite}
@keyframes stream-packet{0%{offset-distance:0%;opacity:0}12%,88%{opacity:1}100%{offset-distance:100%;opacity:0}}
.video-reel{animation:reel 1.8s linear infinite}@keyframes reel{to{transform:translateX(var(--reel-step))}}
.video-cell{fill:var(--accent);fill-opacity:.07;stroke:var(--accent);stroke-opacity:.16;stroke-width:1}
.play-symbol{transform-box:fill-box;transform-origin:center;animation:play-pulse 1.8s ease-in-out infinite}@keyframes play-pulse{0%,100%{opacity:.7;transform:scale(.94)}50%{opacity:1;transform:scale(1)}}
@media(prefers-reduced-motion:reduce){
*{animation:none!important}.scene{opacity:0;transform:none}.s0{opacity:1}
.intro-kicker,.intro-subtitle,.intro-fact,.intro-laptop,.intro-app{opacity:1!important;transform:none!important}
.name-mask{width:230px!important;opacity:1!important;transform:none!important}.intro-trace,.intro-rule,.intro-wire,.chapter-progress{stroke-dashoffset:0!important}
.intro-screen-sheen,.bus-packet,.stream-packet,.core-halo{display:none}
}
'''
    desc='Egor, gdfaler. CS student at BMSTU. Native macOS apps, systems, graphics and machine learning. Cycles through identity and original schematic illustrations of DynamicIsland, HWMonitor and TorrentPlayer. These illustrate application capabilities, not live measurements. TorrentPlayer is an early MVP. Full text and project links are below the image.'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">gdfaler / projects under the hood</title><desc id="desc">{html.escape(desc)}</desc><defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{line}" stroke-width=".45"/></pattern></defs><style>{css}</style>{body}</svg>'''



def badge(name, theme):
    width = 24 + len(name) * 7.2
    bg, fg, line = ('#0d1017','#a69bf7','#30384b') if theme=='dark' else ('#f4f5fa','#6756b3','#bfc9dc')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="28" viewBox="0 0 {width:.1f} 28" role="img" aria-labelledby="title"><title id="title">{html.escape(name)} repository</title><rect x=".5" y=".5" width="{width-1:.1f}" height="27" rx="7" fill="{bg}" stroke="{line}"/><text x="12" y="18" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="12" fill="{fg}">{html.escape(name)}</text></svg>'

def generate(out,appdir=None):
    files={f'showcase-{theme}{"-mobile" if mobile else ""}.svg':render(theme,mobile,appdir) for theme in ('dark','light') for mobile in (False,True)}
    for theme in ('dark','light'):
        for name in ('DynamicIsland','HWMonitor','TorrentPlayer','ClipShot'):
            files[f'link-{name.lower()}-{theme}.svg']=badge(name,theme)
    out.mkdir(parents=True,exist_ok=True)
    for name,content in files.items():
        temp=out/(name+'.tmp');temp.write_text(content,encoding='utf-8');temp.replace(out/name)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'assets/showcase')
    args=p.parse_args();generate(args.output_dir);print('Rendered showcase and project navigation SVGs.')
