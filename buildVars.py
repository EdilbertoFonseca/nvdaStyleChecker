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

Created on: 13/09/2026
"""

# Function copied from: AddonTemplate (NVDA add-on)
# Original source: utils.py
# License: GNU GPL v2.0 – https://www.gnu.org/licenses/gpl-2.0.html
# Repository: https://github.com/nvaccess/addonTemplate
def _(arg: str) -> str:
	"""
	A function that passes the string to it without doing anything to it.
	Needed for recognizing strings for translation by Gettext.
	"""
	return arg

# Application information
app_info = {
	"app_name": "nvdaStyleChecker,",
	"app_summary": _("System for code validations"),
	"app_description": _(
		"System for checking add-on code and performing validation"
	),
	"app_version": "1.1.0",
	"app_author": "Edilberto Fonseca <edilberto.fonseca@outlook.com>",
	"spec_file": "install/pyinstaller/nvdaStyleChecker.spec",
	"script_name": "src/main.py",
}

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = ["buildVars.py"]
