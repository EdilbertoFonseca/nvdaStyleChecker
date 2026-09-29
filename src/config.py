# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 - 2026 Edilberto Fonseca
This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

-------------------------------------------------------------------------
AI DISCLOSURE / NOTA DE IA:
This project utilizes AI for code refactoring and logic suggestions.
All AI-generated code was manually reviewed and tested by the author.
-------------------------------------------------------------------------

Created on: 10/09/2026

NVDA Add-on Style & Manifest Checker - Graphical User Interface (GUI).
Accessible interface built with wxPython for NVDA screen reader users.
"""

import gettext
import re
import sys
from pathlib import Path

# --- Locale Path Configuration ---
if getattr(sys, "frozen", False):
	# When run via PyInstaller (automatically accesses the internal / _internal folder)
	MEIPASS = getattr(sys, "_MEIPASS", None)
	if isinstance(MEIPASS, str):
		baseDir = Path(MEIPASS)
	else:
		baseDir = Path(__file__).parent
else:
	# When run in development mode (VS Code, F5, etc.)
	baseDir = Path(__file__).parent

# --- Locale Configuration ---
BASE_DIR = baseDir
LOCALE_DIR = BASE_DIR / "locale"
DOMAIN = "main"

try:
	# Attempts to load the translation from the detected locale folder.
	translation = gettext.translation(DOMAIN, localedir=LOCALE_DIR, languages=["pt_BR"], fallback=False)
	_ = translation.gettext
except Exception:

	def _(message: str) -> str:
		return message  # --- Regular Expression Patterns ---


CAMEL_CASE_PATTERN = re.compile(r"^[a-z]+(?:[A-Z0-9][a-z0-9]*)*$")
PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
UPPER_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")

# Common Python/NVDA parameters and names to ignore during camelCase check
IGNORED_ARGUMENTS = {
	"self",
	"cls",
	"decorated_cls",
	"wrapped_func",
	"fn",
	"func",
}

# Required keys in NVDA's manifest.ini file
REQUIRED_MANIFEST_KEYS = {
	"name": "Add-on technical name",
	"summary": "Short title/summary",
	"version": "Add-on version",
	"description": "Detailed description",
	"author": "Author(s)",
	"minimumNVDAVersion": "Minimum supported NVDA version",
	"lastTestedNVDAVersion": "Last tested NVDA version",
}
