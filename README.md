# BG3 Translator - Automatic Localization

Translates XML and `.loca` files for **Baldur's Gate 3** mods automatically via Google Translate.

Features a **modern dark GUI** (CustomTkinter) and **.pak support on Linux via Bottles**.

Supports **any language pair**. The script auto-detects the source language from the mod folder name and lets you choose the target language.

Protects `<content>`, `LSTags`, placeholders `[1]`, and line breaks during translation.

---

## Features

- **Graphical Interface (GUI)** with modern dark theme using CustomTkinter
- **Terminal Mode (CLI)** for command-line users
- **.pak support on Linux** via Bottles/Wine (auto-detects and uses Divine.exe)
- **Batch Mode** — translate multiple mods at once
- **Automatic language detection** from folder name (`English/`, `Japanese/`, etc.)
- **Built-in .loca converter** — no external tool needed
- **Persistent settings** saved in JSON (always in the script folder)
- **.exe generator** for Windows (`build_exe.bat`)
- **Multilingual UI** — interface in Portuguese, English, or Spanish

---

## Requirements

- **Python 3.8+** (https://python.org/downloads)
  - Windows: check `Add Python to PATH` during installation
- Internet connection (for Google Translate)

### Python Dependencies

```
deep-translator>=1.11.0
customtkinter>=5.2.0
```

---

## Installation (first time)

### Windows

1. Download and install Python 3: https://python.org/downloads
2. Extract the translator ZIP to a folder
3. Run the installer:
```cmd
setup.bat
```

### Linux (Bazzite/Fedora/Debian/Arch)

```bash
cd script-folder
chmod +x setup.sh
./setup.sh
```

On **Bazzite** (or other immutable systems), if `tkinter` is not installed:
```bash
rpm-ostree install python3-tkinter
# reboot
```

### Mac

```bash
cd script-folder
chmod +x setup.sh
./setup.sh
```

---

## How to Use

> **Note:** The `setup.bat` / `setup.sh` scripts automatically create a Python virtual environment (`venv` folder) in the script's directory. You do **not** need to create it manually.

### GUI Mode (Recommended)

#### Windows
```cmd
venv\Scripts\python tradutor_bg3_gui.py
```
Or double-click `tradutor_bg3_gui.py` if Python is associated.

#### Linux / Mac
```bash
venv/bin/python tradutor_bg3_gui.py
```

The GUI includes:
- Mod/folder selection field
- Language dropdown (16 pre-configured languages) + custom code input
- LSLib field (Divine.exe) — with Auto-detect button
- "Generate .loca" checkbox
- "Batch mode (multiple mods)" checkbox
- Save/Load/Clear Config buttons
- Progress bar and real-time log
- App language selector (PT/EN/ES)

### CLI Mode

```bash
# Linux/Mac
venv/bin/python tradutor_bg3.py

# Windows
venv\Scripts\python tradutor_bg3.py
```

---

## Generate .exe (Windows)

To distribute the translator without requiring Python:

1. On Windows, double-click `build_exe.bat`
2. The script generates two files:
   - `Tradutor_BG3.exe` — Terminal mode (CLI)
   - `Tradutor_BG3_GUI.exe` — GUI mode (no terminal window)
3. Send these `.exe` files to anyone — no Python needed!

---

## .pak Support

### Windows

On Windows, the script auto-detects `Divine.exe` from LSLib, or you can set the path manually.

1. Download LSLib at: https://github.com/Norbyte/lslib
2. Set the path to `Divine.exe` in the LSLib field
3. Click **Save Config**
4. Select a mod `.pak` and click **TRANSLATE**

The script extracts the `.pak`, translates localization files, and repacks at the end. A backup is saved to the `_backups/` folder (auto-created in the same folder as the mod) before overwriting.

> **Note:** Starting from this version, the CMD window no longer flashes during `.pak` extraction and repacking. Everything happens silently in the background!

### Linux (via Bottles)

**Linux also supports .pak!** The script auto-detects if you have **Bottles** installed and uses its Wine to run `Divine.exe`.

#### Step-by-step to configure LSLib on Linux:

1. **Install Bottles** (if not already):
   ```bash
   flatpak install flathub com.usebottles.bottles
   ```

2. **Create a bottle for LSLib**:
   - Open Bottles
   - Create a new bottle:
     - **Name**: `LSLIB`
     - **Environment**: `Application`
   - Enter the `LSLIB` bottle
   - Go to the **Dependencies** tab
   - Click **Search for dependencies**
   - Search for **`dotnetcoredesktop8`** or **`dotnet8`**
   - Install the .NET 8.0 Desktop Runtime

3. **Download LSLib**:
   - https://github.com/Norbyte/lslib/releases
   - Download `ExportTool-vX.X.X.zip` (the Windows binary)
   - Extract anywhere (e.g. `~/Downloads/Packed/`)

4. **In BG3 Translator**:
   - **LSLib** field: set the path to `Divine.exe`
   - Example: `/home/user/Downloads/Packed/Tools/Divine.exe`
   - Click **Save Config**

5. **Done!** The script now extracts and repacks `.pak` automatically via Bottles.

#### Without Bottles (Linux/Mac)

If you don't have Bottles, the script works normally with:
- Already extracted folders (XML/.loca)
- Single and Batch modes for mod folders

For .pak, you need to extract manually on Windows first.

---

## Batch Mode

You can translate multiple mods at once:

1. Check the **"Batch mode (multiple mods)"** checkbox
2. Select the folder containing multiple mods (`.pak` or extracted folders)
3. Click **TRANSLATE**
4. The script processes all automatically

---

## Saved Settings

The script saves your preferences to `tradutor_bg3_config.json` (always in the script folder):

- `mod_folder` — default mod folder
- `lslib_path` — LSLib path (Divine.exe)
- `target_lang` — chosen target language
- `generate_loca` — generate `.loca` file in addition to `.xml`
- `batch_mode` — single or batch mode
- `app_lang` — UI language (pt/en/es)

On next run, use **Load Config** to restore everything.

---

## Supported Languages

The GUI has 16 pre-configured languages in the dropdown. You can also **type directly** any Google Translate code (e.g. `hi` for Hindi, `ar` for Arabic).

| Code | Language |
|------|----------|
| `en` | English |
| `pt` | Portuguese |
| `fr` | French |
| `de` | German |
| `es` | Spanish |
| `it` | Italian |
| `pl` | Polish |
| `ru` | Russian |
| `ja` | Japanese |
| `ko` | Korean |
| `zh-cn` | Chinese (Simplified) |
| `zh-tw` | Chinese (Traditional) |
| `tr` | Turkish |
| `uk` | Ukrainian |
| `cs` | Czech |
| `hu` | Hungarian |

In terminal mode (CLI), you can also type any Google Translate code directly.

---

## Translation Quality Notice

Translation is done automatically by **Google Translate**. While the result is understandable, word order may seem semantically odd in Portuguese (or other languages).

**Example:**
- Original English: `Wisdom Saving Throw`
- Auto-translation: `Sabedoria Teste de Resistencia`
- Correct PT-BR: `Teste de Resistencia de Sabedoria`

The reader will understand the meaning, but grammatical construction may not be perfect. Review is recommended, especially for complex texts or heavy D&D terminology.

---

## Files

| File | Description |
|------|-------------|
| `tradutor_bg3_gui.py` | Graphical interface (CustomTkinter, dark theme) |
| `tradutor_bg3.py` | Terminal mode (CLI) |
| `requirements.txt` | Python dependencies |
| `setup.bat` | Windows installer |
| `setup.sh` | Linux/Mac installer |
| `build_exe.bat` | Standalone .exe generator for Windows |
| `README.md` | This file |

---

## Portability

To move to another PC, just copy the entire folder:

```
BG3_translator/
  tradutor_bg3_gui.py
  tradutor_bg3.py
  requirements.txt
  setup.bat
  setup.sh
  build_exe.bat
  README.md
```

On the destination PC:
1. Install Python 3
2. Run `setup.bat` (Windows) or `./setup.sh` (Linux/Mac)
3. Done!

The `venv` (virtual environment) will be created locally on the new PC. No need to copy venv.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'tkinter'"
Install your system's tkinter:
- Fedora/Bazzite: `rpm-ostree install python3-tkinter` (reboot)
- Debian/Ubuntu: `sudo apt install python3-tk`
- Arch: `sudo pacman -S tk`

### "ModuleNotFoundError: No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Temporary folders not deleted after translation
In some cases (especially on Windows), the script may not be able to delete the temporary extracted folder after repacking the `.pak`. This usually happens when Windows still has file handles open.

**The translation is NOT affected** — the `.pak` is successfully repacked. The script will simply skip the folder deletion and display a warning in the log at the end. You can manually delete the leftover folders later if you want.

### Error extracting .pak on Linux
Check:
1. Bottles is installed: `flatpak list | grep bottles`
2. The bottle has .NET 8.0 installed (dependency `dotnetcoredesktop8`)
3. The path to `Divine.exe` is correct in the LSLib field

### "Found 0 mods" in batch mode
Check that the selected folder actually contains `.pak` files or `Localization/` folders.

---

## License and Credits

- Translation: Google Translate (via `deep-translator`)
- .pak tool: [LSLib / Norbyte](https://github.com/Norbyte/lslib)
- GUI framework: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
