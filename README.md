# MarkItDown

[![Version](https://img.shields.io/badge/version-0.1.6-blue)](https://github.com/thijs-philips/markitdown/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20x64-lightgrey)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Convert any document to Markdown — no Python required.**

A self-contained Windows tool that converts files to structured Markdown, usable from the command line or directly from the Windows Explorer right-click menu. Based on Microsoft's [markitdown](https://github.com/microsoft/markitdown), repackaged as a portable standalone executable.

<!-- TODO: hero screenshot of context menu in action -->
<!-- ![Context menu demo](assets/context-menu-demo.png) -->

**Supports:** PDF · Word · Excel · PowerPoint · HTML · Images · Audio · EPUB · CSV · JSON · XML · ZIP · Outlook MSG

---

## Install

Download the latest release from the [Releases](https://github.com/thijs-philips/markitdown/releases) page — no Python, no dependencies.

| Package | Description |
|---------|-------------|
| `markitdown-*-win-x64.zip` | Standalone CLI (~47 MB) |
| `MarkdownConverter-setup.exe` | Windows Explorer context menu integration *(coming soon)* |

## Quickstart

```powershell
# Convert a file
markitdown report.pdf -o report.md

# Pipe to stdout
markitdown presentation.pptx

# Batch convert
Get-ChildItem *.docx | ForEach-Object { markitdown $_ -o "$($_.BaseName).md" }
```

Output preserves document structure — headings, tables, lists, links:

```
# Quarterly Report

| Region | Revenue | Growth |
|--------|---------|--------|
| EMEA   | €4.2M   | +12%   |
| APAC   | €3.1M   | +8%    |

## Next Steps
- Finalize budget for Q4
- Schedule board review
```

## Windows Explorer Integration

Right-click any supported file → **Convert to Markdown**. The `.md` file is saved alongside the original.

See [windows-context-menu/README.md](windows-context-menu/README.md) for install/uninstall instructions.

## Performance

Compiled to native code with Nuitka (ahead-of-time C compilation, no interpreter overhead).

| Metric | Value | vs full Python env* |
|--------|-------|---------------------|
| Startup | ~0.3s (cold), near-instant (warm) | ~60% faster |
| Executable size | 47.8 MB | ~92% smaller |
| Distributable zip | 46.1 MB | ~93% smaller |
| Runtime dependencies | None (fully self-contained) | — |

<sub>*Based on a casual comparison against a `pip install markitdown[all]` venv (~620 MB installed). Not a rigorous benchmark — your mileage may vary, batteries not included, etc.</sub>

## How It Works

This fork takes the upstream `markitdown` Python library and compiles it into a standalone Windows executable using [Nuitka](https://nuitka.net). The result is a single folder you can drop anywhere — no Python installation, no pip, no virtual environments.

Heavy dependencies (pandas, magika) have been replaced with lightweight alternatives (openpyxl, built-in file-type detection) to keep the binary small and fast.

## Advanced Usage

<details>
<summary>Python library (pip install)</summary>

If you prefer using markitdown as a Python library:

```bash
pip install 'markitdown[all]'
```

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("report.pdf")
print(result.text_content)
```

See the [upstream documentation](https://github.com/microsoft/markitdown) for full Python API details, plugins, Azure integrations, and optional dependencies.

</details>


<details>
<summary>Azure Document Intelligence / Content Understanding</summary>

For cloud-based high-quality extraction, see:
- [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Azure Content Understanding](https://learn.microsoft.com/azure/ai-services/content-understanding/)

Both are supported via the Python library (`pip install 'markitdown[az-doc-intel]'` or `markitdown[az-content-understanding]`).

</details>

## Build from Source

- [build_nuitka/README.md](build_nuitka/README.md) — Nuitka build (recommended)
- [build_pyinstaller/README.md](build_pyinstaller/README.md) — PyInstaller build (alternative)
- [windows-context-menu/](windows-context-menu/) — C# context menu shell extension

Requires: Windows, Python 3.13+, MSVC (for Nuitka) and/or PyInstaller.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and PR guidelines.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA). For details, visit https://cla.opensource.microsoft.com.

## License

[MIT](LICENSE) — Copyright (c) Microsoft Corporation.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
