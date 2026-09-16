# -*- mode: python -*-

import os
import sys


# --- 1. CONFIGURAÇÃO DE CAMINHOS ---

current_spec_dir = os.path.dirname(os.path.abspath(SPEC))
REPO_DIR = os.path.abspath(os.path.join(current_spec_dir, '..', '..'))

# Importa as informações do projeto
sys.path.insert(0, REPO_DIR)
from buildVars import app_info

path_to_src = os.path.join(REPO_DIR, 'src')
script_main = os.path.join(REPO_DIR, app_info["script_name"])

# Onde os nossos hooks customizados vão morar
hooks_path = os.path.join(REPO_DIR, 'hooks')


# --- 2. CONFIGURAÇÕES DE COMPILAÇÃO ---

NAME_EXE = f'{app_info["app_name"]}.exe'
BUILD_TARGET = os.path.join(REPO_DIR, 'build')
DIST_TARGET = os.path.join(REPO_DIR, 'dist')


# --- 3. INFORMAÇÕES DE VERSÃO DO WINDOWS ---

def create_version_file():
	"""Create the Windows version information file."""

	version = app_info["app_version"]

	# Windows requires a four-part numeric version.
	version_parts = version.split('.')
	while len(version_parts) < 4:
		version_parts.append('0')

	file_version = ','.join(version_parts[:4])

	version_file = os.path.join(
		BUILD_TARGET,
		'version_info.txt',
	)

	os.makedirs(BUILD_TARGET, exist_ok=True)

	version_info = f'''# UTF-8

VSVersionInfo(
	ffi=FixedFileInfo(
		filevers=({file_version}),
		prodvers=({file_version}),
		mask=0x3f,
		flags=0x0,
		OS=0x40004,
		fileType=0x1,
		subtype=0x0,
		date=(0, 0)
	),
	kids=[
		StringFileInfo(
			[
				StringTable(
					'040904B0',
					[
						StringStruct(
							'CompanyName',
							'{app_info["app_author"]}'
						),
						StringStruct(
							'FileDescription',
							'{app_info["app_description"]}'
						),
						StringStruct(
							'FileVersion',
							'{version}'
						),
						StringStruct(
							'InternalName',
							'{app_info["app_name"]}.exe'
						),
						StringStruct(
							'OriginalFilename',
							'{app_info["app_name"]}.exe'
						),
						StringStruct(
							'ProductName',
							'{app_info["app_name"]}'
						),
						StringStruct(
							'ProductVersion',
							'{version}'
						),
						StringStruct(
							'Comments',
							'{app_info["app_summary"]}'
						)
					]
				)
			]
		),
		VarFileInfo(
			[
				VarStruct(
					'Translation',
					[1033, 1200]
				)
			]
		)
	]
)
'''

	with open(version_file, 'w', encoding='utf-8') as file:
		file.write(version_info)

	return version_file


version_file = create_version_file()


# --- 4. ANÁLISE ---

a = Analysis(
	[script_main],
	pathex=[path_to_src],
	binaries=[],
	datas=[
		(os.path.join(path_to_src, 'locale'), 'locale')
	],
	hiddenimports=[
		'wx.combo',
		'wx.gizmos',
		'wx.lib.platebtn',
		'wx.lib.agw.aui',
		'wx.lib.agw.buttonpanel'
	],
	hookspath=[hooks_path],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=None,
	noarchive=False,
)


pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=None,
)


# --- 5. EXECUTÁVEL ---

exe = EXE(
	pyz,
	a.scripts,
	[],
	exclude_binaries=True,
	name=os.path.join(BUILD_TARGET, NAME_EXE),
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False,
	windowed=True,
	icon=os.path.join(current_spec_dir, 'mondrian.ico'),
	version=version_file,
)


# --- 6. COLETA ---

coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name=os.path.join(DIST_TARGET, app_info["app_name"]),
)
