<div align="center">

```
██████╗ ███████╗██████╗ ██╗  ██╗
██╔══██╗██╔════╝██╔══██╗██║ ██╔╝
██████╔╝█████╗  ██████╔╝█████╔╝ 
██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ 
██████╔╝███████╗██║  ██║██║  ██╗
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

</div>

---

```bash
$ whoami
> Berk Talha Aslan  |  berkaslan7988  |  Sivas Cumhuriyet University -> Information Systems and Technologies, 4th Year
> Developer · Security Enthusiast 
```

---

## ⚡ About

A curious CS student trying to keep software development and security under the same roof.

Every project I build is the foundation for the next one.

Currently working on **cybersecurity** & **software development** — from cryptography to ML-based detection systems, from single scripts to multi-agent AI.

---

## 🎡 Latest Release — `Night Fair`

> *A 64-game bilingual browser arcade — zero dependencies, playable right now*

```
Vanilla HTML/CSS/JS  —  no frameworks, no build step  —  GitHub Pages  —  bilingual (EN/TR)
```

| Feature | Details |
|---------|---------|
| 🕹️ 64 mini games | 7 categories: arcade, puzzle, word, brain, cards & dice, board-vs-bot, carnival |
| 🧠 Real algorithms | Sudoku generator with **unique-solution guarantee**, minimax bots, maze & spanning-tree generation, optimal Nim (XOR strategy) |
| 🎟️ Ticket economy | Cross-game tickets, best scores, favorites, deep links (`#g/snake`) — all persisted in localStorage |
| 🌐 Fully bilingual | `/en` and `/tr` share one engine; every game ships its own EN/TR strings — fix once, fixed in both |
| ⚙️ Tiny custom engine | Game registry, hash router, lifecycle cleanup (zero leaked timers/listeners), DPR-aware canvas, synthesized WebAudio SFX |
| 📱 Plays anywhere | Touch + keyboard controls, responsive layout, works offline from a single folder |

🎮 **Play:** [berkaslan7988.github.io/night-fair](https://berkaslan7988.github.io/night-fair/)
🔗 [**berkaslan7988/night-fair**](https://github.com/berkaslan7988/night-fair)

---

## 🛡️ Release — `NetSentinel`

> *Real-time ML-based network intrusion detection — Windows desktop*

```
Python + PySide6 + pyqtgraph  —  Scapy  —  scikit-learn + PyTorch  —  SQLite  —  bilingual (EN/TR)
```

| Feature | Details |
|---------|---------|
| 📡 Live detection | Scapy capture → bidirectional 5-tuple flows → 78 CIC-IDS2017 features → ML inference at **~9 ms/flow** |
| 🤖 Hybrid ML | RandomForest (F1 **0.9968**, FPR 0.11%) + IsolationForest + **PyTorch Autoencoder**; RF-weighted 0–100 risk score |
| 🚨 Smart alerts | Per-source-IP deduplication/aggregation, severity levels, attacker profiling — *no alarm floods* |
| 🖥️ Dashboard | Phosphor-green terminal-style PySide6 panel + pyqtgraph live charts; **live** or **CSV/DB replay** demo mode |
| 🧪 Tested | 75 unit/integration tests · safety-guarded attack simulator + benchmark · trained on CIC-IDS2017 (~2.36M flows) |
| 🛡️ Ethics-first | Own/lab network only; attack simulator refuses public targets and requires explicit confirmation |

🔗 [**berkaslan7988/NetSentinel**](https://github.com/berkaslan7988/NetSentinel)

---

## 📡 Release — `CyberSec Academy`

> *Interactive, bilingual (TR/EN) cybersecurity learning app — cross-platform*

```
Flutter + Dart  —  21 sections · 105 topics · 171 questions  —  Windows/Web/Linux/macOS/Android/iOS
```

| Feature | Details |
|---------|---------|
| 📚 Learn | 21 sections, 105 topics — concept + command examples + step-by-step mini-lab + defense & *common-mistake* notes |
| 🧪 Test | 171 questions across 6 types incl. **command writing** with flexible grading (flag-order independent, alias-aware, partial credit) |
| 🔁 Spaced repetition | Leitner box scheduler (1 → 3 → 7 → 16 → 35 days) with a *Today's Review* queue |
| 📊 Dashboard | Overall progress ring, stat cards, achievement badges, weak-area suggestions |
| 🌐 Bilingual + UX | Instant TR/EN switch · light/dark themes · full-text search · persistent progress |
| 🛡️ Ethics-first | Every offensive topic paired with a defense/detection counterpart — lab/authorized use only |

🔗 [**berkaslan7988/CyberSec-Academy**](https://github.com/berkaslan7988/CyberSec-Academy)

---

## 📶 Release — `NetScope`

> *Wi-Fi monitoring, analysis & defensive security — Windows desktop*

```
Python + PySide6 (Qt)  —  native WLAN API (ctypes)  —  SQLite  —  single-file .exe
```

| Feature | Details |
|---------|---------|
| 📶 Live scanning | Real RSSI via the native WLAN API, color-coded security, signal sparklines |
| 📊 Analytics | Signal-over-time charts, channel congestion scoring, best-channel advice |
| 🌐 LAN discovery | Device map, TCP port/service scan, bandwidth — *your own network only* |
| 🛡️ Security | Evil-twin / rogue-AP detection, per-network risk score, live alerts |
| 💾 History & reports | Persistent SQLite history + one-click CSV / PDF export |
| 🎨 UX | Dark/Light themes · real IEEE OUI vendor DB · 65 unit tests |

🔗 [**berkaslan7988/NetScope**](https://github.com/berkaslan7988/NetScope)

---

## 🗂️ Featured Project — `perfect_victory`

> *33 projects · 5 difficulty levels · Cryptography → Autonomous AI Agent*

A self-designed curriculum.

| Level | Theme | What's inside |
|-------|-------|----------------|
| `qwerty` | Cryptography & Fundamentals | Ciphers, hashing, OSINT, networking |
| `ytrewq` | Reverse Engineering & Pentest | Sockets, HTTP, memory manipulation |
| `zxcvbn` | Advanced Security + ML | Scapy, CVE scanning, scikit-learn models |
| `nbvcxz` | Full Applications | Multi-agent AI, E2EE messaging, security suite |
| `asdfgh` | Web Development | Flask, MVC, auth, e-commerce, forum |

🔗 [**berkaslan7988/perfect_victory**](https://github.com/berkaslan7988/perfect_victory)

---

## 📱 Release — `Person AI`

> *Multi-character AI chat app for Android*

```
Gemini · Groq · DeepSeek · OpenRouter  —  Python + Flet  —  APK included
```

| Feature | Details |
|---------|---------|
| 🎭 Character System | Custom personas + SillyTavern V2 import/export |
| ⚡ Streaming | Token-by-token responses with typing indicator |
| 🎨 Theming | Dark/Light + accent color picker |
| 💾 Persistence | SQLite, multi-session, session history & search |
| 🌐 Bilingual | Full TR/EN interface |

🔗 [**berkaslan7988/Person-AI**](https://github.com/berkaslan7988/Person-AI)

---

## 🏎️ Project — `PID-vehicle-simulation`

> *PID-controlled autonomous vehicle lane-following in Unity*

```
Unity 6  —  C#  —  Pure Pursuit + PID  —  Python (Matplotlib) reporting
```

| Feature | Details |
|---------|---------|
| 🎯 Control | Pure Pursuit + PID steering, live-tunable Kp/Ki/Kd |
| 🛣️ Route | 30-waypoint city + highway-ramp track with Laplacian smoothing |
| 📊 Telemetry | Real-time e(t)/u(t) charts, CSV logging, auto report generation |
| 🧮 Result | 1.51° avg tracking error, 3.21° RMS |

🔗 [**berkaslan7988/PID-vehicle-simulation**](https://github.com/berkaslan7988/PID-vehicle-simulation)

---

## 🗡️ Game — `Sunless Crown`

> *Procedural roguelite dungeon crawler in Godot 4*

```
Godot 4.7  —  GDScript  —  procedural generation  —  component architecture  —  custom shaders
```

| Feature | Details |
|---------|---------|
| 🎲 Procedural | Room+corridor generator with **flood-fill connectivity guarantee**, seeded |
| 🤖 Enemy AI | FSM-driven (idle/patrol/chase/attack); ranged, splitting & tank types |
| 👑 Bosses & story | 3 multi-phase bosses with telegraphed attacks + pre/post-fight dialogue |
| 🎒 Systems | Loot, inventory, equipment, 22 upgrades, XP/level, meta progression, JSON save |
| ✨ Juice | Screen shake, hit-stop, particles, damage numbers, shaders, object pooling |

🔗 [**berkaslan7988/sunless-crown**](https://github.com/berkaslan7988/2d-dungeon-crawler)

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50" height="50" alt="Python" title="Python"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" width="50" height="50" alt="PyTorch" title="PyTorch"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" width="50" height="50" alt="scikit-learn" title="scikit-learn"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg" width="50" height="50" alt="C#" title="C#"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="50" height="50" alt="JavaScript" title="JavaScript"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="50" height="50" alt="React" title="React"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" width="50" height="50" alt="Flask" title="Flask"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/qt/qt-original.svg" width="50" height="50" alt="Qt / PySide6" title="Qt / PySide6"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/unity/unity-original.svg" width="50" height="50" alt="Unity" title="Unity"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/godot/godot-original.svg" width="50" height="50" alt="Godot / GDScript" title="Godot / GDScript"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flutter/flutter-original.svg" width="50" height="50" alt="Flutter" title="Flutter"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dart/dart-original.svg" width="50" height="50" alt="Dart" title="Dart"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-original.svg" width="50" height="50" alt="Rust" title="Rust"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" width="50" height="50" alt="SQLite" title="SQLite"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" width="50" height="50" alt="HTML5" title="HTML5"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="50" height="50" alt="CSS3" title="CSS3"/>
</p>

```python
skills = {
    "security"  : ["scapy", "intrusion detection", "flow analysis", "packet analysis", "CVE scanning"],
    "ml / ai"   : ["scikit-learn", "PyTorch", "autoencoders", "anomaly detection",
                   "litellm", "ChromaDB", "multi-agent orchestration"],
    "control"   : ["PID tuning", "Pure Pursuit", "Unity physics (Rigidbody)", "telemetry & CSV/PDF reporting"],
    "game dev"  : ["Godot 4 / GDScript", "procedural generation", "FSM enemy AI",
                   "component architecture", "shaders & game juice", "object pooling",
                   "vanilla JS game engines", "minimax & puzzle generators"],
    "web"       : ["Flask", "React", "Vite", "Chart.js", "vanilla JS SPA", "i18n architecture"],
    "desktop"   : ["PySide6 / Qt", "Tauri", "C# UI"],
    "mobile"    : ["Flet", "Flutter / Dart"],
}
```

---

## 🧠 Interests

```
[x] Cybersecurity & Ethical Hacking  —  To understand the attack, to defend
[x] AI / Multi-Agent Systems          —  Where machines think together
[x] Game Development                  —  Where systems become play
[x] Software Architecture             —  Code needs architecture too
[x] Series & Films                    —  Sci-fi, Crime, Psychological Thriller, Fantastic 🎬
[x] Music                             —  Any genre, depends on the mood 🎧
[x] Sleep                             —  Takes too long, still optimizing..
```

---

## 📬 Reach Me

<p align="center">
  <a href="mailto:berkaslan7988@gmail.com">
    <img src="https://img.shields.io/badge/berkaslan7988@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
  &nbsp;
  <a href="https://github.com/berkaslan7988">
    <img src="https://img.shields.io/badge/berkaslan7988-181717?style=for-the-badge&logo=github&logoColor=white" />
  </a>
</p>

---

<div align="center">

*"The best way to understand a system is to try to break it."*

![Profile views](https://komarev.com/ghpvc/?username=berkaslan7988&color=green&style=flat-square)

</div>
