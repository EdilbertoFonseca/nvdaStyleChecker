# appTemplate

A reusable template for creating Python desktop applications with wxPython.

The project provides a basic application structure with localization support,
centralized project information, and PyInstaller integration.

## Features

- Python desktop application based on wxPython.
- Reusable project structure.
- Centralized application information in `buildVars.py`.
- gettext-based localization.
- Poedit support using a standardized `main.po` file.
- PyInstaller configuration.
- Automatic Windows executable version information.
- Custom PyInstaller hooks support.
- Ready-to-use project structure for new applications.

## Project Structure

```text
appTemplate/
│
├── buildVars.py
│
├── hooks/
│
├── install/
│   └── pyinstaller/
│       ├── appTemplate.spec
│       └── mondrian.ico
│
└── src/
    ├── main.py
    │
    └── locale/
        └── main.po
```

## Requirements

- Python 3.x
- wxPython
- PyInstaller
- Poedit (optional, for translations)

## Application Information

Project information is centralized in buildVars.py.

app_info = {
	"app_name": "appTemplate",
	"app_summary": "Application template",
	"app_description": "A template for creating Python desktop applications.",
	"app_version": "1.1.0",
	"app_author": "Edilberto Fonseca <edilberto.fonseca@outlook.com>",
	"spec_file": "install/pyinstaller/appTemplate.spec",
	"script_name": "src/main.py",
}

This information is used by different parts of the project.

For example:

- app_name defines the application name.
- app_version defines the application version.
- app_author provides the application author information.
- app_description provides the Windows file description.
- app_summary provides additional application information.
- script_name identifies the application's main script.

Centralizing this information makes it possible to create new projects
without changing project-specific information throughout the source code.

## Running the Application

From the project root, run:

```python
python src/main.py
```

The application will start using the configuration defined in
buildVars.py.

## Localization

The project uses Python's gettext module for localization.
The translation file uses the standardized filename:

```git
src/locale/main.po
```

Using a generic main.po filename makes the template reusable across
different projects.

Translatable strings are marked in the Python source code using the _()
function.

For example:

```Python
_('Welcome to the application.')
_('File')
_('Exit')
_('Ready.')
```

## Poedit

Poedit can be used to scan the Python source code and find translatable
strings.

The translation file is always named:
```git
main.po
```

This allows the same template structure to be reused in different
applications without renaming the translation file.
When creating a new project, configure Poedit to scan the application's
source files and update main.po with the strings found in the code.
Building with PyInstaller

The PyInstaller specification file is located at:

```python
pyinstaller install/pyinstaller/appTemplate.spec
```

The build process generates the executable using the information defined
in buildVars.py.

## Windows Version Information

During the build process, the specification file automatically generates:
```txt
build/version_info.txt
```

The generated version information includes:

- Company name.
- File description.
- File version.
- Internal name.
- Original filename.
- Product name.
- Product version.
- Comments.

The version defined in buildVars.py is converted to the four-component
numeric format required by Windows.

For example:

```python
1.1.0
```

is converted to:

```python
1,1,0,0
```

The original version string remains available in the Windows file and
product version fields.

## Custom PyInstaller Hooks

Custom PyInstaller hooks can be placed in:

```python
hooks/
```

The specification file automatically adds this directory to the
PyInstaller hook search path.
This allows projects created from the template to provide custom hooks
when required by third-party libraries.
  
## Creating a New Project

To create a new application from this template:

1. Copy or clone the repository.
2. Rename the project repository.
3. Update the information in buildVars.py.
4. Modify src/main.py according to the new application.
5. Use Poedit to extract and translate the application strings.
6. Keep the translation file as src/locale/main.po.
7. Replace the application icon in install/pyinstaller/ if necessary.
8. Build the application using the PyInstaller specification file.
Whenever possible, keep project-specific configuration centralized in
buildVars.py.

## License

This project is licensed under the GNU General Public License.
See the COPYING file for more information.

## Author

Edilberto Fonseca
Email: <edilberto.fonseca@outlook.com>

## AI Disclosure

This project utilizes AI for code refactoring and logic suggestions.
All AI-generated code was manually reviewed and tested by the author.
