#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tradutor BG3 - Interface Grafica (Tkinter)
Traduz mods de Baldur's Gate 3 automaticamente via Google Translate.
"""

import datetime
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
except ImportError:
    print("Erro: customtkinter nao instalado.")
    print("Execute: pip install customtkinter")
    sys.exit(1)

# =============================================================================
# DIRETORIO DO SCRIPT (garante que configs e logs ficam na pasta do programa)
# =============================================================================
SCRIPT_DIR = Path(sys.argv[0]).parent.resolve()
if not (SCRIPT_DIR / "tradutor_bg3_gui.py").exists():
    SCRIPT_DIR = Path(__file__).parent.resolve()

CONFIG_FILE = SCRIPT_DIR / "tradutor_bg3_config.json"
LOG_FILE = SCRIPT_DIR / "tradutor_bg3.log"

# =============================================================================
# DEPENDENCIAS
# =============================================================================
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Erro: deep-translator nao instalado.")
    print("Execute: pip install deep-translator")
    sys.exit(1)

# =============================================================================
# TRADUCOES (UI i18n)
# =============================================================================
TRANSLATIONS = {
    "pt": {
        "title": "Tradutor BG3",
        "mod_folder": "Mod / Pasta:",
        "language": "Idioma:",
        "lslib": "LSLib:",
        "generate_loca": "Gerar .loca",
        "batch_mode": "Modo lote (varios mods)",
        "custom_lang": "Idioma customizado",
        "save_config": "Salvar Config",
        "load_config": "Carregar Config",
        "clear_config": "Limpar Config",
        "translate": "TRADUZIR",
        "ready": "Pronto",
        "log": "Log:",
        "browsing_mod": "Selecione a pasta do mod",
        "browsing_lslib": "Selecione o Divine.exe",
        "error_no_mod": "Erro: Selecione um mod ou pasta.",
        "error_path_not_found": "Erro: Caminho nao encontrado: {}",
        "connecting_translate": "Conectando ao Google Translate ({})...",
        "extracting_pak": "Extraindo .pak...",
        "error_extract_pak": "Erro ao extrair .pak",
        "error_lslib_not_set": "Erro: .pak detectado mas LSLib nao configurado.",
        "error_no_loc": "Nenhum arquivo de localizacao encontrado.",
        "source": "Origem: {}",
        "detected_lang": "Idioma detectado: {}",
        "translating": "Traduzindo...",
        "completed": "Concluido!",
        "translation_done": "Traducao concluida!",
        "translation_failed": "Traducao falhou.",
        "repacking_pak": "Recompactando .pak...",
        "pak_success": ".pak recompactado com sucesso!",
        "pak_fail": "Falha ao recompactar .pak.",
        "batch_found": "Encontrados {} mods",
        "batch_processing": "--- [{}/{}] {} ---",
        "batch_skip_extract": "Pulando (falha na extracao)",
        "batch_skip_no_loc": "Sem localizacao, pulando.",
        "skip_no_lslib": "Pulando (LSLib nao configurado)",
        "batch_repack": "Recompactando .pak...",
        "batch_repack_fail": "Falha ao recompactar.",
        "batch_done": "Lote concluido!",
        "processing": "Processando: {}",
        "no_content_found": "Nenhum <content> encontrado.",
        "found_texts": "Encontrados {} textos para traduzir",
        "translated_count": "Traduzidos: {} de {}",
        "xml_valid": "XML validado com sucesso!",
        "xml_error": "Erro no XML: {}",
        "loca_generated": ".loca gerado: {}",
        "config_saved": "Configuracoes salvas.",
        "config_loaded": "Configuracoes carregadas.",
        "config_cleared": "Configuracoes limpas.",
        "select_app_lang": "Selecione o idioma do aplicativo:",
        "app_lang_label": "Idioma do app:",
        "restart_title": "Idioma",
        "restart_message": "Reinicie o aplicativo para aplicar o novo idioma.",
        "auto": "Auto",
        "browse": "Procurar",
        "placeholder_mod": "Caminho da pasta ou .pak...",
        "placeholder_lslib": "Caminho do Divine.exe",
        "placeholder_lslib_bottles": "Caminho do Divine.exe (usara Bottles)",
        "placeholder_custom_lang": "Digite a sigla (ex: hi, ar)",
        "pak_linux_bottles": "AVISO: {}.pak encontrado — pulado.",
        "pak_linux_hint": "O LSLib (Divine.exe) so funciona no Windows.",
        "pak_linux_extract": "Descompacte manualmente com o LSLib primeiro.",
    },
    "en": {
        "title": "BG3 Translator",
        "mod_folder": "Mod / Folder:",
        "language": "Language:",
        "lslib": "LSLib:",
        "generate_loca": "Generate .loca",
        "batch_mode": "Batch mode (multiple mods)",
        "custom_lang": "Custom language",
        "save_config": "Save Config",
        "load_config": "Load Config",
        "clear_config": "Clear Config",
        "translate": "TRANSLATE",
        "ready": "Ready",
        "log": "Log:",
        "browsing_mod": "Select mod folder",
        "browsing_lslib": "Select Divine.exe",
        "error_no_mod": "Error: Select a mod or folder.",
        "error_path_not_found": "Error: Path not found: {}",
        "connecting_translate": "Connecting to Google Translate ({})...",
        "extracting_pak": "Extracting .pak...",
        "error_extract_pak": "Error extracting .pak",
        "error_lslib_not_set": "Error: .pak detected but LSLib not configured.",
        "error_no_loc": "No localization file found.",
        "source": "Source: {}",
        "detected_lang": "Detected language: {}",
        "translating": "Translating...",
        "completed": "Completed!",
        "translation_done": "Translation completed!",
        "translation_failed": "Translation failed.",
        "repacking_pak": "Repacking .pak...",
        "pak_success": ".pak repacked successfully!",
        "pak_fail": "Failed to repack .pak.",
        "batch_found": "Found {} mods",
        "batch_processing": "--- [{}/{}] {} ---",
        "batch_skip_extract": "Skipping (extraction failed)",
        "batch_skip_no_loc": "No localization, skipping.",
        "skip_no_lslib": "Skipping (LSLib not configured)",
        "batch_repack": "Repacking .pak...",
        "batch_repack_fail": "Failed to repack.",
        "batch_done": "Batch completed!",
        "processing": "Processing: {}",
        "no_content_found": "No <content> found.",
        "found_texts": "Found {} texts to translate",
        "translated_count": "Translated: {} of {}",
        "xml_valid": "XML validated successfully!",
        "xml_error": "XML error: {}",
        "loca_generated": ".loca generated: {}",
        "config_saved": "Config saved.",
        "config_loaded": "Config loaded.",
        "config_cleared": "Config cleared.",
        "select_app_lang": "Select app language:",
        "app_lang_label": "App language:",
        "restart_title": "Language",
        "restart_message": "Restart the application to apply the new language.",
        "auto": "Auto",
        "browse": "Browse",
        "placeholder_mod": "Path to folder or .pak...",
        "placeholder_lslib": "Path to Divine.exe",
        "placeholder_lslib_bottles": "Path to Divine.exe (will use Bottles)",
        "placeholder_custom_lang": "Type code (e.g. hi, ar)",
        "pak_linux_bottles": "WARNING: {}.pak found — skipped.",
        "pak_linux_hint": "LSLib (Divine.exe) only works on Windows.",
        "pak_linux_extract": "Extract manually with LSLib first.",
    },
    "es": {
        "title": "Traductor BG3",
        "mod_folder": "Mod / Carpeta:",
        "language": "Idioma:",
        "lslib": "LSLib:",
        "generate_loca": "Generar .loca",
        "batch_mode": "Modo lote (varios mods)",
        "custom_lang": "Idioma personalizado",
        "save_config": "Guardar Config",
        "load_config": "Cargar Config",
        "clear_config": "Limpiar Config",
        "translate": "TRADUCIR",
        "ready": "Listo",
        "log": "Registro:",
        "browsing_mod": "Seleccione la carpeta del mod",
        "browsing_lslib": "Seleccione el Divine.exe",
        "error_no_mod": "Error: Seleccione un mod o carpeta.",
        "error_path_not_found": "Error: Ruta no encontrada: {}",
        "connecting_translate": "Conectando a Google Translate ({})...",
        "extracting_pak": "Extrayendo .pak...",
        "error_extract_pak": "Error al extraer .pak",
        "error_lslib_not_set": "Error: .pak detectado pero LSLib no configurado.",
        "error_no_loc": "No se encontro archivo de localizacion.",
        "source": "Origen: {}",
        "detected_lang": "Idioma detectado: {}",
        "translating": "Traduciendo...",
        "completed": "Completado!",
        "translation_done": "Traduccion completada!",
        "translation_failed": "La traduccion fallo.",
        "repacking_pak": "Reempaquetando .pak...",
        "pak_success": ".pak reempaquetado con exito!",
        "pak_fail": "Error al reempaquetar .pak.",
        "batch_found": "Encontrados {} mods",
        "batch_processing": "--- [{}/{}] {} ---",
        "batch_skip_extract": "Saltando (fallo en extraccion)",
        "batch_skip_no_loc": "Sin localizacion, saltando.",
        "skip_no_lslib": "Saltando (LSLib no configurado)",
        "batch_repack": "Reempaquetando .pak...",
        "batch_repack_fail": "Error al reempaquetar.",
        "batch_done": "Lote completado!",
        "processing": "Procesando: {}",
        "no_content_found": "No se encontro <content>.",
        "found_texts": "Encontrados {} textos para traducir",
        "translated_count": "Traducidos: {} de {}",
        "xml_valid": "XML validado con exito!",
        "xml_error": "Error en XML: {}",
        "loca_generated": ".loca generado: {}",
        "config_saved": "Configuracion guardada.",
        "config_loaded": "Configuracion cargada.",
        "config_cleared": "Configuracion limpiada.",
        "select_app_lang": "Seleccione el idioma de la aplicacion:",
        "app_lang_label": "Idioma de la app:",
        "restart_title": "Idioma",
        "restart_message": "Reinicie la aplicacion para aplicar el nuevo idioma.",
        "auto": "Auto",
        "browse": "Buscar",
        "placeholder_mod": "Ruta de la carpeta o .pak...",
        "placeholder_lslib": "Ruta del Divine.exe",
        "placeholder_lslib_bottles": "Ruta del Divine.exe (usara Bottles)",
        "placeholder_custom_lang": "Escriba el codigo (ej: hi, ar)",
        "pak_linux_bottles": "ADVERTENCIA: {}.pak encontrado — omitido.",
        "pak_linux_hint": "LSLib (Divine.exe) solo funciona en Windows.",
        "pak_linux_extract": "Extraiga manualmente con LSLib primero.",
    },
}


def _t(key, *args):
    lang = "pt"
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            lang = cfg.get("app_lang", "pt")
        except Exception:
            pass
    text = TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(key, key)
    if args:
        return text.format(*args)
    return text


# =============================================================================
# CONFIG
# =============================================================================
DEFAULT_CONFIG = {
    "mod_folder": "",
    "lslib_path": "",
    "target_lang": "pt",
    "auto_mode": True,
    "generate_loca": False,
    "batch_mode": False,
    "app_lang": "pt",
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# =============================================================================
# MAPEAMENTO DE IDIOMAS
# =============================================================================
LANG_MAP = {
    "english": "en", "brazilianportuguese": "pt", "french": "fr",
    "german": "de", "spanish": "es", "italian": "it", "polish": "pl",
    "russian": "ru", "chinese": "zh-cn", "chinesetraditional": "zh-tw",
    "japanese": "ja", "korean": "ko", "turkish": "tr", "ukrainian": "uk",
    "czech": "cs", "hungarian": "hu",
    "en": "en", "pt": "pt", "fr": "fr", "de": "de", "es": "es",
    "it": "it", "pl": "pl", "ru": "ru", "ja": "ja", "ko": "ko",
    "tr": "tr", "uk": "uk", "cs": "cs", "hu": "hu", "zh-cn": "zh-cn",
    "zh-tw": "zh-tw",
}

LANG_NAMES = {
    "en": "Ingles", "pt": "Portugues", "fr": "Frances", "de": "Alemao",
    "es": "Espanhol", "it": "Italiano", "pl": "Polones", "ru": "Russo",
    "zh-cn": "Chines (Simplificado)", "zh-tw": "Chines (Tradicional)",
    "ja": "Japones", "ko": "Coreano", "tr": "Turco", "uk": "Ucraniano",
    "cs": "Tcheco", "hu": "Hungaro",
}

TARGET_LANG_CODES = [
    ("pt", "Portugues"), ("en", "Ingles"), ("fr", "Frances"),
    ("de", "Alemao"), ("es", "Espanhol"), ("it", "Italiano"),
    ("pl", "Polones"), ("ru", "Russo"), ("ja", "Japones"),
    ("ko", "Coreano"), ("zh-cn", "Chines Simplificado"),
    ("zh-tw", "Chines Tradicional"), ("tr", "Turco"),
    ("uk", "Ucraniano"), ("cs", "Tcheco"), ("hu", "Hungaro"),
]


def resolve_target_folder_name(target_lang: str):
    reverse = {
        "en": "English", "pt": "BrazilianPortuguese", "fr": "French",
        "de": "German", "es": "Spanish", "it": "Italian", "pl": "Polish",
        "ru": "Russian", "zh-cn": "Chinese", "zh-tw": "ChineseTraditional",
        "ja": "Japanese", "ko": "Korean", "tr": "Turkish", "uk": "Ukrainian",
        "cs": "Czech", "hu": "Hungarian",
    }
    return reverse.get(target_lang, target_lang.capitalize())


def detect_source_lang(en_path: Path):
    folder_name = en_path.parent.name.lower()
    code = LANG_MAP.get(folder_name)
    if code:
        return code
    for parent in en_path.parents:
        code = LANG_MAP.get(parent.name.lower())
        if code:
            return code
    return "en"


# =============================================================================
# CONVERSOR .LOCA EMBUTIDO
# =============================================================================
def _escape_xml(text):
    if text is None:
        return ""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _unescape_xml(text):
    if text is None:
        return ""
    return (text.replace("&quot;", '"').replace("&lt;", "<")
            .replace("&gt;", ">").replace("&amp;", "&"))


def _read_table_entry(data, offset):
    handle = data[offset:offset + 37].decode('utf-8', errors='replace').rstrip('\x00')
    meta = data[offset + 38:offset + 70]
    version = struct.unpack_from("<H", meta, 26)[0]
    str_len_with_null = struct.unpack_from("<H", meta, 28)[0]
    return handle, version, str_len_with_null


def loca_to_xml_bytes(loca_path):
    with open(loca_path, "rb") as f:
        data = f.read()
    if len(data) < 12:
        raise ValueError("Arquivo .loca muito pequeno")
    if data[:4] == b"LOCA":
        num_entries = struct.unpack_from("<I", data, 4)[0]
        strings_offset = struct.unpack_from("<I", data, 8)[0]
        fmt = "LOCA"
    elif data[:5] == b"LOCAs":
        table_size = struct.unpack_from("<I", data, 8)[0]
        num_entries = (table_size - 12) // 70
        strings_offset = 12 + num_entries * 70
        fmt = "LOCAs"
    else:
        raise ValueError(f"Header .loca invalido: {data[:5]}")

    entries = []
    for i in range(num_entries):
        off = 12 + i * 70
        handle, version, str_len = _read_table_entry(data, off)
        entries.append((handle, version, str_len))

    strings = []
    off = strings_offset
    for handle, version, str_len in entries:
        if str_len == 0:
            strings.append("")
        else:
            s = data[off:off + str_len - 1].decode('utf-8', errors='replace')
            strings.append(s)
            off += str_len

    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<contentList>']
    for (handle, version, _), text in zip(entries, strings):
        lines.append(f'  <content contentuid="{handle}" version="{version}">{_escape_xml(text)}</content>')
    lines.append('</contentList>')
    return "\n".join(lines) + "\n", fmt


def _write_table_entry(out, handle, version, text_bytes):
    hb = handle.encode('utf-8')[:37]
    out.extend(hb + b'\x00' * (37 - len(hb)) + b'\x00')
    meta = bytearray(32)
    struct.pack_into("<H", meta, 26, version)
    struct.pack_into("<H", meta, 28, len(text_bytes) + 1)
    out.extend(meta)


def xml_to_loca_bytes(xml_path, format_hint="LOCA"):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    contents = [c for c in root.findall('content') if c.get('contentuid', '').strip()]
    n = len(contents)

    out = bytearray()
    if format_hint == "LOCA":
        out.extend(b"LOCA")
        out.extend(struct.pack("<I", n))
        out.extend(struct.pack("<I", 12 + n * 70))
    else:
        out.extend(b"LOCAs\x01\x00\x00")
        out.extend(struct.pack("<I", n * 70 + 12))

    for c in contents:
        handle = c.get('contentuid', '')
        version = int(c.get('version', 1))
        text = c.text or ""
        _write_table_entry(out, handle, version, text.encode('utf-8'))

    for c in contents:
        text = c.text or ""
        out.extend(text.encode('utf-8'))
        out.append(0)

    return bytes(out)


def loca_file_to_xml(loca_path: Path, xml_path: Path):
    try:
        xml_str, fmt = loca_to_xml_bytes(loca_path)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        return True
    except Exception as e:
        return False


def xml_file_to_loca(xml_path: Path, loca_path: Path, format_hint="LOCA"):
    try:
        loca_bytes = xml_to_loca_bytes(xml_path, format_hint)
        loca_path.parent.mkdir(parents=True, exist_ok=True)
        with open(loca_path, "wb") as f:
            f.write(loca_bytes)
        return True
    except Exception as e:
        return False


# =============================================================================
# PROTECAO E TRADUCAO
# =============================================================================
def protect(text):
    placeholders = []
    idx = 0
    def save(m):
        nonlocal idx
        ph = f"§§PH{idx}§§"
        placeholders.append((ph, m.group(0)))
        idx += 1
        return ph
    text = re.sub(r'&lt;LSTag[^&]*&gt;', save, text)
    text = re.sub(r'&lt;/LSTag&gt;', save, text)
    text = re.sub(r'&lt;LSTag[^&]*/&gt;', save, text)
    text = re.sub(r'&lt;br\s*/?&gt;', save, text, flags=re.I)
    text = re.sub(r'\[\d+\]', save, text)
    text = re.sub(r'\n', save, text)
    return text, placeholders


def restore(text, placeholders):
    for ph, orig in placeholders:
        text = text.replace(ph, orig)
    return text


import re as _re

_TRANSLATION_SPACING_RE = _re.compile(r'([.!?])([A-Z])')

def fix_translation_spacing(text):
    """Corrige espaçamento faltante após pontuação (bug comum do Google Translate)."""
    return _TRANSLATION_SPACING_RE.sub(r'\1 \2', text)


def translate_text(text, translator, max_retries=3):
    if not text or not text.strip():
        return text
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            result = translator.translate(text)
            if result and result.strip():
                return fix_translation_spacing(result)
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                import time
                time.sleep(1.5)
    return text


# =============================================================================
# UTILS
# =============================================================================
FAILED_CLEANUPS = []


def _force_rmtree(path: Path):
    if not path.exists():
        return True
    for root, dirs, files in os.walk(str(path), topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.chmod(file_path, 0o777)
                os.remove(file_path)
            except Exception:
                pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                os.chmod(dir_path, 0o777)
                os.rmdir(dir_path)
            except Exception:
                pass
    try:
        os.rmdir(str(path))
        return True
    except Exception:
        FAILED_CLEANUPS.append(str(path))
        return False


# =============================================================================
# LSLIB
# =============================================================================
def find_lslib_exe():
    candidates = [
        Path(r"C:\Program Files\LSLib\Divine.exe"),
        Path(r"C:\Program Files (x86)\LSLib\Divine.exe"),
        Path(r"C:\Tools\LSLib\Divine.exe"),
        Path(r"C:\LSLib\Divine.exe"),
        Path("Divine.exe"),
        Path(r"LSLib\Divine.exe"),
        Path(r"Divine\Divine.exe"),
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def resolve_lslib_path(path: Path):
    if not path or not path.exists():
        return None
    if path.is_file():
        return path
    if path.is_dir():
        for sub in ["", "Tools", "bin", "Divine"]:
            subdir = path / sub if sub else path
            candidate = subdir / "Divine.exe"
            if candidate.exists() and candidate.is_file():
                return candidate
    return None


def has_bottles():
    return (Path.home() / ".var/app/com.usebottles.bottles").exists()


def find_bottles_wine_env():
    bottles_dir = Path.home() / ".var/app/com.usebottles.bottles/data/bottles/bottles"
    if not bottles_dir.exists():
        return None
    for bottle_dir in bottles_dir.iterdir():
        if not bottle_dir.is_dir():
            continue
        yml_path = bottle_dir / "bottle.yml"
        if not yml_path.exists():
            continue
        try:
            with open(yml_path, "r", encoding="utf-8") as f:
                content = f.read()
            has_dotnet8 = "dotnetcoredesktop8" in content or "dotnet8" in content
            if not has_dotnet8:
                continue
            runner = None
            for line in content.splitlines():
                if line.strip().startswith("Runner:"):
                    runner = line.split(":", 1)[1].strip()
                    break
            if not runner:
                continue
            runner_path = Path.home() / f".var/app/com.usebottles.bottles/data/bottles/runners/{runner}/bin/wine"
            if runner_path.exists():
                return {"WINE": str(runner_path), "WINEPREFIX": str(bottle_dir)}
        except Exception:
            continue
    return None


def to_wine_path(path: Path):
    return "Z:" + str(path).replace("/", "\\")


def _convert_args_for_wine(args: list):
    result = []
    for arg in args:
        if isinstance(arg, str) and len(arg) > 1 and arg.startswith("/") and not arg.startswith("-/"):
            result.append(to_wine_path(Path(arg)))
        else:
            result.append(arg)
    return result


def _run_lslib_cmd(lslib_path: Path, args: list):
    is_win = sys.platform == "win32"
    kwargs = {"capture_output": True, "text": True, "check": True}
    if is_win:
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    if not is_win and has_bottles():
        env = find_bottles_wine_env()
        if env:
            wine_path = env["WINE"]
            wineprefix = env["WINEPREFIX"]
            wine_args = [to_wine_path(lslib_path)] + _convert_args_for_wine(args)
            cmd = [wine_path] + wine_args
            env_vars = dict(os.environ)
            env_vars["WINEPREFIX"] = wineprefix
            try:
                result = subprocess.run(cmd, env=env_vars, **kwargs)
                return True, result.stdout, result.stderr
            except subprocess.CalledProcessError as e:
                return False, e.stdout, e.stderr
            except Exception as e:
                return False, "", str(e)
    cmd = [str(lslib_path)] + args
    try:
        result = subprocess.run(cmd, **kwargs)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)


def extract_pak(pak_path: Path, output_dir: Path, lslib_path: Path):
    success, stdout, stderr = _run_lslib_cmd(
        lslib_path,
        ["-g", "bg3", "-a", "extract-package", "-s", str(pak_path), "-d", str(output_dir)]
    )
    return success


def create_pak(source_dir: Path, pak_path: Path, lslib_path: Path):
    if not source_dir.exists():
        return False
    backups_dir = pak_path.parent / "_backups"
    backups_dir.mkdir(exist_ok=True)
    backup_path = backups_dir / (pak_path.name + ".original")
    if not backup_path.exists():
        shutil.copy2(pak_path, backup_path)
    pak_path.unlink()
    cmd_args = [
        "-g", "bg3", "-a", "create-package", "-c", "lz4",
        "-s", str(source_dir), "-d", str(pak_path),
    ]
    success, stdout, stderr = _run_lslib_cmd(lslib_path, cmd_args)
    if not success or not pak_path.exists() or pak_path.stat().st_size < 1024:
        if backup_path.exists():
            shutil.copy2(backup_path, pak_path)
        return False
    return True


# =============================================================================
# RESOLVER CAMINHOS
# =============================================================================
def find_file_in_dir(directory: Path, extensions):
    for ext in extensions:
        matches = list(directory.glob(f"*{ext}"))
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            return matches[0]
    return None


def resolve_source(user_input: Path):
    en_was_loca = False
    found_loca_also = False
    localization_parent = None

    if user_input.is_file():
        if user_input.suffix.lower() == ".loca":
            en_was_loca = True
        sibling = user_input.with_suffix(".loca" if user_input.suffix.lower() == ".xml" else ".xml")
        if sibling.exists():
            found_loca_also = True
        for parent in user_input.parents:
            if parent.name.lower() == "localization":
                localization_parent = parent
                break
        return user_input, en_was_loca, found_loca_also, localization_parent

    if user_input.name.lower() == "localization":
        localization_parent = user_input
        lang_options = []
        for child in user_input.iterdir():
            if child.is_dir() and child.name.lower() in LANG_MAP:
                xml_file = find_file_in_dir(child, [".xml"])
                loca_file = find_file_in_dir(child, [".loca"])
                if xml_file or loca_file:
                    lang_options.append({
                        "path": child, "name": child.name,
                        "xml": xml_file, "loca": loca_file,
                    })
        if len(lang_options) > 1:
            selected = lang_options[0]
            for opt in lang_options:
                if opt["name"].lower() == "english":
                    selected = opt
                    break
            has_both = selected["xml"] and selected["loca"]
            if selected["xml"]:
                return selected["xml"], False, has_both, localization_parent
            return selected["loca"], True, has_both, localization_parent
        elif len(lang_options) == 1:
            opt = lang_options[0]
            has_both = opt["xml"] and opt["loca"]
            if opt["xml"]:
                return opt["xml"], False, has_both, localization_parent
            return opt["loca"], True, has_both, localization_parent
        xml_file = find_file_in_dir(user_input, [".xml"])
        if xml_file:
            return xml_file, False, False, localization_parent
        loca_file = find_file_in_dir(user_input, [".loca"])
        if loca_file:
            return loca_file, True, False, localization_parent
        return None, False, False, None

    for loc_dir in user_input.rglob("Localization"):
        if loc_dir.is_dir():
            return resolve_source(loc_dir)

    xml_file = find_file_in_dir(user_input, [".xml"])
    if xml_file:
        sibling_loca = xml_file.with_suffix(".loca")
        found_loca_also = sibling_loca.exists()
        for parent in xml_file.parents:
            if parent.name.lower() == "localization":
                localization_parent = parent
                break
        return xml_file, False, found_loca_also, localization_parent

    loca_file = find_file_in_dir(user_input, [".loca"])
    if loca_file:
        sibling_xml = loca_file.with_suffix(".xml")
        found_loca_also = sibling_xml.exists()
        for parent in loca_file.parents:
            if parent.name.lower() == "localization":
                localization_parent = parent
                break
        return loca_file, True, found_loca_also, localization_parent

    return None, False, False, None


def derive_output_name(en_path: Path, dest_folder_name: str):
    source_folder = en_path.parent.name.lower()
    file_stem = en_path.stem.lower()
    if file_stem == source_folder:
        return dest_folder_name.lower()
    return en_path.stem


def resolve_target_auto(localization_parent: Path, en_path: Path, en_was_loca: bool, generate_loca: bool, target_lang: str = "pt"):
    target_folder = resolve_target_folder_name(target_lang)
    target_dir = localization_parent / target_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    out_name = derive_output_name(en_path, target_folder.lower())
    if en_was_loca:
        loca_path = target_dir / (out_name + ".loca")
        xml_path = target_dir / (out_name + ".xml")
        return xml_path, loca_path, True
    else:
        xml_path = target_dir / (out_name + ".xml")
        if generate_loca:
            loca_path = target_dir / (out_name + ".loca")
            return xml_path, loca_path, True
        return xml_path, None, False


def resolve_target_manual(user_path: Path, en_path: Path, en_was_loca: bool, generate_loca: bool, target_lang: str = "pt"):
    xml_path = None
    loca_path = None
    should_loca = en_was_loca or generate_loca

    if not user_path.is_dir():
        xml_path = user_path.with_suffix(".xml") if user_path.suffix.lower() == ".loca" else user_path
        if user_path.suffix.lower() == ".loca":
            loca_path = user_path
            should_loca = True
        return xml_path, loca_path, should_loca

    if user_path.name.lower() == "localization":
        target_folder = resolve_target_folder_name(target_lang)
        target_dir = user_path / target_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        out_name = derive_output_name(en_path, target_folder.lower())
        if en_was_loca:
            loca_path = target_dir / (out_name + ".loca")
            xml_path = target_dir / (out_name + ".xml")
        else:
            xml_path = target_dir / (out_name + ".xml")
            if generate_loca:
                loca_path = target_dir / (out_name + ".loca")
        return xml_path, loca_path, should_loca

    if en_was_loca:
        loca_path = user_path / en_path.name
        xml_path = user_path / (en_path.stem + ".xml")
    else:
        xml_path = user_path / en_path.name
        if generate_loca:
            loca_path = user_path / (en_path.stem + ".loca")
    return xml_path, loca_path, should_loca


# =============================================================================
# TRADUCAO SINGLE
# =============================================================================
def process_single_mod(en_path, localization_parent, en_was_loca, found_loca_also,
                       translator, auto_mode, target_lang="pt", log_callback=None, progress_callback=None):
    if log_callback:
        log_callback(_t("processing", en_path.name))

    target_folder = resolve_target_folder_name(target_lang)
    if localization_parent:
        generate_loca = en_was_loca or found_loca_also
        pt_path, pt_loca_path, pt_should_loca = resolve_target_auto(
            localization_parent, en_path, en_was_loca, generate_loca, target_lang
        )
    else:
        if en_was_loca or found_loca_also:
            generate_loca = True
        else:
            generate_loca = False
        pt_path, pt_loca_path, pt_should_loca = resolve_target_manual(
            en_path.parent, en_path, en_was_loca, generate_loca, target_lang
        )

    xml_en_path = en_path
    tmp_xml_en = None
    if en_was_loca:
        tmp_xml_en = Path(tempfile.gettempdir()) / f"tradutor_bg3_{en_path.stem}.xml"
        if not loca_file_to_xml(en_path, tmp_xml_en):
            if log_callback:
                log_callback("Erro ao converter .loca -> .xml")
            return False, None
        xml_en_path = tmp_xml_en

    with open(xml_en_path, "r", encoding="utf-8") as f:
        raw_en = f.read()

    handles = []
    for m in re.finditer(r'(<content contentuid="([^"]+)"[^>]*>)(.*?)(</content>)', raw_en, re.DOTALL):
        handles.append((m.group(1), m.group(2), m.group(3), m.group(4)))

    if not handles:
        if log_callback:
            log_callback(_t("no_content_found"))
        return False, None

    if log_callback:
        log_callback(_t("found_texts", len(handles)))

    translated_count = 0
    raw_pt = raw_en

    for i, (open_tag, uid, content, close_tag) in enumerate(handles, 1):
        protected, placeholders = protect(content)
        translated = translate_text(protected, translator)
        restored = restore(translated, placeholders)

        old = open_tag + content + close_tag
        new = open_tag + restored + close_tag
        raw_pt = raw_pt.replace(old, new, 1)
        translated_count += 1

        if progress_callback:
            progress_callback(i, len(handles))

    pt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pt_path, "w", encoding="utf-8") as f:
        f.write(raw_pt)

    if log_callback:
        log_callback(_t("translated_count", translated_count, len(handles)))

    try:
        ET.parse(str(pt_path))
        if log_callback:
            log_callback(_t("xml_valid"))
    except ET.ParseError as e:
        if log_callback:
            log_callback(_t("xml_error", e))
        return False, None

    if pt_should_loca and pt_loca_path:
        xml_file_to_loca(pt_path, pt_loca_path, "LOCA")
        if log_callback:
            log_callback(_t("loca_generated", pt_loca_path.name))

    if tmp_xml_en and tmp_xml_en.exists():
        tmp_xml_en.unlink()

    return True, pt_path


# =============================================================================
# SCANNER DE MODS
# =============================================================================
def scan_mods_folder(root_dir: Path):
    mods = []
    for pak in root_dir.rglob("*.pak"):
        mods.append({"type": "pak", "path": pak, "name": pak.stem})
    for loc_dir in root_dir.rglob("Localization"):
        if loc_dir.is_dir():
            has_lang = False
            for child in loc_dir.iterdir():
                if child.is_dir() and child.name.lower() in LANG_MAP:
                    has_lang = True
                    break
            if has_lang:
                already = any(str(loc_dir) in str(m["path"]) for m in mods if m["type"] == "pak")
                if not already:
                    mods.append({"type": "folder", "path": loc_dir, "name": loc_dir.parent.name})
    return mods


# =============================================================================
# INTERFACE GRAFICA (CustomTkinter - visual moderno)
# =============================================================================
class TranslatorGUI:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title(_t("title"))
        self.root.geometry("780x640")
        self.root.minsize(720, 580)

        self.is_windows = sys.platform == "win32"
        self.cfg = load_config()
        self.running = False
        self.thread = None

        # Pergunta idioma do app na primeira vez
        if not self.cfg.get("app_lang"):
            self._show_first_time_lang_dialog()

        self._build_ui()
        if self.is_windows:
            self._auto_detect_lslib()

    def _build_ui(self):
        # Grid principal: 1 coluna, expansivel
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)

        r = 0

        # Titulo
        title = ctk.CTkLabel(main_frame, text=_t("title"),
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.grid(row=r, column=0, columnspan=3, pady=(15, 5))
        r += 1

        # --- Idioma do App ---
        app_lang_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        app_lang_frame.grid(row=r, column=0, columnspan=3, pady=(0, 10))
        ctk.CTkLabel(app_lang_frame, text=_t("app_lang_label"), font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        self.app_lang_combo = ctk.CTkComboBox(app_lang_frame, values=["Portugues (pt)", "English (en)", "Espanol (es)"], state="readonly", width=150, command=self._on_app_lang_changed)
        self.app_lang_combo.pack(side="left", padx=5)
        self._set_app_lang_combo()
        r += 1

        # --- Mod/Pasta ---
        ctk.CTkLabel(main_frame, text=_t("mod_folder"), font=ctk.CTkFont(size=13)).grid(
            row=r, column=0, padx=(15, 5), pady=8, sticky="w")
        self.entry_mod = ctk.CTkEntry(main_frame, placeholder_text=_t("placeholder_mod"))
        self.entry_mod.grid(row=r, column=1, padx=5, pady=8, sticky="ew")
        self.entry_mod.insert(0, self.cfg.get("mod_folder", ""))
        ctk.CTkButton(main_frame, text=_t("browse"), width=90, command=self._browse_mod).grid(
            row=r, column=2, padx=(5, 15), pady=8)
        r += 1

        # --- Idioma ---
        ctk.CTkLabel(main_frame, text=_t("language"), font=ctk.CTkFont(size=13)).grid(
            row=r, column=0, padx=(15, 5), pady=8, sticky="w")
        self.lang_options = [f"{name} ({code})" for code, name in TARGET_LANG_CODES]
        self.lang_combo = ctk.CTkComboBox(main_frame, values=self.lang_options, state="readonly", width=280)
        self.lang_combo.grid(row=r, column=1, padx=(5, 15), pady=8, sticky="w")
        self._set_lang_combo()
        r += 1

        # --- LSLib ---
        ctk.CTkLabel(main_frame, text=_t("lslib"), font=ctk.CTkFont(size=13)).grid(
            row=r, column=0, padx=(15, 5), pady=8, sticky="w")
        placeholder = "Caminho do Divine.exe"
        if not self.is_windows and has_bottles():
            placeholder = "Caminho do Divine.exe (usara Bottles)"
        self.entry_lslib = ctk.CTkEntry(main_frame, placeholder_text=placeholder)
        self.entry_lslib.grid(row=r, column=1, padx=5, pady=8, sticky="ew")
        self.entry_lslib.insert(0, self.cfg.get("lslib_path", ""))
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=r, column=2, padx=(5, 15), pady=8)
        ctk.CTkButton(btn_frame, text=_t("auto"), width=60, command=self._auto_detect_lslib).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text=_t("browse"), width=80, command=self._browse_lslib).pack(side="left", padx=2)
        r += 1

        # --- Checkboxes ---
        checks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        checks_frame.grid(row=r, column=0, columnspan=3, padx=15, pady=(5, 5), sticky="w")
        self.chk_custom_lang = ctk.CTkCheckBox(checks_frame, text=_t("custom_lang"), command=self._on_custom_lang_toggle)
        self.chk_custom_lang.pack(side="left", padx=5)
        self.chk_loca = ctk.CTkCheckBox(checks_frame, text=_t("generate_loca"))
        self.chk_loca.pack(side="left", padx=15)
        if self.cfg.get("generate_loca", False):
            self.chk_loca.select()
        self.chk_batch = ctk.CTkCheckBox(checks_frame, text=_t("batch_mode"))
        self.chk_batch.pack(side="left", padx=15)
        if self.cfg.get("batch_mode", False):
            self.chk_batch.select()
        r += 1

        # --- Botoes de config ---
        cfg_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cfg_frame.grid(row=r, column=0, columnspan=3, padx=15, pady=(0, 5), sticky="w")
        ctk.CTkButton(cfg_frame, text=_t("save_config"), width=110, command=self._save_config_ui).pack(side="left", padx=3)
        ctk.CTkButton(cfg_frame, text=_t("load_config"), width=110, command=self._load_config_ui).pack(side="left", padx=3)
        ctk.CTkButton(cfg_frame, text=_t("clear_config"), width=110, command=self._clear_config_ui).pack(side="left", padx=3)
        r += 1

        # --- Botao Traduzir ---
        self.btn_translate = ctk.CTkButton(
            main_frame, text=_t("translate"), height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E7D32", hover_color="#1B5E20",
            command=self._start_translation
        )
        self.btn_translate.grid(row=6, column=0, columnspan=3, padx=15, pady=15, sticky="ew")

        # --- Progresso ---
        self.progress_bar = ctk.CTkProgressBar(main_frame, height=16, corner_radius=8)
        self.progress_bar.grid(row=7, column=0, columnspan=3, padx=15, pady=(5, 0), sticky="ew")
        self.progress_bar.set(0)
        self.lbl_progress = ctk.CTkLabel(main_frame, text=_t("ready"), font=ctk.CTkFont(size=12))
        self.lbl_progress.grid(row=8, column=0, columnspan=3, pady=(0, 5))

        # --- Log ---
        ctk.CTkLabel(main_frame, text=_t("log"), font=ctk.CTkFont(size=12)).grid(
            row=9, column=0, padx=15, pady=(5, 0), sticky="w")
        self.txt_log = ctk.CTkTextbox(main_frame, height=180, wrap="word", state="disabled",
                                       font=ctk.CTkFont(size=12))
        self.txt_log.grid(row=10, column=0, columnspan=3, padx=15, pady=(0, 15), sticky="nsew")
        main_frame.grid_rowconfigure(10, weight=1)

    def _set_app_lang_combo(self):
        current = self.cfg.get("app_lang", "pt")
        mapping = {"pt": "Portugues (pt)", "en": "English (en)", "es": "Espanol (es)"}
        self.app_lang_combo.set(mapping.get(current, "Portugues (pt)"))

    def _on_app_lang_changed(self, value):
        code = value.split("(")[1].split(")")[0] if "(" in value else "pt"
        self.cfg["app_lang"] = code
        save_config(self.cfg)
        messagebox.showinfo(_t("restart_title"), _t("restart_message"))

    def _show_first_time_lang_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Idioma / Language / Idioma")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Selecione o idioma do aplicativo:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Select app language:", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(dialog, text="Seleccione el idioma de la aplicacion:", font=ctk.CTkFont(size=12)).pack(pady=(0, 10))

        combo = ctk.CTkComboBox(dialog, values=["Portugues (pt)", "English (en)", "Espanol (es)"], state="readonly", width=200)
        combo.set("Portugues (pt)")
        combo.pack(pady=10)

        def on_ok():
            val = combo.get()
            code = val.split("(")[1].split(")")[0] if "(" in val else "pt"
            self.cfg["app_lang"] = code
            save_config(self.cfg)
            dialog.destroy()

        ctk.CTkButton(dialog, text="OK", command=on_ok).pack(pady=10)
        self.root.wait_window(dialog)

    def _set_lang_combo(self):
        current = self.cfg.get("target_lang", "pt")
        for opt in self.lang_options:
            if opt.endswith(f"({current})"):
                self.lang_combo.set(opt)
                return
        # Se nao achou nas opcoes, pode ser um codigo customizado
        if self.cfg.get("custom_lang", False):
            self.lang_combo.set(current)
        else:
            self.lang_combo.set(self.lang_options[0])

    def _on_custom_lang_toggle(self):
        if self.chk_custom_lang.get():
            self.lang_combo.configure(state="normal", values=[])
            self.lang_combo.set("")
        else:
            self.lang_combo.configure(state="readonly", values=self.lang_options)
            self._set_lang_combo()

    def get_target_lang_code(self):
        val = self.lang_combo.get().strip()
        if not val:
            return "pt"
        if "(" in val and ")" in val:
            return val.split("(")[1].split(")")[0]
        # Usuario digitou um codigo diretamente (ex: "hi", "ar")
        return val.lower()

    def _browse_mod(self):
        path = filedialog.askdirectory(title=_t("browsing_mod"))
        if path:
            self.entry_mod.delete(0, "end")
            self.entry_mod.insert(0, path)

    def _browse_lslib(self):
        if self.entry_lslib is None:
            return
        path = filedialog.askopenfilename(title=_t("browsing_lslib"), filetypes=[("Executable", "*.exe")])
        if path:
            self.entry_lslib.delete(0, "end")
            self.entry_lslib.insert(0, path)

    def _auto_detect_lslib(self):
        if self.entry_lslib is None:
            return
        found = find_lslib_exe()
        if found:
            self.entry_lslib.delete(0, "end")
            self.entry_lslib.insert(0, str(found))
            self.log(f"LSLib detectado: {found}")
        else:
            self.entry_lslib.delete(0, "end")

    def log(self, message):
        def _do_log():
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", f"[{timestamp}] {message}\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
        if threading.current_thread() is threading.main_thread():
            _do_log()
        else:
            self.root.after(0, _do_log)

    def set_progress(self, current, total):
        def _do_set():
            if total > 0:
                pct = current / total
                self.progress_bar.set(pct)
                self.lbl_progress.configure(text=f"Progresso: {current}/{total} ({int(pct*100)}%)")
            else:
                self.progress_bar.set(0)
                self.lbl_progress.configure(text=_t("ready"))
        if threading.current_thread() is threading.main_thread():
            _do_set()
        else:
            self.root.after(0, _do_set)

    def _load_config_ui(self):
        self.cfg = load_config()
        self.entry_mod.delete(0, "end")
        self.entry_mod.insert(0, self.cfg.get("mod_folder", ""))
        if self.entry_lslib is not None:
            self.entry_lslib.delete(0, "end")
            self.entry_lslib.insert(0, self.cfg.get("lslib_path", ""))
        if self.cfg.get("custom_lang", False):
            self.chk_custom_lang.select()
            self._on_custom_lang_toggle()
        else:
            self.chk_custom_lang.deselect()
            self._on_custom_lang_toggle()
        self._set_lang_combo()
        if self.cfg.get("generate_loca", False):
            self.chk_loca.select()
        else:
            self.chk_loca.deselect()
        if self.cfg.get("batch_mode", False):
            self.chk_batch.select()
        else:
            self.chk_batch.deselect()
        self.log(_t("config_loaded"))

    def _save_config_ui(self):
        self.cfg["mod_folder"] = self.entry_mod.get()
        self.cfg["lslib_path"] = self.entry_lslib.get() if self.entry_lslib is not None else ""
        self.cfg["target_lang"] = self.get_target_lang_code()
        self.cfg["generate_loca"] = self.chk_loca.get()
        self.cfg["batch_mode"] = self.chk_batch.get()
        self.cfg["custom_lang"] = bool(self.chk_custom_lang.get())
        save_config(self.cfg)
        self.log(_t("config_saved"))

    def _clear_config_ui(self):
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        self.cfg = dict(DEFAULT_CONFIG)
        self.log(_t("config_cleared"))

    def _start_translation(self):
        if self.running:
            return
        self.running = True
        self.btn_translate.configure(state="disabled", text=_t("translating"))
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")
        self.progress_bar.set(0)
        self.lbl_progress.configure(text=_t("translating"))

        self.thread = threading.Thread(target=self._run_translation, daemon=True)
        self.thread.start()

    def _run_translation(self):
        try:
            self._do_translation()
        except Exception as e:
            self.log(f"ERRO: {e}")
            traceback.print_exc()
        finally:
            self.running = False
            self.root.after(0, self._on_translation_done)

    def _on_translation_done(self):
        self.btn_translate.configure(state="normal", text=_t("translate"))
        self.lbl_progress.configure(text=_t("completed"))
        self.progress_bar.set(1)

    def _do_translation(self):
        mod_path_str = self.entry_mod.get().strip()
        lslib_str = self.entry_lslib.get().strip() if self.entry_lslib is not None else ""
        target_lang = self.get_target_lang_code()
        generate_loca = self.chk_loca.get()
        batch_mode = self.chk_batch.get()

        if not mod_path_str:
            self.log(_t("error_no_mod"))
            return

        mod_input = Path(mod_path_str)
        if not mod_input.exists():
            self.log(_t("error_path_not_found", mod_path_str))
            return

        lslib_path = None
        if lslib_str:
            lslib_path = resolve_lslib_path(Path(lslib_str))

        self.log(_t("connecting_translate", target_lang))
        try:
            translator = GoogleTranslator(source="auto", target=target_lang)
        except Exception as e:
            self.log(f"Erro ao conectar: {e}")
            return

        if batch_mode:
            self._do_batch(mod_input, translator, target_lang, generate_loca, lslib_path)
        else:
            self._do_single(mod_input, translator, target_lang, generate_loca, lslib_path)

    def _do_single(self, mod_input, translator, target_lang, generate_loca, lslib_path):
        extracted_dir = None
        original_pak = None

        # Se for uma pasta com .pak dentro, detecta automaticamente
        if mod_input.is_dir():
            pak_files = list(mod_input.glob("*.pak"))
            if pak_files:
                mod_input = pak_files[0]

        if mod_input.is_file() and mod_input.suffix.lower() == ".pak":
            original_pak = mod_input
            if lslib_path:
                extracted_dir = mod_input.parent / mod_input.stem
                if extracted_dir.exists():
                    _force_rmtree(extracted_dir)
                self.log(_t("extracting_pak"))
                if not extract_pak(mod_input, extracted_dir, lslib_path):
                    self.log(_t("error_extract_pak"))
                    return
                mod_input = extracted_dir
            else:
                self.log(_t("error_lslib_not_set"))
                return

        en_path, en_was_loca, found_loca_also, localization_parent = resolve_source(mod_input)
        if not en_path:
            self.log(_t("error_no_loc"))
            if extracted_dir and extracted_dir.exists():
                _force_rmtree(extracted_dir)
            return

        self.log(_t("source", en_path.name))
        detected_src = detect_source_lang(en_path)
        if detected_src != "auto":
            self.log(_t("detected_lang", LANG_NAMES.get(detected_src, detected_src)))
            try:
                translator = GoogleTranslator(source=detected_src, target=target_lang)
            except Exception:
                pass

        success, _ = process_single_mod(
            en_path, localization_parent, en_was_loca, found_loca_also or generate_loca,
            translator, True, target_lang,
            log_callback=self.log, progress_callback=self.set_progress
        )

        if success and original_pak and lslib_path:
            self.log(_t("repacking_pak"))
            if create_pak(extracted_dir, original_pak, lslib_path):
                self.log(_t("pak_success"))
            else:
                self.log(_t("pak_fail"))

        if extracted_dir and extracted_dir.exists():
            _force_rmtree(extracted_dir)

        if success:
            self.log(_t("translation_done"))
        else:
            self.log(_t("translation_failed"))

    def _do_batch(self, batch_dir, translator, target_lang, generate_loca, lslib_path):
        if not batch_dir.is_dir():
            self.log("Erro: Modo lote requer uma pasta.")
            return

        mods = scan_mods_folder(batch_dir)
        self.log(_t("batch_found", len(mods)))

        for i, mod in enumerate(mods, 1):
            self.log(_t("batch_processing", i, len(mods), mod["name"]))
            extracted_dir = None
            original_pak = None
            mod_input = mod["path"]

            if mod["type"] == "pak":
                if lslib_path:
                    original_pak = mod["path"]
                    extracted_dir = mod["path"].parent / mod["path"].stem
                    if extracted_dir.exists():
                        _force_rmtree(extracted_dir)
                    if extract_pak(mod["path"], extracted_dir, lslib_path):
                        mod_input = extracted_dir
                    else:
                        self.log(_t("batch_skip_extract"))
                        continue
                else:
                    self.log(_t("skip_no_lslib"))
                    continue

            en_path, en_was_loca, found_loca_also, localization_parent = resolve_source(mod_input)
            if not en_path:
                self.log(_t("batch_skip_no_loc"))
                if extracted_dir and extracted_dir.exists():
                    _force_rmtree(extracted_dir)
                continue

            detected_src = detect_source_lang(en_path)
            if detected_src != "auto":
                try:
                    translator = GoogleTranslator(source=detected_src, target=target_lang)
                except Exception:
                    pass

            success, _ = process_single_mod(
                en_path, localization_parent, en_was_loca, found_loca_also or generate_loca,
                translator, True, target_lang,
                log_callback=self.log, progress_callback=self.set_progress
            )

            if success and original_pak and lslib_path:
                self.log(_t("repacking_pak"))
                if not create_pak(extracted_dir, original_pak, lslib_path):
                    self.log(_t("batch_repack_fail"))

            if extracted_dir and extracted_dir.exists():
                _force_rmtree(extracted_dir)

        self.log(_t("batch_done"))

    def run(self):
        self.root.mainloop()


def main():
    app = TranslatorGUI()
    app.run()


if __name__ == "__main__":
    main()
