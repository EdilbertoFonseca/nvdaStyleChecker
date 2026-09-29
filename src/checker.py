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

NVDA Add-on Style & Manifest Checker - Python source code checker.
"""

import ast
import re
from pathlib import Path
from typing import TypedDict

from config import (
	CAMEL_CASE_PATTERN,
	IGNORED_ARGUMENTS,
	PASCAL_CASE_PATTERN,
	UPPER_SNAKE_CASE_PATTERN,
	_,
)


class CheckResults(TypedDict):
	"""Store the pass/fail status of each style check."""

	pascal_case: bool
	upper_snake_case: bool
	camel_case: bool
	tabs: bool
	header: bool
	utf8: bool
	i18n: bool


class CheckDetails(TypedDict):
	"""Store the detailed results of each style check."""

	pascal_case: list[str]
	upper_snake_case: list[str]
	camel_case: list[str]
	tabs: list[str]
	header: str
	utf8: str
	i18n: list[str]


class NVDAStyleChecker:
	"""Check Python source files against NVDA style conventions."""

	I18N_FUNCTIONS = {
		"_",
		"pgettext",
		"npgettext",
		"ngettext",
	}

	UI_FUNCTIONS = {
		"message",
		"messageBox",
		"StaticText",
		"Button",
		"CheckBox",
		"RadioButton",
		"StaticBox",
		"TextCtrl",
	}

	LOG_FUNCTIONS = {
		"debug",
		"info",
		"warning",
		"error",
		"critical",
		"exception",
	}

	def __init__(self, file_path: str | Path) -> None:
		self.file_path = Path(file_path)
		self.source = ""
		self.lines: list[str] = []
		self.tree: ast.Module | None = None

		self.results: CheckResults = {
			"pascal_case": False,
			"upper_snake_case": False,
			"camel_case": False,
			"tabs": False,
			"header": False,
			"utf8": False,
			"i18n": False,
		}

		self.details: CheckDetails = {
			"pascal_case": [],
			"upper_snake_case": [],
			"camel_case": [],
			"tabs": [],
			"header": "",
			"utf8": "",
			"i18n": [],
		}

	def read_file(self) -> None:
		"""Read the source file using UTF-8, with a Latin-1 fallback."""
		try:
			self.source = self.file_path.read_text(encoding="utf-8")
		except UnicodeDecodeError:
			self.source = self.file_path.read_text(
				encoding="latin-1",
				errors="replace",
			)

		self.lines = self.source.splitlines()

	def parse_file(self) -> tuple[bool, str | None]:
		"""Parse the source code into an abstract syntax tree."""
		try:
			self.tree = ast.parse(
				self.source,
				filename=str(self.file_path),
			)
			return True, None
		except SyntaxError as error:
			error_line = error.lineno or 0
			err_msg = _("Syntax error at line {line_no}: {error_msg}").format(
				line_no=error_line,
				error_msg=error.msg,
			)
			return False, err_msg

	def check_pascal_case(self) -> None:
		"""Check class names against the PascalCase naming convention."""
		if self.tree is None:
			return

		invalid_names: set[str] = set()

		for node in ast.walk(self.tree):
			if isinstance(node, ast.ClassDef) and not PASCAL_CASE_PATTERN.fullmatch(node.name):
				invalid_names.add(
					_("line {line_no}: class '{name}'").format(
						line_no=node.lineno,
						name=node.name,
					),
				)

		sorted_details = sorted(invalid_names)
		self.details["pascal_case"] = sorted_details
		self.results["pascal_case"] = not sorted_details

	def check_upper_snake_case(self) -> None:
		"""Check module-level constants against UPPER_SNAKE_CASE."""
		if self.tree is None:
			return

		invalid_names: set[str] = set()

		for node in self.tree.body:
			if not isinstance(node, (ast.Assign, ast.AnnAssign)):
				continue

			targets = node.targets if isinstance(node, ast.Assign) else [node.target]

			for target in targets:
				if not isinstance(target, ast.Name):
					continue

				var_name = target.id

				if var_name.startswith("__") and var_name.endswith("__"):
					continue

				if var_name.startswith("_"):
					continue

				if not UPPER_SNAKE_CASE_PATTERN.fullmatch(var_name):
					invalid_names.add(
						_("line {line_no}: global constant '{name}'").format(
							line_no=node.lineno,
							name=var_name,
						),
					)

		sorted_details = sorted(invalid_names)
		self.details["upper_snake_case"] = sorted_details
		self.results["upper_snake_case"] = not sorted_details

	def check_camel_case(self) -> None:
		"""Check functions, arguments, and local variables against camelCase."""
		if self.tree is None:
			return

		invalid_names: set[str] = set()

		for node in ast.walk(self.tree):
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				self._check_camel_case_function(node, invalid_names)
			elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
				self._check_camel_case_variable(node, invalid_names, self.tree)

		sorted_details = sorted(invalid_names)
		self.details["camel_case"] = sorted_details
		self.results["camel_case"] = not sorted_details

	def _check_camel_case_function(
		self,
		node: ast.FunctionDef | ast.AsyncFunctionDef,
		invalid_names: set[str],
	) -> None:
		"""Check a function name and its positional arguments."""
		name = node.name

		# Ignore dunder methods (e.g. __init__) and the translation function _().
		if (name.startswith("__") and name.endswith("__")) or name == "_":
			return

		check_name = self._normalize_function_name(name)

		if not check_name:
			return

		if not CAMEL_CASE_PATTERN.fullmatch(check_name):
			invalid_names.add(
				_("line {line_no}: function '{name}'").format(
					line_no=node.lineno,
					name=name,
				),
			)

		for arg in node.args.args:
			self._check_camel_case_argument(arg, invalid_names)

	def _check_camel_case_argument(
		self,
		arg: ast.arg,
		invalid_names: set[str],
	) -> None:
		"""Check a function argument name against camelCase."""
		arg_name = arg.arg

		if arg_name in IGNORED_ARGUMENTS or arg_name == "_":
			return

		check_arg = self._remove_leading_underscores(arg_name)

		if not check_arg:
			return

		if not CAMEL_CASE_PATTERN.fullmatch(check_arg):
			invalid_names.add(
				_("line {line_no}: argument '{name}'").format(
					line_no=arg.lineno,
					name=arg_name,
				),
			)

	def _check_camel_case_variable(
		self,
		node: ast.Name,
		invalid_names: set[str],
		tree: ast.Module,
	) -> None:
		"""Check a local variable name against camelCase."""
		# Exclude the exact Name nodes belonging to module-level assignments.
		for statement in tree.body:
			if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
				continue

			targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]

			for target in targets:
				if any(candidate is node for candidate in ast.walk(target)):
					return

		name = node.id

		if name == "_" or name.isupper() or name in IGNORED_ARGUMENTS:
			return

		check_var = self._remove_leading_underscores(name)

		if not check_var:
			return

		if not CAMEL_CASE_PATTERN.fullmatch(check_var):
			invalid_names.add(
				_("line {line_no}: variable '{name}'").format(
					line_no=node.lineno,
					name=name,
				),
			)

	def _normalize_function_name(self, name: str) -> str:
		"""Remove NVDA event/script prefixes before validating a function name."""
		if name.startswith("script_"):
			name = name[7:]
		elif name.startswith("_script_"):
			name = name[8:]
		elif name.startswith("event_"):
			name = name[6:]
		elif name.startswith("_event_"):
			name = name[7:]

		return self._remove_leading_underscores(name)

	def _remove_leading_underscores(self, name: str) -> str:
		"""Remove leading underscores from a name."""
		while name.startswith("_"):
			name = name[1:]

		return name

	def check_tabs(self) -> None:
		"""Check whether indentation uses tabs instead of spaces."""
		indentation_found = False
		invalid_lines: list[int] = []

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
					line_no=line_no,
				)
				for line_no in invalid_lines
			]
		elif indentation_found:
			self.details["tabs"] = [_("All indented lines use tabs.")]
		else:
			self.details["tabs"] = [_("The file has no indented lines.")]

	def check_header(self) -> None:
		"""Check whether a standard NVDA add-on header is present."""
		if not self.lines:
			self.results["header"] = False
			self.details["header"] = _("Empty file.")
			return

		header_lines: list[str] = []

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
			_("Header identified.") if header_lines else _("No standard header identified.")
		)

	def check_utf8(self) -> None:
		"""Check whether a UTF-8 encoding declaration is present."""
		encoding_pattern = re.compile(r"coding[=:]\s*([-\w.]+)", re.IGNORECASE)
		encoding: str | None = None

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

	def _get_call_function_name(self, node: ast.Call) -> str:
		"""Return the function name from a call node."""
		if isinstance(node.func, ast.Name):
			return node.func.id

		if isinstance(node.func, ast.Attribute):
			return node.func.attr

		return ""

	def _is_translation_call(self, node: ast.expr) -> bool:
		"""Return whether an expression is already wrapped for translation."""
		if not isinstance(node, ast.Call):
			return False

		if isinstance(node.func, ast.Name):
			return node.func.id in self.I18N_FUNCTIONS

		if isinstance(node.func, ast.Attribute):
			return node.func.attr in self.I18N_FUNCTIONS

		return False

	def _add_untranslated_string(
		self,
		node: ast.Constant,
		argument_name: str | None = None,
	) -> None:
		"""Add an untranslated string to the i18n report."""
		if not isinstance(node.value, str):
			return

		value = node.value.strip()

		if len(value) <= 1 or value.startswith(("http://", "https://")) or " " not in value:
			return

		if argument_name:
			self.details["i18n"].append(
				_('line {line_no}: {arg}="{value}..."').format(
					line_no=node.lineno,
					arg=argument_name,
					value=value[:30],
				),
			)
		else:
			self.details["i18n"].append(
				_('line {line_no}: "{value}..."').format(
					line_no=node.lineno,
					value=value[:30],
				),
			)

	def _check_i18n_call(self, node: ast.Call) -> None:
		"""Check a function call for untranslated UI strings."""
		func_name = self._get_call_function_name(node)

		if func_name in self.I18N_FUNCTIONS:
			return

		if func_name in self.LOG_FUNCTIONS:
			return

		if func_name not in self.UI_FUNCTIONS:
			return

		for arg in node.args:
			if self._is_translation_call(arg):
				continue

			if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
				self._add_untranslated_string(arg)

		for keyword in node.keywords:
			if self._is_translation_call(keyword.value):
				continue

			if isinstance(keyword.value, ast.Constant) and isinstance(
				keyword.value,
				str,
			):
				self._add_untranslated_string(keyword.value, keyword.arg)

	def check_i18n(self) -> None:
		"""Check for UI and message strings missing _() translation wrappers."""
		if self.tree is None:
			return

		self.details["i18n"] = []

		for node in ast.walk(self.tree):
			if isinstance(node, ast.Call):
				self._check_i18n_call(node)

		self.details["i18n"] = sorted(set(self.details["i18n"]))
		self.results["i18n"] = not self.details["i18n"]

	def analyze(self) -> tuple[bool, str | None]:
		"""Run all Python style checks."""
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

	def generate_report_text(self) -> str:
		"""Generate the complete text report for the analysis."""
		points = sum(1 for result in self.results.values() if result)
		total = len(self.results)
		percentage = (points / total) * 100

		output: list[str] = []

		output.append("============================================================")
		output.append(_("STYLE ANALYSIS - PYTHON FILE (.PY)"))
		output.append("============================================================\n")
		output.append(
			_("Analyzed file: {file_path}\n").format(
				file_path=self.file_path,
			),
		)

		output.append(
			self._format_line(
				_("Classes in PascalCase"),
				self.results["pascal_case"],
			),
		)
		output.append(
			self._format_line(
				_("Global constants in UPPER_SNAKE_CASE"),
				self.results["upper_snake_case"],
			),
		)
		output.append(
			self._format_line(
				_("Functions and variables in camelCase"),
				self.results["camel_case"],
			),
		)
		output.append(
			self._format_line(
				_("Indentation using tabs"),
				self.results["tabs"],
			),
		)
		output.append(
			self._format_line(
				_("Presence of standard header"),
				self.results["header"],
			),
		)
		output.append(
			self._format_line(
				_("UTF-8 encoding declaration"),
				self.results["utf8"],
			),
		)
		output.append(
			self._format_line(
				_("Strings marked for translation _()"),
				self.results["i18n"],
			),
		)

		output.append("\n" + "-" * 60)
		output.append(
			_("Score: {points}/{total} points").format(
				points=points,
				total=total,
			),
		)
		output.append(
			_("Compliance: {percentage:.2f}%").format(
				percentage=percentage,
			),
		)
		output.append("-" * 60 + "\n")

		output.append(_("ANALYSIS DETAILS"))
		output.append("-" * 60)

		if self.details["pascal_case"]:
			output.append(_("\\nClass names not following PascalCase:"))
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

		output.append(
			_("\nHeader:\n  - {header_detail}").format(
				header_detail=self.details["header"],
			),
		)
		output.append(
			_("\nEncoding:\n  - {utf8_detail}").format(
				utf8_detail=self.details["utf8"],
			),
		)

		return "\n".join(output)

	def _format_line(self, description: str, result: bool) -> str:
		"""Format a report line with its pass/fail status."""
		status = _("PASSED (+1)") if result else _("FAILED (+0)")
		return f"[{status}] {description}"
