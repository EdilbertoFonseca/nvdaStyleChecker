# hooks/hook-polib.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Isso garante que TODOS os sub-módulos sejam encontrados
hiddenimports = collect_submodules('polib')

# Isso garante que arquivos de dados (metadados) do polibsejam incluídos
datas = collect_data_files('polib')
