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

NVDA Add-on Manifest Checker.
Validates the structure and required keys of manifest.ini files.
"""

import re
from pathlib import Path
from typing import TypedDict, cast

from config import REQUIRED_MANIFEST_KEYS, _


class ManifestInfo(TypedDict, total=False):
	name: str
	summary: str
	version: str
	description: str
	author: str
	minimumNVDAVersion: str
	lastTestedNVDAVersion: str


class NVDAManifestChecker:
	"""Check NVDA add-on manifest.ini file structure and required keys."""

	def __init__(self, file_path: str | Path) -> None:
		self.file_path = Path(file_path)
		self.issues: list[str] = []
		self.info: ManifestInfo = {}

	def analyze(self) -> tuple[bool, str | None]:
		"""Analyze the manifest file and validate its required fields."""
		self.issues = []
		self.info = {}

		if not self.file_path.exists():
			return False, _("File not found: {file_path}").format(
				file_path=self.file_path,
			)

		raw_content, error_msg = self._read_manifest_file()
		if error_msg:
			return False, error_msg

		info = cast(dict[str, str], self.info)

		self._parse_manifest_content(raw_content, info)
		self._validate_required_keys(info)
		self._validate_version_keys(info)

		return True, None

	def _read_manifest_file(self) -> tuple[str, str | None]:
		"""Read the manifest file using UTF-8 with a Latin-1 fallback."""
		try:
			raw_content = self.file_path.read_text(encoding="utf-8-sig")
		except UnicodeDecodeError:
			try:
				raw_content = self.file_path.read_text(
					encoding="latin-1",
					errors="replace",
				)
			except Exception as err:
				return "", _("Error reading file: {err}").format(err=err)
		except Exception as err:
			return "", _("Error opening file: {err}").format(err=err)

		return raw_content, None

	def _parse_manifest_content(
		self,
		raw_content: str,
		info: dict[str, str],
	) -> None:
		"""Parse manifest key-value pairs, including multiline values."""
		current_key: str | None = None
		current_val: list[str] = []
		in_multiline = False

		for line in raw_content.splitlines():
			line_str = line.strip()

			if in_multiline:
				if line_str.endswith('"""'):
					content = line_str[:-3].rstrip()
					if content:
						current_val.append(content)

					if current_key is not None:
						info[current_key] = "\n".join(current_val).strip()

					current_key = None
					current_val = []
					in_multiline = False
				else:
					current_val.append(line_str)

				continue

			if not line_str or line_str.startswith("#") or line_str.startswith(";"):
				continue

			if "=" not in line_str:
				continue

			key, val = line_str.split("=", 1)
			key = key.strip()
			val = val.strip()

			if not key:
				continue

			if val.startswith('"""'):
				if val.endswith('"""') and len(val) > 6:
					info[key] = val[3:-3].strip()
				else:
					in_multiline = True
					current_key = key
					current_val = [val[3:].lstrip()]
			else:
				info[key] = val

	def _validate_required_keys(self, info: dict[str, str]) -> None:
		"""Validate that all required manifest keys are present and non-empty."""
		for key, description in REQUIRED_MANIFEST_KEYS.items():
			val = info.get(key, "").strip()

			if val.startswith('"""') and val.endswith('"""'):
				val = val[3:-3].strip()
			elif val.startswith('"') and val.endswith('"'):
				val = val[1:-1].strip()
			elif val.startswith("'") and val.endswith("'"):
				val = val[1:-1].strip()

			if not val:
				self.issues.append(
					_("Missing or empty required key: '{key}' ({description})").format(
						key=key,
						description=description,
					),
				)

	def _validate_version_keys(self, info: dict[str, str]) -> None:
		"""Validate the format of the NVDA version fields."""
		version_pattern = re.compile(r"^\d{4}\.\d+(\.\d+)?$")

		for key in ("minimumNVDAVersion", "lastTestedNVDAVersion"):
			if key not in info:
				continue

			val = info[key].strip().strip('"').strip("'")

			if val and not version_pattern.match(val):
				self.issues.append(
					_(
						"Invalid format in '{key}': '{value}'. Expected YYYY.R pattern (e.g., 2023.3)",
					).format(
						key=key,
						value=val,
					),
				)

	def generate_report_text(self) -> str:
		"""Generate a human-readable manifest validation report."""
		info = cast(dict[str, str], self.info)
		output: list[str] = []

		output.append("============================================================")
		output.append(_("MANIFEST VALIDATION (MANIFEST.INI)"))
		output.append("============================================================\n")
		output.append(
			_("Analyzed file: {file_path}\n").format(
				file_path=self.file_path,
			),
		)

		if not self.issues:
			output.append(
				_("STATUS: COMPLIANT - The manifest contains all required keys.\n"),
			)
		else:
			output.append(
				_("STATUS: WARNING - Found {count} issue(s).\n").format(
					count=len(self.issues),
				),
			)

		output.append(_("IDENTIFIED KEYS:"))
		output.append("-" * 60)

		for key, value in info.items():
			clean_val = value.replace("\n", " ")
			output.append(f"  * {key}: {clean_val}")

		if self.issues:
			output.append("\n" + "-" * 60)
			output.append(_("ISSUES FOUND"))
			output.append("-" * 60)

			for issue in self.issues:
				output.append(f"  [X] {issue}")

		return "\n".join(output)
