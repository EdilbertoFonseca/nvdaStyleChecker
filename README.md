# Executive Summary & Technical Report: NVDA Style & Manifest Checker

**Project:** NVDA Add-on Style & Manifest Checker (GUI)  
**Lead Developer:** Edilberto Fonseca  
**Version:** 1.0 (Production Release Candidate)  
**Target Environment:** Microsoft Windows / NVDA Screen Reader Ecosystem  

---

## 1. Project Overview

The **NVDA Style & Manifest Checker** is an accessible graphical tool developed with `wxPython`. It automates the static analysis of Python source code and `manifest.ini` configuration files for NVDA add-on development, ensuring adherence to the strict coding guidelines established by the NVDA open-source community.

---

## 2. Completed Milestones & Accomplishments

### A. Core Architecture & Static Analysis Engine

* **AST-Based Code Analysis (`NVDAStyleChecker`):**
  * Integrated Python’s Abstract Syntax Tree (`ast`) module to parse `.py` files without code execution.
  * Implemented pattern validation using regular expressions:
    * **Classes:** Checked for `PascalCase`.
    * **Global Constants:** Checked for `UPPER_SNAKE_CASE` at module level (`self.tree.body`).
    * **Functions & Variables:** Checked for standard `camelCase` (including `script_` and `event_` prefix rules).
    * **Indentation & Encoding:** Enforced hard tabs (no spaces) and UTF-8 header declarations.
* **Manifest Validation (`NVDAManifestChecker`):**
  * Parsed and validated required keys in `manifest.ini` (`name`, `summary`, `version`, `description`, `author`, `minimumNVDAVersion`, `lastTestedNVDAVersion`).
  * Enforced versioning format compliance (e.g., `YYYY.R`).

### B. Project Internationalization (i18n)

* **Codebase Refactoring to English:**
  * Converted all source code elements (comments, docstrings, internal variable names, class structures, and technical terminology) to idiomatic English.
* **Gettext Infrastructure Setup:**
  * Wrapped all user-facing strings, button labels, report outputs, and dialog messages in `_()` translation functions.
  * Established a robust fallback mechanism (`def _(message): return message`) to handle uninitialized translation domains gracefully.

### C. Build Pipeline & Resource Packaging

* **PyInstaller & SCons Integration:**
  * Configured build scripts for executable generation (`.exe`).
  * Resolved internal directory structure constraints (`_internal` / `internal` pathing introduced in modern PyInstaller versions).
  * Automated dynamic path resolution via `sys._MEIPASS` to ensure compiled runtime location mapping for the `locale/` directory.
* **Multi-language Locale Structure:**
  * Standardized translation catalog hierarchy:

    locale/
    └── <language_code>/
        └── LC_MESSAGES/
            ├── nvdaStyleChecker.po
            └── nvdaStyleChecker.mo
                ```
  * Configured native OS fallback to default English when a system language catalog is absent.

---

## 3. Technical Architecture & File Map

| Component / File | Purpose | Key Responsibilities |
| :--- | :--- | :--- |
| `src/main.py` | Application Entry & GUI | Implements accessible `wx.Frame`, keyboard shortcuts, file open dialogs, and main event loop. |
| `src/locale/` | Localization Repository | Stores binary (`.mo`) and source (`.po`) catalogs for supported languages. |
| `install/pyinstaller/*.spec` | PyInstaller Build Spec | Defines executable metadata, hidden imports, binary targets, and data bindings (`datas=[(..., 'locale')]`). |
| `SConstruct` / `scons` | Automated Build Pipeline | Manages end-to-end compilation workflows and artifact generation. |

---

## 4. Summary Matrix of Analysis Logic

```text
                    +--------------------------------+
                    | Input File (.py / manifest.ini)|
                    +---------------+----------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
   [Python Source Code]                             [manifest.ini]
            |                                               |
            v                                               v
  +------------------+                            +------------------+
  | AST Parsing Tree |                            | Key-Value Parser |
  +--------+---------+                            +--------+---------+
           |                                               |
  +--------+------------------------+                      |
  | - PascalCase (Classes)          |                      |
  | - UPPER_SNAKE (Global Consts)   |                      |
  | - camelCase (Functions/Vars)    |                      |
  | - Tabs Indentation Check        |                      |
  | - i18n _() String Marking       |                      |
  +--------+------------------------+                      |
           |                                               |
           v                                               v
  +------------------------------------------------------------------+
  |              Unified Report Generation & Formatting              |
  +------------------------------------------------------------------+
