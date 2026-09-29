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

from pathlib import Path
from typing import cast, Any

import wx

from checker import NVDAStyleChecker
from config import _
from manifestChecker import NVDAManifestChecker


class MainFrame(wx.Frame):
	"""Accessible main window for NVDA Style & Manifest Checker."""

	def __init__(self) -> None:
		super().__init__(
			parent=None,
			title=_("NVDA Add-on Checker - Code and Manifest Analyzer"),
			size=wx.Size(760, 640),
		)

		self.init_ui()
		self.setup_shortcuts()
		self.Centre()

	def init_ui(self) -> None:
		"""Initialize the graphical user interface."""
		panel = wx.Panel(self)
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		file_sizer = wx.BoxSizer(wx.HORIZONTAL)

		lbl_file = wx.StaticText(
			panel,
			wx.ID_ANY,
			_("File &Path (.py or manifest.ini):"),
		)
		self.txt_file_path = wx.TextCtrl(
			panel,
			wx.ID_ANY,
			"",
			style=wx.TE_PROCESS_ENTER,
		)
		btn_browse = wx.Button(
			panel,
			wx.ID_ANY,
			_("&Browse..."),
		)

		file_sizer.Add(
			lbl_file,
			0,
			wx.ALIGN_CENTER_VERTICAL | wx.ALL,
			5,
		)
		file_sizer.Add(
			self.txt_file_path,
			1,
			wx.ALIGN_CENTER_VERTICAL | wx.ALL,
			5,
		)
		file_sizer.Add(
			btn_browse,
			0,
			wx.ALIGN_CENTER_VERTICAL | wx.ALL,
			5,
		)

		main_sizer.Add(
			file_sizer,
			0,
			wx.EXPAND | wx.ALL,
			5,
		)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.btn_analyze = wx.Button(
			panel,
			wx.ID_ANY,
			_("&Analyze Code (.py)"),
		)
		self.btn_manifest = wx.Button(
			panel,
			wx.ID_ANY,
			_("Validate &Manifest"),
		)
		self.btn_copy = wx.Button(
			panel,
			wx.ID_ANY,
			_("&Copy Report"),
		)
		self.btn_clear = wx.Button(
			panel,
			wx.ID_ANY,
			_("C&lear"),
		)
		self.btn_exit = wx.Button(
			panel,
			wx.ID_ANY,
			_("E&xit"),
		)

		btn_sizer.Add(self.btn_analyze, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_manifest, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_copy, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_clear, 0, wx.RIGHT, 5)
		btn_sizer.Add(self.btn_exit, 0)

		main_sizer.Add(
			btn_sizer,
			0,
			wx.LEFT | wx.BOTTOM | wx.TOP,
			10,
		)

		lbl_report = wx.StaticText(
			panel,
			wx.ID_ANY,
			_("Analysis &Report:"),
		)
		self.txt_report = wx.TextCtrl(
			panel,
			wx.ID_ANY,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
		)

		main_sizer.Add(
			lbl_report,
			0,
			wx.LEFT | wx.TOP,
			10,
		)
		main_sizer.Add(
			self.txt_report,
			1,
			wx.EXPAND | wx.ALL,
			10,
		)

		panel.SetSizer(main_sizer)

		btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
		self.btn_analyze.Bind(wx.EVT_BUTTON, self.on_analyze_code)
		self.btn_manifest.Bind(wx.EVT_BUTTON, self.on_analyze_manifest)
		self.btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_report)
		self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)
		self.btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)
		self.txt_file_path.Bind(wx.EVT_TEXT_ENTER, self.on_analyze_code)

	def setup_shortcuts(self) -> None:
		"""Define global keyboard shortcuts."""
		id_accel_analyze: int = cast(int, wx.NewIdRef())
		id_accel_manifest: int = cast(int, wx.NewIdRef())
		id_accel_browse: int = cast(int, wx.NewIdRef())
		id_accel_copy: int = cast(int, wx.NewIdRef())
		id_accel_clear: int = cast(int, wx.NewIdRef())
		id_accel_exit: int = cast(int, wx.NewIdRef())

		self.Bind(
			wx.EVT_MENU,
			self.on_analyze_code,
			id=id_accel_analyze,
		)
		self.Bind(
			wx.EVT_MENU,
			self.on_analyze_manifest,
			id=id_accel_manifest,
		)
		self.Bind(
			wx.EVT_MENU,
			self.on_browse,
			id=id_accel_browse,
		)
		self.Bind(
			wx.EVT_MENU,
			self.on_copy_report,
			id=id_accel_copy,
		)
		self.Bind(
			wx.EVT_MENU,
			self.on_clear,
			id=id_accel_clear,
		)
		self.Bind(
			wx.EVT_MENU,
			self.on_exit,
			id=id_accel_exit,
		)

		accel_table = wx.AcceleratorTable(
			[
				(wx.ACCEL_CTRL, ord("O"), id_accel_browse),
				(wx.ACCEL_NORMAL, wx.WXK_F5, id_accel_analyze),
				(wx.ACCEL_ALT, ord("M"), id_accel_manifest),
				(wx.ACCEL_ALT, ord("C"), id_accel_copy),
				(wx.ACCEL_ALT, ord("L"), id_accel_clear),
				(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, id_accel_exit),
			],
		)
		self.SetAcceleratorTable(accel_table)

	def on_browse(self, event: Any) -> None:
		"""Open a file dialog and select a file to analyze."""
		wildcard = (
			_("All supported (*.py; manifest.ini)|*.py;manifest.ini|")
			+ _("Python files (*.py)|*.py|")
			+ _("NVDA Manifest (manifest.ini)|manifest.ini|")
			+ _("All files (*.*)|*.*")
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

	def on_analyze_code(self, event: Any) -> None:
		"""Analyze the selected Python file."""
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
					file_path=file_path_str,
				),
				_("File Not Found"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
			self.txt_file_path.SetFocus()
			return

		if file_path.suffix.lower() != ".py":
			wx.MessageBox(
				_(
					"The selected file is not a Python file (.py).\n"
					"To analyze manifests, use the 'Validate Manifest' button.",
				),
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
					error_msg=error_msg,
				),
			)
			wx.MessageBox(
				_("Syntax error found in the Python file.\n\n{error_msg}").format(
					error_msg=error_msg,
				),
				_("Syntax Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
		else:
			report_text = checker.generate_report_text()
			self.txt_report.SetValue(report_text)

		self.txt_report.SetFocus()

	def on_analyze_manifest(self, event: Any) -> None:
		"""Analyze the manifest.ini file associated with the selected path."""
		file_path_str = self.txt_file_path.GetValue().strip()

		if not file_path_str:
			manifest_path = Path("manifest.ini")
		else:
			path = Path(file_path_str)

			if path.name.lower() == "manifest.ini":
				manifest_path = path
			else:
				manifest_path = path.parent / "manifest.ini"

		if not manifest_path.is_file():
			wx.MessageBox(
				_(
					"Could not locate the 'manifest.ini' file in this folder:\n"
					"{folder}\n\n"
					"Ensure the add-on manifest is saved in the same directory.",
				).format(
					folder=manifest_path.parent,
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
					error_msg=error_msg,
				),
			)
			wx.MessageBox(
				error_msg or _("Unknown manifest error."),
				_("Manifest Error"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
		else:
			report_text = checker.generate_report_text()
			self.txt_report.SetValue(report_text)

		self.txt_report.SetFocus()

	def on_copy_report(self, event: Any) -> None:
		"""Copy the current report to the system clipboard."""
		text = self.txt_report.GetValue()

		if not text:
			wx.MessageBox(
				_("No report available to copy."),
				_("Information"),
				wx.OK | wx.ICON_INFORMATION,
				self,
			)
			return

		clipboard = wx.TheClipboard

		if clipboard.Open():
			clipboard.SetData(wx.TextDataObject(text))
			clipboard.Close()
			wx.MessageBox(
				_("Report copied to the clipboard successfully!"),
				_("Success"),
				wx.OK | wx.ICON_INFORMATION,
				self,
			)

	def on_clear(self, event: Any) -> None:
		"""Clear the selected file path and analysis report."""
		self.txt_file_path.Clear()
		self.txt_report.Clear()
		self.txt_file_path.SetFocus()

	def on_exit(self, event: Any) -> None:
		"""Close the application."""
		self.Close(True)
