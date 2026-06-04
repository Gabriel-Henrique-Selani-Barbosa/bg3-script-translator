# BG3 Script Translator

---

## Description

**BG3 Script Translator** is a cross-platform localization tool that automatically translates Baldur's Gate 3 mod files to any language using Google Translate.

Whether you want to play a mod in your native language or share your own mod with a global audience, this tool handles the heavy lifting: it extracts `.pak` files, translates `.loca` and `.xml` localization data, protects game tags and placeholders, and repacks everything back into a working `.pak` — all in a few clicks.

No manual file editing. No external converters. Just select your mod, pick a language, and translate.

---

## Installation Instructions

### Windows

1. Download and install **Python 3.8+** from [python.org](https://python.org/downloads)
   - Check **"Add Python to PATH"** during installation
2. Extract the translator to any folder
3. Double-click `setup.bat` to install dependencies
4. Launch the GUI: double-click `tradutor_bg3_gui.py`

### Linux (Bazzite / Fedora / Debian / Arch)

```bash
# 1. Extract the translator
# 2. Run the installer
chmod +x setup.sh
./setup.sh

# 3. Launch
python3 tradutor_bg3_gui.py
```

### Optional: Generate Standalone .exe (Windows Only)

If you want to share the tool without requiring Python:

1. Double-click `build_exe.bat`
2. Two files will be generated:
   - `Tradutor_BG3.exe` — CLI version
   - `Tradutor_BG3_GUI.exe` — GUI version (no terminal window)
3. Share these `.exe` files — no Python installation needed!

---

## Main Features

- **Modern Dark GUI** — Clean, responsive interface built with CustomTkinter
- **CLI Mode** — Full terminal support for scripting and automation
- **.pak Extraction & Repacking** — Works natively on Windows; on Linux, auto-detects Bottles/Wine
- **Batch Translation** — Translate an entire folder of mods in one run
- **Auto Language Detection** — Detects source language from folder names (`English/`, `Spanish/`, `Japanese/`, etc.)
- **Built-in LOCA Converter** — Convert `.loca` / `.locas` ↔ XML without external tools
- **Tag Protection** — Preserves `<content>`, `LSTags`, placeholders `[1]`, and line breaks during translation
- **Persistent Config** — Saves your settings to JSON in the script folder
- **Multilingual UI** — Interface available in **Portuguese**, **English**, and **Spanish**
- **Automatic Backups** — Original `.pak` files are saved to a `_backups/` folder before overwriting
- **Silent Operations** — On Windows, no CMD windows flash during `.pak` extraction or repacking
- **Cross-Platform** — Windows (native) and Linux (via Bottles Flatpak)

---

## Requirements

- **Python 3.8 or newer**
- **Internet connection** (for Google Translate API)
- **LSLib / Divine.exe** — Only needed if translating `.pak` files directly
  - Download: [Norbyte/lslib](https://github.com/Norbyte/lslib/releases)
  - On Linux: Bottles with `dotnetcoredesktop8` dependency

### Python Dependencies (auto-installed by setup scripts)

```
deep-translator>=1.11.0
customtkinter>=5.2.0
```

---

## Shout Outs

- **Norbyte** — For [LSLib](https://github.com/Norbyte/lslib), the essential toolkit for BG3 modding that powers `.pak` extraction and repacking
- **Google Translate** — Via [deep-translator](https://github.com/nidhaloff/deep-translator) by Nidhaloff
- **CustomTkinter** — For the modern, dark-themed GUI components
- **Larian Studios** — For creating Baldur's Gate 3 and supporting the modding community

---

## Links

- [Source Code & Issues](https://github.com/Gabriel-Henrique-Selani-Barbosa/bg3-script-translator)
- [LSLib Releases](https://github.com/Norbyte/lslib/releases)
