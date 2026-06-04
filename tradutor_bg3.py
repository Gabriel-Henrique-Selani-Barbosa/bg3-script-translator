#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tradutor BG3 100% Dinamico
Traduz arquivos XML/.loca de EN para PT-BR usando Google Translate.
Protege <content>, LSTags, placeholders e tags XML.
Suporta .pak via LSLib e modo lote.
Salva configuracoes em template JSON para reutilizar.

Uso:
    python tradutor_bg3.py
    venv\\Scripts\\python tradutor_bg3.py   (Windows)
    venv/bin/python tradutor_bg3.py          (Linux/Mac)
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
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

# Diretorio do script (usa sys.argv[0] pra funcionar no Windows tambem)
SCRIPT_DIR = Path(sys.argv[0]).parent.resolve()
if not (SCRIPT_DIR / "tradutor_bg3.py").exists():
    # Fallback pra __file__ se sys.argv[0] nao for confiavel
    SCRIPT_DIR = Path(__file__).parent.resolve()

# =============================================================================
# LOGGING — salva tudo em arquivo mesmo se o cmd fechar
# =============================================================================
LOG_FILE = SCRIPT_DIR / "tradutor_bg3.log"

class TeeLogger:
    """Redireciona stdout para console + arquivo simultaneamente."""
    def __init__(self, filepath, original_stdout):
        self.filepath = filepath
        self.original_stdout = original_stdout
        self.file = open(filepath, "a", encoding="utf-8")
        self.file.write(f"\n{'='*60}\n")
        self.file.write(f"  INICIO: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.file.write(f"{'='*60}\n")
        self.file.flush()

    def write(self, message):
        self.original_stdout.write(message)
        self.file.write(message)
        self.file.flush()

    def flush(self):
        self.original_stdout.flush()
        self.file.flush()

    def close(self):
        self.file.close()

sys.stdout = TeeLogger(LOG_FILE, sys.stdout)


# =============================================================================
# CHECAGEM DE DEPENDENCIAS
# =============================================================================
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("=" * 60)
    print("  You need to install a dependency first.")
    print("=" * 60)
    print()
    print("  O pacote 'deep-translator' ta faltando aqui.")
    print("  Mas relaxa que e rapidinho, vou te mostrar como:")
    print()
    print("  [Windows - usando venv]")
    print("    python -m venv venv")
    print("    venv\\Scripts\\pip install deep-translator")
    print("    venv\\Scripts\\python tradutor_bg3.py")
    print()
    print("  [Linux/Mac - usando venv]")
    print("    python3 -m venv venv")
    print("    venv/bin/pip install deep-translator")
    print("    venv/bin/python tradutor_bg3.py")
    print()
    print("  [Ou instala globalmente]")
    print("    pip install deep-translator")
    print()
    print("  Se tiver o 'setup.bat' (Windows) ou 'setup.sh' (Linux),")
    print("  e so dar dois cliques que eu faco tudo sozinho pra voce ✨")
    print("=" * 60)
    sys.exit(1)


# =============================================================================
# CONFIGURACAO SALVA (TEMPLATE)
# =============================================================================
CONFIG_FILE = SCRIPT_DIR / "tradutor_bg3_config.json"

# =============================================================================
# TRADUCOES (UI i18n)
# =============================================================================
TRANSLATIONS = {
    "pt": {
        "welcome": _t("welcome"),
        "select_app_lang": "Selecione o idioma do aplicativo:",
        "menu_main": _t("menu_main"),
        "option_translate": _t("option_translate"),
        "option_config": _t("option_config"),
        "option_exit": _t("option_exit"),
        "choice": _t("choice"),
        "config_menu": _t("config_menu"),
        "config_saved": _t("config_saved"),
        "config_loaded": _t("config_loaded"),
        "config_cleared": _t("config_cleared"),
        "ask_mod_path": _t("ask_mod_path"),
        "ask_target_lang": _t("ask_target_lang"),
        "ask_lslib": _t("ask_lslib"),
        "ask_generate_loca": _t("ask_generate_loca"),
        "ask_batch": _t("ask_batch"),
        "error_no_mod": _t("error_no_mod"),
        "connecting": _t("connecting"),
        "extracting": _t("extracting"),
        "translation_done": _t("translation_done"),
        "translation_failed": _t("translation_failed"),
    },
    "en": {
        "welcome": "=== BG3 Translator ===",
        "select_app_lang": "Select app language:",
        "menu_main": "\n=== MAIN MENU ===",
        "option_translate": "1. Translate mod",
        "option_config": "2. Settings",
        "option_exit": "3. Exit",
        "choice": "Choice: ",
        "config_menu": "\n=== SETTINGS ===",
        "config_saved": "Config saved.",
        "config_loaded": "Config loaded.",
        "config_cleared": "Config cleared.",
        "ask_mod_path": "Mod/folder path: ",
        "ask_target_lang": "Target language (e.g. pt, en, es): ",
        "ask_lslib": "Divine.exe path (blank for auto): ",
        "ask_generate_loca": "Generate .loca? (y/n): ",
        "ask_batch": "Batch mode? (y/n): ",
        "error_no_mod": "Error: Select a mod or folder.",
        "connecting": "Connecting to Google Translate...",
        "extracting": "Extracting .pak...",
        "translation_done": "Translation completed!",
        "translation_failed": "Translation failed.",
    },
    "es": {
        "welcome": "=== Traductor BG3 ===",
        "select_app_lang": "Seleccione el idioma de la aplicacion:",
        "menu_main": _t("menu_main"),
        "option_translate": "1. Traducir mod",
        "option_config": "2. Configuracion",
        "option_exit": "3. Salir",
        "choice": "Opcion: ",
        "config_menu": "\n=== CONFIGURACION ===",
        "config_saved": "Configuracion guardada.",
        "config_loaded": "Configuracion cargada.",
        "config_cleared": "Configuracion limpiada.",
        "ask_mod_path": "Ruta del mod/carpeta: ",
        "ask_target_lang": "Idioma de destino (ej: pt, en, es): ",
        "ask_lslib": "Ruta del Divine.exe (en blanco para auto): ",
        "ask_generate_loca": "Generar .loca? (s/n): ",
        "ask_batch": _t("ask_batch"),
        "error_no_mod": "Error: Seleccione un mod o carpeta.",
        "connecting": "Conectando a Google Translate...",
        "extracting": "Extrayendo .pak...",
        "translation_done": "Traduccion completada!",
        "translation_failed": "La traduccion fallo.",
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


DEFAULT_CONFIG = {
    "mod_folder": "",
    "lslib_path": "",

    "source_lang": "en",
    "target_lang": "pt",
    "auto_mode": True,
    "generate_loca": False,
    "batch_mode": False,
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Garante que todas as chaves existam
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"\n  Configuracoes salvas em: {CONFIG_FILE.name}")


def clear_config():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("  Configuracoes apagadas.")


CONFIG_META = {
    "mod_folder": {
        "desc": "Pasta padrao dos mods",
        "type": "path",
        "example": "C:\\Mods",
    },
    "lslib_path": {
        "desc": "Caminho do LSLib (Windows)",
        "type": "path",
        "example": "C:\\LSLib\\Divine.exe",
    },
    "source_lang": {
        "desc": "Idioma de origem",
        "type": "text",
        "example": "auto, en, pt, ja, ru...",
    },
    "target_lang": {
        "desc": "Idioma de destino",
        "type": "text",
        "example": "pt, en, ja, ru, fr...",
    },
    "auto_mode": {
        "desc": "Traducao automatica ou interativa",
        "type": "bool",
        "options": "true / false",
    },
    "generate_loca": {
        "desc": "Gerar arquivo .loca alem do .xml",
        "type": "bool",
        "options": "true / false",
    },
    "batch_mode": {
        "desc": "Modo unico ou lote",
        "type": "bool",
        "options": "true / false",
    },
}


def config_menu():
    """Menu para gerenciar configuracoes salvas."""
    cfg = load_config()
    print("\n" + "=" * 60)
    print("  Saved Configurations")
    print("=" * 60)
    for k, v in cfg.items():
        meta = CONFIG_META.get(k, {})
        desc = meta.get("desc", k)
        display = v if v else "(nao definido)"
        if meta.get("type") == "bool":
            display = str(v).lower()
            extra = f"  [{meta.get('options', 'true / false')}]"
        elif meta.get("type") == "path":
            extra = f"  [ex: {meta.get('example', 'caminho')}]"
        else:
            extra = f"  [ex: {meta.get('example', 'texto')}]"
        print(f"   {desc}")
        print(f"      {k}: {display}{extra}")
    print()
    print("  O que voce quer fazer?")
    print("    1 = Editar configuracoes")
    print("    2 = Limpar configuracoes (apagar)")
    print("    3 = Voltar")
    choice = input("   Escolha [1/2/3]: ").strip()

    if choice == "2":
        clear_config()
    elif choice == "1":
        print("\n  Deixa em branco pra manter o valor atual.")
        for k in DEFAULT_CONFIG:
            meta = CONFIG_META.get(k, {})
            desc = meta.get("desc", k)
            current = cfg.get(k, "")
            display = current if current else "(vazio)"
            if isinstance(DEFAULT_CONFIG[k], bool):
                display = str(current).lower()
            print(f"\n   {desc}")
            if meta.get("type") == "bool":
                print(f"      Opcoes: {meta.get('options', 'true / false')}")
            elif meta.get("example"):
                print(f"      Exemplo: {meta['example']}")
            val = input(f"   {k} [{display}]: ").strip().strip('"').strip("'")
            if val:
                # Converte tipos
                if isinstance(DEFAULT_CONFIG[k], bool):
                    cfg[k] = val.lower() in ("s", "sim", "yes", "y", "true", "1")
                else:
                    cfg[k] = val
        save_config(cfg)


# =============================================================================
# MAPEAMENTO DE IDIOMAS
# =============================================================================
# Mapeia nomes de pastas do BG3 para códigos do Google Translate
LANG_MAP = {
    # Nomes de pastas comuns no BG3 -> código Google Translate
    "english": "en",
    "brazilianportuguese": "pt",
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "italian": "it",
    "polish": "pl",
    "russian": "ru",
    "chinese": "zh-cn",
    "chinesetraditional": "zh-tw",
    "japanese": "ja",
    "korean": "ko",
    "turkish": "tr",
    "ukrainian": "uk",
    "czech": "cs",
    "hungarian": "hu",
    # Códigos diretos também funcionam
    "en": "en", "pt": "pt", "fr": "fr", "de": "de", "es": "es",
    "it": "it", "pl": "pl", "ru": "ru", "ja": "ja", "ko": "ko",
    "tr": "tr", "uk": "uk", "cs": "cs", "hu": "hu", "zh-cn": "zh-cn",
    "zh-tw": "zh-tw",
}

# Nomes amigáveis pra mostrar pro usuário
LANG_NAMES = {
    "en": "Inglês", "pt": "Português", "fr": "Francês", "de": "Alemão",
    "es": "Espanhol", "it": "Italiano", "pl": "Polonês", "ru": "Russo",
    "zh-cn": "Chinês (Simplificado)", "zh-tw": "Chinês (Tradicional)",
    "ja": "Japonês", "ko": "Coreano", "tr": "Turco", "uk": "Ucraniano",
    "cs": "Tcheco", "hu": "Húngaro",
}


def detect_source_lang(en_path: Path):
    """Detecta idioma de origem pelo nome da pasta do arquivo."""
    folder_name = en_path.parent.name.lower()
    code = LANG_MAP.get(folder_name)
    if code:
        return code
    # Tenta achar uma pasta-pai que corresponda
    for parent in en_path.parents:
        code = LANG_MAP.get(parent.name.lower())
        if code:
            return code
    return "en"  # fallback


def resolve_target_folder_name(target_lang: str):
    """Retorna o nome da pasta de destino no estilo BG3."""
    # Mapeamento reverso comum
    reverse = {
        "en": "English", "pt": "BrazilianPortuguese", "fr": "French",
        "de": "German", "es": "Spanish", "it": "Italian", "pl": "Polish",
        "ru": "Russian", "zh-cn": "Chinese", "zh-tw": "ChineseTraditional",
        "ja": "Japanese", "ko": "Korean", "tr": "Turkish", "uk": "Ukrainian",
        "cs": "Czech", "hu": "Hungarian",
    }
    return reverse.get(target_lang, target_lang.capitalize())


def ask_language(prompt, default="pt"):
    """Pergunta pro usuário qual idioma, com lista de opções."""
    print(f"\n  {prompt}")
    print("  Digita o codigo ou escolhe pelo numero:")
    codes = ["en", "pt", "fr", "de", "es", "it", "pl", "ru", "ja", "ko",
             "zh-cn", "zh-tw", "tr", "uk", "cs", "hu"]
    for i, code in enumerate(codes, 1):
        name = LANG_NAMES.get(code, code)
        marker = " <- padrao" if code == default else ""
        print(f"    {i:2}. {code:6} = {name}{marker}")
    print("    Ou digita qualquer codigo Google Translate (ex: 'hi' = Hindi)")
    while True:
        resp = input(f"   Escolha [Enter = {default}]: ").strip().lower()
        if not resp:
            return default
        # Se digitou numero
        if resp.isdigit():
            idx = int(resp) - 1
            if 0 <= idx < len(codes):
                return codes[idx]
            print("  Invalid number.")
            continue
        # Se digitou codigo direto
        if len(resp) <= 5:
            return resp
        print("  Codigo muito longo. Usa 2-5 letras, tipo 'pt' ou 'ja'.")


# =============================================================================
# UTILITARIOS
# =============================================================================
def ask_path(prompt, must_exist=True, default=""):
    while True:
        path_str = input(prompt).strip().strip('"').strip("'")
        if not path_str:
            if default:
                return Path(default)
            print("  You did not type anything. Please try again.")
            continue
        p = Path(path_str)
        if not p.exists():
            print(f"  Path not found: {p}")
            print("  Da uma olhadinha se ta certinho?")
            continue
        if p.is_dir():
            return p
        if must_exist and not p.is_file():
            print(f"  Isso nao parece um arquivo valido: {p}")
            continue
        return p


def ask_yes_no(question, default=True):
    default_str = "s" if default else "n"
    while True:
        resp = input(f"{question} [{'S/n' if default else 's/N'}]: ").strip().lower()
        if not resp:
            return default
        if resp in ("s", "sim", "yes", "y"):
            return True
        if resp in ("n", "nao", "no"):
            return False
        print("  Please answer with 'y' or 'n'.")


def find_file_in_dir(directory: Path, extensions):
    for ext in extensions:
        matches = list(directory.glob(f"*{ext}"))
        if len(matches) == 1:
            print(f"  Achei so um arquivo aqui: {matches[0].name} ✨")
            return matches[0]
        elif len(matches) > 1:
            print(f"  Opa, tem varios arquivos {ext} aqui:")
            for i, m in enumerate(matches, 1):
                print(f"    {i}. {m.name}")
            choice = input("  Which one do you want? (type the number or press Enter to cancel): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                return matches[int(choice) - 1]
            return None
    return None


def find_all_files_in_dir(directory: Path, extensions):
    result = {}
    for ext in extensions:
        matches = list(directory.glob(f"*{ext}"))
        if matches:
            result[ext] = matches[0]
    return result


def resolve_source(user_input: Path):
    """Resolve o caminho de entrada em um arquivo .xml/.loca de origem."""
    en_was_loca = False
    found_loca_also = False
    localization_parent = None

    # Arquivo direto
    if user_input.is_file():
        if user_input.suffix.lower() == ".loca":
            en_was_loca = True
        # Verifica se tem .loca/.xml irmao
        sibling = user_input.with_suffix(".loca" if user_input.suffix.lower() == ".xml" else ".xml")
        if sibling.exists():
            found_loca_also = True
        for parent in user_input.parents:
            if parent.name.lower() == "localization":
                localization_parent = parent
                break
        return user_input, en_was_loca, found_loca_also, localization_parent

    # Pasta Localization/
    if user_input.name.lower() == "localization":
        localization_parent = user_input
        # Coleta TODAS as subpastas de idioma validas
        lang_options = []
        for child in user_input.iterdir():
            if child.is_dir() and child.name.lower() in LANG_MAP:
                xml_file = find_file_in_dir(child, [".xml"])
                loca_file = find_file_in_dir(child, [".loca"])
                if xml_file or loca_file:
                    lang_options.append({
                        "path": child,
                        "name": child.name,
                        "xml": xml_file,
                        "loca": loca_file,
                    })

        if len(lang_options) > 1:
            # Preferencia automatica: English primeiro, senao a primeira disponivel
            selected = lang_options[0]
            for opt in lang_options:
                if opt["name"].lower() == "english":
                    selected = opt
                    break
            print(f"  Found {len(lang_options)} languages. Using '{selected['name']}' as source.")
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

        # Procura direto na Localization/ (sem subpastas de idioma)
        xml_file = find_file_in_dir(user_input, [".xml"])
        if xml_file:
            return xml_file, False, False, localization_parent
        loca_file = find_file_in_dir(user_input, [".loca"])
        if loca_file:
            return loca_file, True, False, localization_parent
        return None, False, False, None

    # Pasta generica — procura Localization/ em qualquer nivel
    for loc_dir in user_input.rglob("Localization"):
        if loc_dir.is_dir():
            return resolve_source(loc_dir)

    # Procura arquivos diretamente na pasta
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


def _force_rmtree(path: Path):
    """Remove pasta forcando permissao em arquivos read-only (Windows)."""
    import stat
    def onerror(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass
    shutil.rmtree(path, onerror=onerror)


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
    print(f"  Created folder: {target_folder}/")
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
        print(f"  Created folder: {target_folder}/")
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
# CONVERSOR .LOCA <-> .XML (integrado — nao precisa de arquivo externo)
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
    """Le .loca e retorna string XML."""
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
    """Le XML e retorna bytes .loca."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    contents = [c for c in root.findall('content') if c.get('contentuid', '').strip()]
    n = len(contents)
    strings_offset = 12 + n * 70

    out = bytearray()
    if format_hint == "LOCA":
        out.extend(b"LOCA")
        out.extend(struct.pack("<I", n))
        out.extend(struct.pack("<I", strings_offset))
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
    print(f"  Convertendo .loca pra .xml... {xml_path.name}")
    try:
        xml_str, fmt = loca_to_xml_bytes(loca_path)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(f"  Convertido! Formato: {fmt}")
        return True
    except Exception as e:
        print(f"  Erro na conversao .loca -> .xml: {e}")
        return False


def xml_file_to_loca(xml_path: Path, loca_path: Path, format_hint="LOCA"):
    print(f"  Convertendo .xml pra .loca... {loca_path.name}")
    try:
        loca_bytes = xml_to_loca_bytes(xml_path, format_hint)
        loca_path.parent.mkdir(parents=True, exist_ok=True)
        with open(loca_path, "wb") as f:
            f.write(loca_bytes)
        print("  .loca generated successfully!")
        return True
    except Exception as e:
        print(f"  Erro na conversao .xml -> .loca: {e}")
        return False


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


def translate_text(text, translator, max_retries=3):
    if not text or not text.strip():
        return text
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            result = translator.translate(text)
            if result and result.strip():
                return result
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                import time
                time.sleep(1.5)
    print(f"    Nao consegui traduzir esse trecho: '{text[:80]}...' — {last_err}")
    return text  # retorna o original em vez de None


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
    """Garante que o caminho do LSLib seja o Divine.exe."""
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


def _run_lslib_cmd(lslib_path: Path, args: list):
    """Executa Divine.exe da forma mais simples possivel (igual ao cmd)."""
    cmd = [str(lslib_path)] + args
    print(f"  [LSLib] Comando: {' '.join(cmd)}")

    kwargs = {"capture_output": True, "text": True, "check": True}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        result = subprocess.run(cmd, **kwargs)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)


def extract_pak(pak_path: Path, output_dir: Path, lslib_path: Path):
    if not lslib_path or not lslib_path.exists():
        print("  Caminho do LSLib nao fornecido ou invalido.")
        return False
    print(f"  Extraindo .pak com LSLib... {pak_path.name}")
    success, stdout, stderr = _run_lslib_cmd(
        lslib_path,
        ["-g", "bg3", "-a", "extract-package", "-s", str(pak_path), "-d", str(output_dir)]
    )
    if success:
        print(f"  Extraido com sucesso em: {output_dir}")
        return True
    else:
        print(f"  Erro ao extrair .pak: {stderr}")
        if "permissao" in stderr.lower() or "permission" in stderr.lower():
            print("  Dica: Executa o script como Administrador (botao direito -> Executar como Administrador)")
        return False


def create_pak(source_dir: Path, pak_path: Path, lslib_path: Path):
    if not lslib_path or not lslib_path.exists():
        print("  Caminho do LSLib nao fornecido ou invalido.")
        return False
    print(f"  Recompactando .pak com LSLib... {pak_path.name}")

    if not source_dir.exists():
        print(f"  Erro: pasta fonte nao existe: {source_dir}")
        return False

    # Backup do original
    backups_dir = pak_path.parent / "_backups"
    backups_dir.mkdir(exist_ok=True)
    backup_path = backups_dir / (pak_path.name + ".original")
    if not backup_path.exists():
        shutil.copy2(pak_path, backup_path)
        print(f"  Backup criado: _backups/{backup_path.name}")

    # Remove o original antes de recriar
    pak_path.unlink()

    # Cria o novo .pak diretamente no destino final
    cmd_args = [
        "-g", "bg3",
        "-a", "create-package",
        "-c", "lz4",
        "-s", str(source_dir),
        "-d", str(pak_path),
    ]
    success, stdout, stderr = _run_lslib_cmd(lslib_path, cmd_args)

    if not success:
        print(f"  Erro ao criar .pak: {stderr}")
        if stdout:
            print(f"  stdout: {stdout}")
        # Restaura o backup
        if backup_path.exists():
            shutil.copy2(backup_path, pak_path)
            print(f"  Backup restaurado.")
        return False

    # Verifica se o .pak foi gerado com tamanho razoavel
    if not pak_path.exists() or pak_path.stat().st_size < 1024:
        print(f"  Erro: .pak gerado esta vazio ou muito pequeno ({pak_path.stat().st_size if pak_path.exists() else 0} bytes)")
        if stdout:
            print(f"  stdout: {stdout}")
        if stderr:
            print(f"  stderr: {stderr}")
        # Restaura o backup
        if backup_path.exists():
            shutil.copy2(backup_path, pak_path)
            print(f"  Backup restaurado.")
        return False

    print(f"  .pak criado com sucesso: {pak_path} ({pak_path.stat().st_size} bytes)")
    return True


# =============================================================================
# SCANNER DE MODS
# =============================================================================
def scan_mods_folder(root_dir: Path):
    mods = []
    for pak in root_dir.rglob("*.pak"):
        # Ignora .paks dentro de pastas extraidas (pasta com mesmo nome do .pak)
        if pak.parent.name.lower() != pak.stem.lower():
            mods.append({"type": "pak", "path": pak, "name": pak.stem})
    for loc_dir in root_dir.rglob("Localization"):
        if loc_dir.is_dir():
            # Procura qualquer pasta de idioma dentro de Localization/
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
# TRADUCAO SINGLE
# =============================================================================
def process_single_mod(en_path, localization_parent, en_was_loca, found_loca_also,
                       translator, auto_mode, target_lang="pt"):
    target_folder = resolve_target_folder_name(target_lang)
    if localization_parent:
        if found_loca_also:
            generate_loca = ask_yes_no(f"   Tambem achei um .loca aqui. Quer que eu gere o .loca traduzido tambem?")
        else:
            generate_loca = en_was_loca
        pt_path, pt_loca_path, pt_should_loca = resolve_target_auto(
            localization_parent, en_path, en_was_loca, generate_loca, target_lang
        )
    else:
        print(f"\n[Destination] Where to save the translation?")
        print(f"   (Pasta Localization/ cria {target_folder}/ automaticamente)")
        pt_input = ask_path("   Caminho: ", must_exist=False)
        if found_loca_also or en_was_loca:
            generate_loca = ask_yes_no("   Vi que tem um .loca tambem. Quer que eu gere o .loca traduzido?")
        else:
            generate_loca = False
        pt_path, pt_loca_path, pt_should_loca = resolve_target_manual(
            pt_input, en_path, en_was_loca, generate_loca, target_lang
        )

    xml_en_path = en_path
    tmp_xml_en = None
    if en_was_loca:
        tmp_xml_en = Path(tempfile.gettempdir()) / f"tradutor_bg3_{en_path.stem}.xml"
        if not loca_file_to_xml(en_path, tmp_xml_en):
            return False, None
        xml_en_path = tmp_xml_en

    print(f"\n  Abrindo o arquivo... {xml_en_path.name}")
    with open(xml_en_path, "r", encoding="utf-8") as f:
        raw_en = f.read()

    handles = []
    for m in re.finditer(r'(<content contentuid="([^"]+)"[^>]*>)(.*?)(</content>)', raw_en, re.DOTALL):
        handles.append((m.group(1), m.group(2), m.group(3), m.group(4)))

    print(f"  Found {len(handles)} texts to translate.")
    if not handles:
        print("  Nenhum <content> encontrado.")
        return False, None

    translated_count = 0
    skipped_count = 0
    error_count = 0
    raw_pt = raw_en

    for i, (open_tag, uid, content, close_tag) in enumerate(handles, 1):
        protected, placeholders = protect(content)
        translated = translate_text(protected, translator)
        if translated is None:
            error_count += 1
            continue
        restored = restore(translated, placeholders)

        if not auto_mode:
            print(f"\n--- [{i}/{len(handles)}] UID: {uid} ---")
            print(f"   Original:  {content[:200]}")
            print(f"   Traducao:  {restored[:200]}")
            resp = input("   Do you approve? [y/n/q]: ").strip().lower()
            if resp == "q":
                print("   Stopping here.")
                break
            if resp != "s":
                skipped_count += 1
                continue

        old = open_tag + content + close_tag
        new = open_tag + restored + close_tag
        raw_pt = raw_pt.replace(old, new, 1)
        translated_count += 1

        if auto_mode and i % 10 == 0:
            print(f"   ... translated {i} of {len(handles)}")

    print(f"\n  Salvando XML: {pt_path}")
    pt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pt_path, "w", encoding="utf-8") as f:
        f.write(raw_pt)
    print(f"  Traduzidos: {translated_count} | Pulados: {skipped_count} | Erros: {error_count}")

    print("\n  Conferindo XML...")
    try:
        ET.parse(str(pt_path))
        print("  XML ta perfeito! ✨")
    except ET.ParseError as e:
        print(f"  Problema no XML: {e}")
        return False, None

    if pt_should_loca:
        fmt = "LOCA"
        xml_file_to_loca(pt_path, pt_loca_path, fmt)

    if tmp_xml_en and tmp_xml_en.exists():
        tmp_xml_en.unlink()

    return True, pt_path


# =============================================================================
# MAIN
# =============================================================================
def main():
    # Pergunta idioma do app na primeira vez
    cfg = load_config()
    if not cfg.get("app_lang"):
        print("\n" + "=" * 60)
        print("  Selecione o idioma do aplicativo / Select app language")
        print("=" * 60)
        print("  1 = Portugues")
        print("  2 = English")
        print("  3 = Espanol")
        lang_choice = input("  Escolha: ").strip()
        lang_map = {"1": "pt", "2": "en", "3": "es"}
        cfg["app_lang"] = lang_map.get(lang_choice, "pt")
        save_config(cfg)
        print(f"  Idioma definido: {cfg['app_lang']}\n")

    print("=" * 60)
    print("  Welcome to BG3 Translator")
    print("  Vou traduzir seu mod do BG3 pro idioma que voce quiser!")
    print("  Deixa comigo que eu cuido de tudo!")
    print("=" * 60)

    # Verifica se tem config salva com valores uteis
    has_config = (
        CONFIG_FILE.exists()
        and any(
            v for v in cfg.values()
            if v and isinstance(v, str) and v.strip()
        )
    )

    if has_config:
        print("\nYou have saved configurations!")
        use_saved = ask_yes_no("   Quer usar as configs salvas e ir direto?")
        if not use_saved:
            print("\n  Let's go step by step.")
            cfg = dict(DEFAULT_CONFIG)
    else:
        use_saved = False

    # Menu de configuracoes (se nao for usar salvas)
    if not use_saved:
        print("\n  Quer acessar as configuracoes antes de comecar?")
        print("    1 = Ir direto pra traducao")
        print("    2 = Configuracoes salvas (editar/limpar)")
        menu_choice = input("   Escolha [1/2]: ").strip()
        if menu_choice == "2":
            config_menu()
            cfg = load_config()
            use_saved = ask_yes_no("   Agora quer usar as configs salvas?")

    # Determina idiomas
    source_lang = cfg.get("source_lang", "auto")
    target_lang = cfg.get("target_lang", "pt")

    if not use_saved:
        print("\nWhich language do you want as the TARGET of the translation?")
        target_lang = ask_language("Idioma de destino:", default=target_lang)
        cfg["target_lang"] = target_lang
        print(f"\n  Perfect! I will translate -> {LANG_NAMES.get(target_lang, target_lang)}")

    # Inicializa tradutor (source sera detectado automaticamente por mod)
    print("\n  Conectando com o Google Translator...")
    try:
        # Usamos 'auto' como source padrao; sera ajustado por mod
        translator = GoogleTranslator(source="auto", target=target_lang)
    except Exception as e:
        print(f"  Nao consegui conectar no tradutor: {e}")
        print("  Verifica sua internet?")
        return

    # Determina modo (batch ou unico)
    if use_saved and cfg.get("batch_mode"):
        batch_mode = True
    elif use_saved and not cfg.get("batch_mode"):
        batch_mode = False
    else:
        print("\nDo you want to translate a single mod, or a folder full of mods?")
        print("   1 = Um mod unico")
        print("   2 = Varias mods de uma vez (lote)")
        modo_global = input("   Escolhe ai [1 ou 2]: ").strip()
        batch_mode = (modo_global == "2")
        cfg["batch_mode"] = batch_mode

    # ==========================================
    # MODO UNICO
    # ==========================================
    if not batch_mode:
        print(f"\n[1/3] Show me the mod file/folder:")
        print("   (Pode ser .xml, .loca, .pak, uma pasta, ou so Localization/)")
        if use_saved and cfg.get("mod_folder"):
            en_input = Path(cfg["mod_folder"])
            if en_input.exists():
                print(f"  Usando das configs: {en_input}")
            else:
                print(f"  Pasta das configs nao existe mais: {en_input}")
                en_input = ask_path("   Caminho: ", must_exist=True)
        else:
            en_input = ask_path("   Caminho: ", must_exist=True)

        lslib_path = None
        extracted_dir = None
        original_pak = None
        use_lslib = False

        if en_input.is_file() and en_input.suffix.lower() == ".pak":
            print("\n  Detectei um arquivo .pak!")
            original_pak = en_input
            if use_saved and cfg.get("lslib_path"):
                lslib_path = resolve_lslib_path(Path(cfg["lslib_path"]))
                if lslib_path and lslib_path.exists():
                    print(f"  Usando LSLib das configs: {lslib_path}")
                    use_lslib = ask_yes_no("  Quer que eu extraia e traduzo o .pak?")
                else:
                    lslib_path = None
            if not lslib_path:
                auto_lslib = find_lslib_exe()
                if auto_lslib:
                    print(f"  Achei o LSLib aqui: {auto_lslib}")
                    use_lslib = ask_yes_no("  Quer que eu extraia e traduzo o .pak?")
                    if use_lslib:
                        lslib_path = auto_lslib
                else:
                    print("  Nao achei o LSLib automaticamente.")
                    lslib_str = input("  Caminho do LSLib (Divine.exe, converterapp.exe ou pasta): ").strip().strip('"').strip("'")
                    lslib_path = resolve_lslib_path(Path(lslib_str)) if lslib_str else None
                    use_lslib = lslib_path and lslib_path.exists() and lslib_path.is_file()
                    if not use_lslib and lslib_str:
                        print("  Caminho invalido. Vou continuar sem LSLib.")

            if use_lslib:
                extracted_dir = en_input.parent / en_input.stem
                if not extract_pak(en_input, extracted_dir, lslib_path):
                    print("  Nao consegui extrair o .pak 😢")
                    return
                en_input = extracted_dir

        en_path, en_was_loca, found_loca_also, localization_parent = resolve_source(en_input)
        if not en_path:
            print("\n  Nao achei nenhum arquivo .xml ou .loca 😢")
            if extracted_dir and extracted_dir.exists():
                _force_rmtree(extracted_dir)
            return
        print(f"  Perfeito! Vou usar: {en_path.name} ✨")

        # Modo (auto ou interativo)
        if use_saved:
            auto_mode = cfg.get("auto_mode", True)
            print(f"\n  Modo: {'Automatico' if auto_mode else 'Interativo'} (das configs)")
        else:
            print("\nHow do you want me to translate?")
            print("   1 = Automatico (vou traduzir tudo sozinha)")
            print("   2 = Interativo (pergunto um a um)")
            modo = input("   Escolhe ai [1 ou 2]: ").strip()
            auto_mode = (modo == "1")
            cfg["auto_mode"] = auto_mode

        # Detecta idioma de origem automaticamente
        detected_src = detect_source_lang(en_path)
        if detected_src != "auto":
            print(f"  Detected source language: {LANG_NAMES.get(detected_src, detected_src)}")
            try:
                translator = GoogleTranslator(source=detected_src, target=target_lang)
            except Exception:
                pass  # mantem o tradutor auto se der erro

        success, _ = process_single_mod(en_path, localization_parent, en_was_loca,
                                        found_loca_also, translator, auto_mode, target_lang)

        # Recompacta .pak
        if success and use_lslib and original_pak and lslib_path:
            print("\n  Recompactando o .pak traduzido...")
            if create_pak(extracted_dir, original_pak, lslib_path):
                print("  .pak traduzido e recompactado com sucesso! ✨")
            else:
                print("  Nao consegui recompactar o .pak 😢")
                print(f"  Mas os arquivos extraidos estao em: {extracted_dir}")

        if extracted_dir and extracted_dir.exists():
            _force_rmtree(extracted_dir)
            print(f"\n  Limpei arquivos temporarios")

        # Pergunta se quer salvar configs
        if not use_saved:
            cfg["mod_folder"] = str(en_input)
            if lslib_path:
                cfg["lslib_path"] = str(lslib_path)
            print()
            if ask_yes_no("Do you want to save these settings for next time?"):
                save_config(cfg)

        print("\n" + "=" * 60)
        print("  Done! Everything translated successfully.")
        print("=" * 60)
        return

    # ==========================================
    # MODO LOTE
    # ==========================================
    print("\n[Batch] Show me the folder full of mods:")
    if use_saved and cfg.get("mod_folder"):
        batch_dir = Path(cfg["mod_folder"])
        if batch_dir.exists():
            print(f"  Usando das configs: {batch_dir}")
        else:
            print(f"  Pasta das configs nao existe mais: {batch_dir}")
            batch_dir = ask_path("   Caminho da pasta: ", must_exist=True)
    else:
        batch_dir = ask_path("   Caminho da pasta: ", must_exist=True)

    if not batch_dir.is_dir():
        print("  Isso nao e uma pasta 😢")
        return

    mods = scan_mods_folder(batch_dir)
    print(f"\n  Found {len(mods)} mods to translate.")
    if not mods:
        print("  Nao achei nenhum mod (.pak ou Localization/) nessa pasta.")
        if not use_saved:
            cfg["mod_folder"] = str(batch_dir)
            print()
            if ask_yes_no("Quer salvar essas configuracoes pra proxima vez?"):
                save_config(cfg)
        return

    for i, mod in enumerate(mods, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/{len(mods)}] Translating: {mod['name']}")
        print(f"{'='*60}")

        extracted_dir = None
        original_pak = None
        lslib_path = None
        use_lslib = False
        mod_input = mod["path"]

        if mod["type"] == "pak":
            print("  Detectei um .pak!")
            original_pak = mod["path"]
            if use_saved and cfg.get("lslib_path"):
                lslib_path = resolve_lslib_path(Path(cfg["lslib_path"]))
                if lslib_path and lslib_path.exists():
                    use_lslib = True
                    print(f"  Usando LSLib das configs: {lslib_path}")
                else:
                    lslib_path = None
            if not lslib_path:
                auto_lslib = find_lslib_exe()
                if auto_lslib:
                    print(f"  LSLib encontrado: {auto_lslib}")
                    lslib_path = auto_lslib
                    use_lslib = True
                else:
                    lslib_str = input("  Caminho do LSLib (Divine.exe, converterapp.exe ou pasta): ").strip().strip('"').strip("'")
                    lslib_path = resolve_lslib_path(Path(lslib_str)) if lslib_str else None
                    use_lslib = lslib_path and lslib_path.exists() and lslib_path.is_file()
                    if not use_lslib and lslib_str:
                        print("  Caminho invalido. Pulando .pak...")
                        continue
                    elif not use_lslib:
                        print("  Sem LSLib, pulando .pak...")
                        continue

            if use_lslib:
                extracted_dir = mod["path"].parent / mod["path"].stem
                if extract_pak(mod["path"], extracted_dir, lslib_path):
                    mod_input = extracted_dir
                else:
                    print("  Pulando esse mod...")
                    continue

        en_path, en_was_loca, found_loca_also, localization_parent = resolve_source(mod_input)
        if not en_path:
            print("  Nao achei arquivos de localizacao nesse mod.")
            if extracted_dir and extracted_dir.exists():
                _force_rmtree(extracted_dir)
            continue

        # Detecta idioma de origem automaticamente
        detected_src = detect_source_lang(en_path)
        if detected_src != "auto":
            print(f"  Detected source language: {LANG_NAMES.get(detected_src, detected_src)}")
            try:
                translator = GoogleTranslator(source=detected_src, target=target_lang)
            except Exception:
                pass

        success, _ = process_single_mod(en_path, localization_parent, en_was_loca,
                                        found_loca_also, translator, True, target_lang)

        if success and use_lslib and original_pak and lslib_path:
            print("\n  Recompactando .pak...")
            if create_pak(extracted_dir, original_pak, lslib_path):
                print("  .pak recompactado! ✨")
            else:
                print(f"  Falhou, mas arquivos estao em: {extracted_dir}")

        if extracted_dir and extracted_dir.exists():
            _force_rmtree(extracted_dir)

    # Salva configs do lote
    if not use_saved:
        cfg["mod_folder"] = str(batch_dir)
        if lslib_path:
            cfg["lslib_path"] = str(lslib_path)
        print()
        if ask_yes_no("Do you want to save these settings for next time?"):
            save_config(cfg)

    print("\n" + "=" * 60)
    print(f"  Done! {len(mods)} mods processed.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "=" * 60)
        print("  An unexpected error occurred.")
        print("=" * 60)
        print(f"\n  Tipo do erro: {type(e).__name__}")
        print(f"  Mensagem: {e}")
        print("\n  Detalhes completos:")
        traceback.print_exc()
        print(f"\n  Log salvo em: {LOG_FILE}")
        print("=" * 60)
        sys.exit(1)
    finally:
        if sys.platform == "win32":
            input("\n  Press Enter to close...")
        if hasattr(sys.stdout, 'close'):
            sys.stdout.close()
        sys.stdout = sys.__stdout__
