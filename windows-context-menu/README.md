# Markdown Converter

A free, lightweight, and Windows-compatible document-to-Markdown converter . This tool integrates directly with Windows Explorer by adding a right-click context menu option to convert documents to Markdown using [markitdown](https://github.com/microsoft/markitdown).

## Features
- Seamless integration with Windows Explorer (classic and Windows 11 modern context menu)
- Convert documents to Markdown via right-click menu
- Supports PDF, DOCX, PPTX, XLSX, XLS, MSG, HTML, and HTM
- Batch conversion of multiple selected files
- Fast and lightweight

## Installation
1. Download the latest release from the [Releases](https://github.com/DevEpic/MarkdownConverter/releases) page.
2. In an elevated command prompt type: `PATH\TO\ MarkdownConverter.exe install`

## Expected Usage
1. Right-click on any supported document (PDF, DOCX, PPTX, XLSX, XLS, MSG, HTML, HTM) in Windows Explorer.
2. Select `Convert to Markdown`.
3. The converted `.md` file will be saved in the same directory as the original.

## Additional ways to use
1. Via a command prompt (elevation not required) type: `PATH\TO\ MarkdownConverter.exe markdown "PATH\TO\Document.docx" --silent --overwrite`

## Uninstallation
1.  In an elevated command prompt type: `PATH\TO\ MarkdownConverter.exe uninstall`

## Dependencies
This project uses the following:

- [markitdown](https://github.com/microsoft/markitdown) - Microsoft's document-to-Markdown conversion tool (bundled).
- [CommandLineParser](https://www.nuget.org/packages/CommandLineParser/) - Parses command-line arguments.
- [Microsoft.Win32.Registry](https://www.nuget.org/packages/Microsoft.Win32.Registry/) - Used for modifying Windows registry keys.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve functionality, add new features, or support additional image formats.

## License
This project is licensed under the [MIT License](LICENSE).

## Icon Attribution
Icons used in this project are created by [HideMaru](https://www.flaticon.com/authors/hidemaru/color-lineal-color?author_id=1271&type=standard) from Flaticon.

## Contact
For support or inquiries, please open an issue on GitHub
