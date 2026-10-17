# Heya, I'm Egor

Student at BMSTU. I like building things from scratch to see how they work inside: a Minecraft-style game with no engine, a language model with no library doing the hard part, and lately native macOS apps that dig into the hardware. Trying to get into mobile dev next.

<img src="https://img.shields.io/badge/Swift-F05138?style=flat-square&logo=swift&logoColor=white" alt="Swift"> <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java"> <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white" alt="C++">

## 🏆 Achievements

- 🥇 **Winner**, "City Energy—In Action" hackathon («Энергия города — в дело»)
- 🏅 **Prize winner**, Moscow Pre-Professional Olympiad for Schoolchildren 2026, research sector
- 🏅 **Prize winner**, RTU MIREA Multidisciplinary Olympiad 2026, Computer Science track
- 🎓 Yandex Lyceum, "Fundamentals of Python Programming" (2025–2026)

## 🍎 macOS apps

<table>
<tr>
<td width="33%" valign="top">
<a href="https://github.com/gdfaler/HWMonitor"><img src="https://raw.githubusercontent.com/gdfaler/HWMonitor/main/docs/social-preview.png" alt="HWMonitor"></a>
<p><b><a href="https://github.com/gdfaler/HWMonitor">HWMonitor</a></b><br>
Hardware monitor for Apple Silicon: every SMC temperature sensor (115 on an M5), per-core frequencies, power draw. A MacBook Air has no fan, so it cools the chip by moving the heaviest background apps to efficiency cores. Under the same test load, that took the chip from 92–101 °C down to about 50 °C.</p>
</td>
<td width="33%" valign="top">
<a href="https://github.com/gdfaler/DynamicIsland"><img src="https://raw.githubusercontent.com/gdfaler/DynamicIsland/main/assets/social-preview.png" alt="DynamicIsland"></a>
<p><b><a href="https://github.com/gdfaler/DynamicIsland">DynamicIsland</a></b><br>
Turns the MacBook notch into an iPhone-style dynamic island: now playing from Music, Spotify or Safari, a visualizer that moves to the actual sound (FFT), a timer, and alerts for charging, volume and headphones. No private APIs.</p>
</td>
<td width="33%" valign="top">
<a href="https://github.com/gdfaler/ClipShot"><img src="https://raw.githubusercontent.com/gdfaler/ClipShot/main/docs/social-preview.png" alt="ClipShot"></a>
<p><b><a href="https://github.com/gdfaler/ClipShot">ClipShot</a></b><br>
Press ⇧⌘1 or ⇧⌘S and the screenshot goes straight to the clipboard, so nothing piles up on the desktop. A tiny menu bar app in under 900 lines of Swift.</p>
</td>
</tr>
</table>

All three are native Swift with zero dependencies and build with one script, no Xcode needed. HWMonitor and ClipShot have ready-to-run builds in Releases.

## 🎮 Games

### 🧱 [MineAndCraft](https://github.com/gdfaler/MineAndCraft)
Minecraft, except I wrote every block of it. The world is infinite and generated from a seed: hills, caves, ores, forests, all streamed in chunks on background threads. It saves when you quit and remembers your settings. Java + LWJGL, straight OpenGL, no engine.

Mojang, please don't sue.

### 🐻 [Five Nights On Your Own](https://github.com/gdfaler/FiveNightOnYourOwn)
FNaF where Freddy is literally the letter F. Cameras, doors, lights, power, six nights, all drawn in ASCII inside a JavaFX window that pretends to be an old terminal.

## 🧪 Other stuff

### 🧠 [GDF AI](https://github.com/gdfaler/gdf_ai)
I built my own ChatGPT. It has 3 million parameters and has read 30 KB of text in its whole life, so it's not very smart, but it's trying its best. Under the hood it's a LLaMA-style transformer I wrote from scratch in PyTorch, with its own tokenizer and a Flask web chat. Trains in under a minute, runs offline.

- 💬 [Vneurochka](https://github.com/gdfaler/vneurochka2025): Android app for school clubs, with accounts and chat on Firebase. Made with a teammate for the "Potential" 2025 competition.
- ⚙️ [arraylib](https://github.com/gdfaler/arraylib): calculates sums, averages and medians of arrays. Has CMake, unit tests, integration tests and CI. Overkill? Yes.

```text
loop. fail. upgrade. repeat.
```
