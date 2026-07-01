//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Defines the command-line options for converting documents to Markdown.
//------------------------------------------------------------------------------

using CommandLine;

namespace MarkdownConverter.Options
{
    /// <summary>
    /// Command-line options for converting a document to Markdown using markitdown.
    /// </summary>
    [Verb("markdown", HelpText = "Convert a document to Markdown.")]
    class MarkdownOptions : SilentOptions
    {
        /// <summary>
        /// If true, allows overwriting of existing files.
        /// </summary>
        [Option('o', "overwrite", Default = false, HelpText = "Allow target file overwrites.")]
        public bool AllowOverwrite { get; set; }

        /// <summary>
        /// If true, copies the resulting Markdown to the clipboard instead of writing .md files.
        /// </summary>
        [Option('c', "clipboard", Default = false, HelpText = "Copy the Markdown result to the clipboard instead of saving a file.")]
        public bool ToClipboard { get; set; }

        /// <summary>
        /// Path(s) to the source document file(s).
        /// </summary>
        [Value(0, MetaName = "source", Required = true, Min = 1, HelpText = "Path(s) to the source document file(s).")]
        public IEnumerable<string> SourceFilePaths { get; set; } = [];
    }
}
