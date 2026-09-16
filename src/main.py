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
"""

"""
NVDA Add-on Style & Manifest Checker - Graphical User Interface (GUI).
Accessible interface built with wxPython for NVDA screen reader users.
"""

import ast
import gettext
import io
import re

# --- Internationalization (i18n) Setup ---
import sys
from pathlib import Path

import wx

# --- Locale Path Configuration ---
if getattr(sys, 'frozen', False):
	# When run via PyInstaller (automatically accesses the internal / _internal folder)
	BASE_DIR = Path(sys._MEIPASS)
else:
	# When run in development mode (VS Code, F5, etc.)
	BASE_DIR = Path(__file__).parent

LOCALE_DIR = BASE_DIR / "locale"
DOMAIN = "main"

try:
	# Attempts to load the translation from the detected locale folder.
	translation = gettext.translation(DOMAIN, localedir=LOCALE_DIR, languages=["pt_BR"], fallback=False)
	_ = translation.gettext
except Exception:
	def _(message):
		return message# --- Regular Expression Patterns ---

CAMEL_CASE_PATTERN = re.compile(r"^[a-z]+(?:[A-Z0-9][a-z0-9]*)*$")
PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
UPPER_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")

# Common Python/NVDA parameters and names to ignore during camelCase check
IGNORED_ARGUMENTS = {
	"self", "cls", "decorated_cls", "wrapped_func", "fn", "func"
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


# --- Python Code Checker Class ---
class NVDAStyleChecker:
	"""Check Python source code against NVDA add-on style rules."""

	def __init__(self, file_path):
		self.file_path = Path(file_path)
		self.source = ""
		self.lines = []
		self.tree = None

		self.results = {
			"pascal_case": False,
			"upper_snake_case": False,
			"camel_case": False,
			"tabs": False,
			"header": False,
			"utf8": False,
			"i18n": False,
		}

		self.details = {
			"pascal_case": [],
			"upper_snake_case": [],
			"camel_case": [],
			"tabs": [],
			"header": "",
			"utf8": "",
			"i18n": [],
		}

	def read_file(self):
		try:
			self.source = self.file_path.read_text(encoding="utf-8")
		except UnicodeDecodeError:
			self.source = self.file_path.read_text(
				encoding="latin-1", errors="replace"
			)
		self.lines = self.source.splitlines()

	def parse_file(self):
		try:
			self.tree = ast.parse(
				self.source,
				filename=str(self.file_path),
			)
			return True, None
		except SyntaxError as error:
			err_msg = _("Syntax error at line {line_no}: {error_msg}").format(
				line_no=error.lineno, error_msg=error.msg
			)
			return False, err_msg

	def check_pascal_case(self):
		if self.tree is None:
			return
		invalid_names = set()
		for node in ast.walk(self.tree):
			if isinstance(node, ast.ClassDef):
				if not PASCAL_CASE_PATTERN.fullmatch(node.name):
					invalid_names.add(
						_("line {line_no}: class '{name}'").format(
							line_no=node.lineno, name=node.name
						)
					)
		sorted_details = sorted(list(invalid_names))
		self.details["pascal_case"] = sorted_details
		self.results["pascal_case"] = not sorted_details

	def check_upper_snake_case(self):
		if self.tree is None:
			return
		invalid_names = set()
		for node in self.tree.body:
			if isinstance(node, (ast.Assign, ast.AnnAssign)):
				targets = node.targets if isinstance(node, ast.Assign) else [node.target]
				for target in targets:
					if isinstance(target, ast.Name):
						var_name = target.id
						if var_name.startswith("__") and var_name.endswith("__"):
							continue
						if var_name.startswith("_"):
							continue
						if not UPPER_SNAKE_CASE_PATTERN.fullmatch(var_name):
							invalid_names.add(
								_("line {line_no}: global constant '{name}'").format(
									line_no=node.lineno, name=var_name
								)
							)
		sorted_details = sorted(list(invalid_names))
		self.details["upper_snake_case"] = sorted_details
		self.results["upper_snake_case"] = not sorted_details

	def check_camel_case(self):
		if self.tree is None:
			return
		invalid_names = set()
		for node in ast.walk(self.tree):
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				name = node.name
				if name.startswith("__") and name.endswith("__"):
					continue

				check_name = name
				if check_name.startswith("script_"):
					check_name = check_name[7:]
				elif check_name.startswith("event_"):
					check_name = check_name[6:]

				if not CAMEL_CASE_PATTERN.fullmatch(check_name):
					invalid_names.add(
						_("line {line_no}: function '{name}'").format(
							line_no=node.lineno, name=name
						)
					)

				for arg in node.args.args:
					arg_name = arg.arg
					if arg_name in IGNORED_ARGUMENTS or arg_name.startswith("_"):
						continue
					if not CAMEL_CASE_PATTERN.fullmatch(arg_name):
						invalid_names.add(
							_("line {line_no}: argument '{name}'").format(
								line_no=arg.lineno, name=arg_name
							)
						)

			elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
				if node in self.tree.body:
					continue
				name = node.id
				if name.startswith("_") or name.isupper() or name in IGNORED_ARGUMENTS:
					continue
				if not CAMEL_CASE_PATTERN.fullmatch(name):
					invalid_names.add(
						_("line {line_no}: variable '{name}'").format(
							line_no=node.lineno, name=name
						)
					)

		sorted_details = sorted(list(invalid_names))
		self.details["camel_case"] = sorted_details
		self.results["camel_case"] = not sorted_details

	def check_tabs(self):
		indentation_found = False
		invalid_lines = []

		for line_number, line in enumerate(self.lines, start=1):
			if not line.strip():
				continue
			leading_whitespace = line[: len(line) - len(line.lstrip())]
			if not leading_whitespace:
				continue

			indentation_found = True
			if " " in leading_whitespace:
				invalid_lines.append(line_number)

		self.results["tabs"] = not invalid_lines

		if invalid_lines:
			self.details["tabs"] = [
				_("line {line_no}: contains space(s) in indentation").format(
					line_no=line_no
				)
				for line_no in invalid_lines
			]
		elif indentation_found:
			self.details["tabs"] = [_("All indented lines use tabs.")]
		else:
			self.details["tabs"] = [_("The file has no indented lines.")]

	def check_header(self):
		if not self.lines:
			self.details["header"] = _("Empty file.")
			return

		header_lines = []
		for line in self.lines[:20]:
			lower_line = line.lower()
			if any(
				keyword in lower_line
				for keyword in (
					"author:",
					"copyright:",
					"gnu general public license",
					"this file is covered by",
				)
			):
				header_lines.append(line.strip())

		self.results["header"] = bool(header_lines)
		self.details["header"] = (
			_("Header identified.")
			if header_lines
			else _("No standard header identified.")
		)

	def check_utf8(self):
		encoding_pattern = re.compile(r"coding[=:]\s*([-\w.]+)", re.IGNORECASE)
		encoding = None

		for line in self.lines[:2]:
			match = encoding_pattern.search(line)
			if match:
				encoding = match.group(1)
				break

		if encoding and re.search(r"utf[-_]?8", encoding, re.IGNORECASE):
			self.results["utf8"] = True
			self.details["utf8"] = _("UTF-8 encoding declaration found.")
		else:
			self.results["utf8"] = False
			self.details["utf8"] = _("UTF-8 encoding declaration not found.")

	def check_i18n(self):
		"""Check for UI/message strings missing _() translation wrappers."""
		if self.tree is None:
			return

		untranslated = set()

		for node in ast.walk(self.tree):
			if isinstance(node, ast.Call):
				func_name = ""
				if isinstance(node.func, ast.Name):
					func_name = node.func.id
				elif isinstance(node.func, ast.Attribute):
					func_name = node.func.attr

				if func_name in ("_", "pgettext", "npgettext", "ngettext"):
					continue

				for arg in node.args:
					if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
						val = arg.value.strip()
						if len(val) > 1 and not val.startswith("http") and " " in val:
							untranslated.add(
								_("line {line_no}: \"{value}...\"").format(
									line_no=arg.lineno, value=val[:30]
								)
							)

				for keyword in node.keywords:
					if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
						val = keyword.value.value.strip()
						if len(val) > 1 and not val.startswith("http") and " " in val:
							untranslated.add(
								_("line {line_no}: {arg}=\"{value}...\"").format(
									line_no=keyword.value.lineno,
									arg=keyword.arg,
									value=val[:30],
								)
							)

		sorted_details = sorted(list(untranslated))
		self.details["i18n"] = sorted_details
		self.results["i18n"] = not sorted_details

	def analyze(self):
		self.read_file()
		parsed_success, error_msg = self.parse_file()
		if not parsed_success:
			return False, error_msg

		self.check_pascal_case()
		self.check_upper_snake_case()
		self.check_camel_case()
		self.check_tabs()
		self.check_header()
		self.check_utf8()
		self.check_i18n()

		return True, None

	def generate_report_text(self):
		points = sum(1 for result in self.results.values() if result)
		total = len(self.results)
		percentage = (points / total) * 100

		output = []
		output.append("============================================================")
		output.append(_("STYLE ANALYSIS - PYTHON FILE (.PY)"))
		output.append("============================================================\n")
		output.append(_("Analyzed file: {file_path}\n").format(file_path=self.file_path))

		output.append(self._format_line(_("Classes in PascalCase"), self.results["pascal_case"]))
		output.append(self._format_line(_("Global constants in UPPER_SNAKE_CASE"), self.results["upper_snake_case"]))
		output.append(self._format_line(_("Functions and variables in camelCase"), self.results["camel_case"]))
		output.append(self._format_line(_("Indentation using tabs"), self.results["tabs"]))
		output.append(self._format_line(_("Presence of standard header"), self.results["header"]))
		output.append(self._format_line(_("UTF-8 encoding declaration"), self.results["utf8"]))
		output.append(self._format_line(_("Strings marked for translation _()"), self.results["i18n"]))

		output.append("\n" + "-" * 60)
		output.append(_("Score: {points}/{total} points").format(points=points, total=total))
		output.append(_("Compliance: {percentage:.2f}%").format(percentage=percentage))
		output.append("-" * 60 + "\n")

		output.append(_("ANALYSIS DETAILS"))
		output.append("-" * 60)

		if self.details["pascal_case"]:
			output.append(_("\nClass names not following PascalCase:"))
			for item in self.details["pascal_case"]:
				output.append(f"  - {item}")

		if self.details["upper_snake_case"]:
			output.append(_("\nGlobal constants not following UPPER_SNAKE_CASE:"))
			for item in self.details["upper_snake_case"]:
				output.append(f"  - {item}")

		if self.details["camel_case"]:
			output.append(_("\nNames not following camelCase:"))
			for item in self.details["camel_case"]:
				output.append(f"  - {item}")

		if self.details["i18n"]:
			output.append(_("\nStrings in functions/UI without _() translation wrappers:"))
			for item in self.details["i18n"]:
				output.append(f"  - {item}")

		output.append(_("\nIndentation:"))
		for item in self.details["tabs"]:
			output.append(f"  - {item}")

		output.append(_("\nHeader:\n  - {header_detail}").format(header_detail=self.details['header']))
		output.append(_("\nEncoding:\n  - {utf8_detail}").format(utf8_detail=self.details['utf8']))

		return "\n".join(output)

	def _format_line(self, description, result):
		status = _("PASSED (+1)") if result else _("FAILED (+0)")
		return f"[{status}] {description}"


# --- NVDA Manifest Checker Class ---
class NVDAManifestChecker:
	"""Check NVDA add-on manifest.ini file structure and required keys."""

	def __init__(self, file_path):
		self.file_path = Path(file_path)
		self.issues = []
		self.info = {}

	def analyze(self):
		if not self.file_path.exists():
			return False, _("File not found: {file_path}").format(file_path=self.file_path)

		try:
			raw_content = self.file_path.read_text(encoding="utf-8-sig")
		except UnicodeDecodeError:
			try:
				raw_content = self.file_path.read_text(encoding="latin-1", errors="replace")
			except Exception as err:
				return False, _("Error reading file: {err}").format(err=err)
		except Exception as err:
			return False, _("Error opening file: {err}").format(err=err)

		self.info = {}
		current_key = None
		current_val = []
		in_multiline = False

		for line in raw_content.splitlines():
			line_str = line.strip()

			if in_multiline:
				current_val.append(line_str)
				if line_str.endswith('"""'):
					in_multiline = False
					self.info[current_key] = "\n".join(current_val)
					current_key = None
					current_val = []
				continue

			if not line_str or line_str.startswith("#") or line_str.startswith(";"):
				continue

			if "=" in line_str:
				key, val = line_str.split("=", 1)
				key = key.strip()
				val = val.strip()

				if val.startswith('"""') and not (val.endswith('"""') and len(val) > 3):
					in_multiline = True
					current_key = key
					current_val = [val]
				else:
					self.info[key] = val

		version_pattern = re.compile(r"^\d{4}\.\d+(\.\d+)?$")

		for key, description in REQUIRED_MANIFEST_KEYS.items():
			val = self.info.get(key, "").strip()
			if val.startswith('"') and val.endswith('"'):
				val = val[1:-1].strip()
			elif val.startswith('"""') and val.endswith('"""'):
				val = val[3:-3].strip()

			if not val:
				self.issues.append(
					_("Missing or empty required key: '{key}' ({description})").format(
						key=key, description=description
					)
				)

		for v_key in ("minimumNVDAVersion", "lastTestedNVDAVersion"):
			if v_key in self.info:
				val = self.info[v_key].strip().strip('"').strip("'")
				if val and not version_pattern.match(val):
					self.issues.append(
						_("Invalid format in '{key}': '{value}'. Expected YYYY.R pattern (e.g., 2023.3)").format(
							key=v_key, value=val
						)
					)

		return True, None

	def generate_report_text(self):
		output = []
		output.append("============================================================")
		output.append(_("MANIFEST VALIDATION (MANIFEST.INI)"))
		output.append("============================================================\n")
		output.append(_("Analyzed file: {file_path}\n").format(file_path=self.file_path))

		if not self.issues:
			output.append(_("STATUS: COMPLIANT - The manifest contains all required keys.\n"))
		else:
			output.append(_("STATUS: WARNING - Found {count} issue(s).\n").format(count=len(self.issues)))

		output.append(_("IDENTIFIED KEYS:"))
		output.append("-" * 60)
		for key, value in self.info.items():
			clean_val = value.replace("\n", " ")
			output.append(f"  * {key}: {clean_val}")

		if self.issues:
			output.append("\n" + "-" * 60)
			output.append(_("ISSUES FOUND"))
			output.append("-" * 60)
			for issue in self.issues:
				output.append(f"  [X] {issue}")

		return "\n".join(output)


# --- wxPython Graphical User Interface ---
class MainFrame(wx.Frame):
	"""Accessible Main Window for NVDA Style & Manifest Checker."""

	def __init__(self):
		super().__init__(
			parent=None,
			title=_("NVDA Add-on Checker - Code and Manifest Analyzer"),
			size=(760, 640),
		)

		self.init_ui()
		self.setup_shortcuts()
		self.Centre()

	def init_ui(self):
		panel = wx.Panel(self)
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		file_sizer = wx.BoxSizer(wx.HORIZONTAL)

		lbl_file = wx.StaticText(panel, wx.ID_ANY, _("File &Path (.py or manifest.ini):"))
		self.txt_file_path = wx.TextCtrl(panel, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
		btn_browse = wx.Button(panel, wx.ID_ANY, _("&Browse..."))

		file_sizer.Add(lbl_file, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		file_sizer.Add(self.txt_file_path, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		file_sizer.Add(btn_browse, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		main_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 5)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.btn_analyze = wx.Button(panel, wx.ID_ANY, _("&Analyze Code (.py)"))
		self.btn_manifest = wx.Button(panel, wx.ID_ANY, _("Validate &Manifest"))
		self.btn_copy = wx.Button(panel, wx.ID_ANY, _("&Copy Report"))
		self.btn_clear = wx.Button(panel, wx.ID_ANY, _("C&lear"))
		self.btn_exit = wx.Button(panel, wx.ID_ANY, _("E&xit"))

		btn_sizer.Add(self.btn_analyze, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_manifest, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_copy, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_clear, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_exit, 0)

		main_sizer.Add(btn_sizer, 0, wx.LEFT | wx.BOTTOM | wx.TOP, 10)

		lbl_report = wx.StaticText(panel, wx.ID_ANY, _("Analysis &Report:"))
		self.txt_report = wx.TextCtrl(
			panel,
			wx.ID_ANY,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
		)

		main_sizer.Add(lbl_report, 0, wx.LEFT | wx.TOP, 10)
		main_sizer.Add(self.txt_report, 1, wx.EXPAND | wx.ALL, 10)

		panel.SetSizer(main_sizer)

		btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
		self.btn_analyze.Bind(wx.EVT_BUTTON, self.on_analyze_code)
		self.btn_manifest.Bind(wx.EVT_BUTTON, self.on_analyze_manifest)
		self.btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_report)
		self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)
		self.btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)
		self.txt_file_path.Bind(wx.EVT_TEXT_ENTER, self.on_analyze_code)

	def setup_shortcuts(self):
		"""Define global keyboard shortcuts."""
		id_accel_analyze = wx.NewIdRef()
		id_accel_manifest = wx.NewIdRef()
		id_accel_browse = wx.NewIdRef()
		id_accel_copy = wx.NewIdRef()
		id_accel_clear = wx.NewIdRef()
		id_accel_exit = wx.NewIdRef()

		self.Bind(wx.EVT_MENU, self.on_analyze_code, id=id_accel_analyze)
		self.Bind(wx.EVT_MENU, self.on_analyze_manifest, id=id_accel_manifest)
		self.Bind(wx.EVT_MENU, self.on_browse, id=id_accel_browse)
		self.Bind(wx.EVT_MENU, self.on_copy_report, id=id_accel_copy)
		self.Bind(wx.EVT_MENU, self.on_clear, id=id_accel_clear)
		self.Bind(wx.EVT_MENU, self.on_exit, id=id_accel_exit)

		accel_table = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('O'), id_accel_browse),
			(wx.ACCEL_NORMAL, wx.WXK_F5, id_accel_analyze),
			(wx.ACCEL_ALT, ord('M'), id_accel_manifest),
			(wx.ACCEL_ALT, ord('C'), id_accel_copy),
			(wx.ACCEL_ALT, ord('L'), id_accel_clear),
			(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, id_accel_exit)
		])
		self.SetAcceleratorTable(accel_table)

	def on_browse(self, event):
		wildcard = (
			_("All supported (*.py; manifest.ini)|*.py;manifest.ini|") +
			_("Python files (*.py)|*.py|") +
			_("NVDA Manifest (manifest.ini)|manifest.ini|") +
			_("All files (*.*)|*.*")
		)
		dlg = wx.FileDialog(
			self,
			message=_("Select file to analyze"),
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
		)

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.txt_file_path.SetValue(path)
			
			if Path(path).name.lower() == "manifest.ini":
				self.btn_manifest.SetFocus()
			else:
				self.btn_analyze.SetFocus()

		dlg.Destroy()

	def on_analyze_code(self, event):
		file_path_str = self.txt_file_path.GetValue().strip()

		if not file_path_str:
			wx.MessageBox(
				_("Please select or enter the path to a .py file."),
				_("Missing Path"),
				wx.OK | wx.ICON_WARNING,
				self,
			)
			self.txt_file_path.SetFocus()
			return

		file_path = Path(file_path_str)
		if not file_path.is_file():
			wx.MessageBox(
				_("The specified file was not found:\n{file_path}").format(
					file_path=file_path_str
				),
				_("File Not Found"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
			self.txt_file_path.SetFocus()
			return

		if file_path.suffix.lower() != ".py":
			wx.MessageBox(
				_("The selected file is not a Python file (.py).\n"
				  "To analyze manifests, use the 'Validate Manifest' button."),
				_("Invalid File"),
				wx.OK | wx.ICON_WARNING,
				self,
			)
			self.txt_file_path.SetFocus()
			return

		checker = NVDAStyleChecker(file_path)
		success, error_msg = checker.analyze()

		if not success:
			self.txt_report.SetValue(
				_("FILE ANALYSIS FAILED\n\n{error_msg}").format(
					error_msg=error_msg
				)
			)
			wx.MessageBox(
				_("Syntax error found in the Python file.\n\n{error_msg}").format(
					error_msg=error_msg
				),
				_("Syntax Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
		else:
			report_text = checker.generate_report_text()
			self.txt_report.SetValue(report_text)

		self.txt_report.SetFocus()

	def on_analyze_manifest(self, event):
		file_path_str = self.txt_file_path.GetValue().strip()

		if not file_path_str:
			manifest_path = Path("manifest.ini")
		else:
			p = Path(file_path_str)
			if p.name.lower() == "manifest.ini":
				manifest_path = p
			else:
				manifest_path = p.parent / "manifest.ini"

		if not manifest_path.is_file():
			wx.MessageBox(
				_("Could not locate the 'manifest.ini' file in this folder:\n{folder}\n\n"
				  "Ensure the add-on manifest is saved in the same directory.").format(
					folder=manifest_path.parent
				),
				_("Manifest Not Found"),
				wx.OK | wx.ICON_WARNING,
				self,
			)
			self.txt_file_path.SetFocus()
			return

		checker = NVDAManifestChecker(manifest_path)
		success, error_msg = checker.analyze()

		if not success:
			self.txt_report.SetValue(
				_("MANIFEST READING FAILED\n\n{error_msg}").format(
					error_msg=error_msg
				)
			)
			wx.MessageBox(
				error_msg,
				_("Manifest Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
		else:
			report_text = checker.generate_report_text()
			self.txt_report.SetValue(report_text)

		self.txt_report.SetFocus()

	def on_copy_report(self, event):
		text = self.txt_report.GetValue()
		if not text:
			wx.MessageBox(
				_("No report available to copy."),
				_("Information"),
				wx.OK | wx.ICON_INFORMATION,
				self,
			)
			return

		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(text))
			wx.TheClipboard.Close()
			wx.MessageBox(
				_("Report copied to the clipboard successfully!"),
				_("Success"),
				wx.OK | wx.ICON_INFORMATION,
				self,
			)

	def on_clear(self, event):
		self.txt_file_path.Clear()
		self.txt_report.Clear()
		self.txt_file_path.SetFocus()

	def on_exit(self, event):
		self.Close(True)


def main():
	app = wx.App(False)
	frame = MainFrame()
	frame.Show()
	app.MainLoop()


if __name__ == "__main__":
	main()
