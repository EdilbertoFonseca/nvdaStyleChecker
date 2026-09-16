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

Created on: 14/09/2026
"""

import gettext
import os
import sys

import wx

sys.path.insert(
	0,
	os.path.abspath(
		os.path.join(
			os.path.dirname(__file__),
			'..',
		)
	),
)

from buildVars import app_info

# ----------------------------------------------------------------------
# Localization
# ----------------------------------------------------------------------

def setup_locale():
	"""Initialize application localization."""

	locale_dir = os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		'locale',
	)

	translation = gettext.translation(
		'main',
		localedir=locale_dir,
		languages=["pt_BR"], 
		fallback=False,
	)

	translation.install()

	return translation.gettext


_ = setup_locale()


# ----------------------------------------------------------------------
# Main window
# ----------------------------------------------------------------------

class MainFrame(wx.Frame):
	"""Main application window."""

	def __init__(self):
		super().__init__(
			parent=None,
			title=_(f"{app_info["app_summary"]}"),
			size=(800, 600),
		)

		self._create_controls()
		self._create_menu()
		self._create_status_bar()

		self.Centre()


	def _create_controls(self):
		"""Create the main window controls."""

		panel = wx.Panel(self)

		sizer = wx.BoxSizer(wx.VERTICAL)

		label = wx.StaticText(
			panel,
			label=_('Welcome to the application.'),
		)

		sizer.Add(
			label,
			0,
			wx.ALL,
			20,
		)

		panel.SetSizer(sizer)


	def _create_menu(self):
		"""Create the application menu."""

		menu_bar = wx.MenuBar()

		file_menu = wx.Menu()

		exit_item = file_menu.Append(
			wx.ID_EXIT,
			_('Exit'),
		)

		self.Bind(
			wx.EVT_MENU,
			self._on_exit,
			exit_item,
		)

		menu_bar.Append(
			file_menu,
			_('File'),
		)

		self.SetMenuBar(menu_bar)


	def _create_status_bar(self):
		"""Create the application status bar."""

		self.CreateStatusBar()
		self.SetStatusText(_('Ready.'))


	def _on_exit(self, event):
		"""Close the application."""

		self.Close()


# ----------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------

class Application(wx.App):
	"""Main wxPython application."""

	def OnInit(self):
		"""Initialize the application."""

		frame = MainFrame()
		frame.Show()

		return True


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main():
	"""Start the application."""

	app = Application()
	app.MainLoop()


if __name__ == '__main__':
	main()
