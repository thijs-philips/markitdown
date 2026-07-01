//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Provides methods to invoke markitdown.exe for document-to-Markdown conversion.
//------------------------------------------------------------------------------

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// Invokes the bundled markitdown executable to convert documents to Markdown.
    /// </summary>
    internal static class MarkitdownHelper
    {
        /// <summary>
        /// Document file extensions supported by markitdown.
        /// </summary>
        internal static readonly string[] SupportedExtensions =
        [
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".xls",
            ".msg",
            ".html",
            ".htm"
        ];

        /// <summary>
        /// Timeout for markitdown conversions (large documents may take a while).
        /// </summary>
        private static readonly TimeSpan ConversionTimeout = TimeSpan.FromMinutes(2);

        /// <summary>
        /// Returns true if the given file extension is supported by markitdown.
        /// </summary>
        internal static bool IsSupported(string extension)
        {
            return SupportedExtensions.Contains(extension, StringComparer.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Converts a document to Markdown by invoking markitdown.exe.
        /// </summary>
        /// <param name="sourceFilePath">Full path to the source document.</param>
        /// <param name="outputFilePath">Full path for the output .md file.</param>
        /// <param name="errorMessage">Error details when conversion fails.</param>
        /// <param name="onOutputLine">Optional callback for real-time stdout streaming.</param>
        /// <returns>True if conversion succeeded; otherwise false.</returns>
        internal static bool Convert(
            string sourceFilePath,
            string outputFilePath,
            out string errorMessage,
            Action<string>? onOutputLine = null)
        {
            errorMessage = string.Empty;

            string exePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "markitdown", "markitdown.exe");

            ProcessResult result;
            try
            {
                result = ProcessHandler.Run(
                    exePath,
                    $"\"{sourceFilePath}\" -o \"{outputFilePath}\"",
                    timeout: ConversionTimeout,
                    onOutputLine: onOutputLine,
                    onErrorLine: onOutputLine);
            }
            catch (FileNotFoundException ex)
            {
                errorMessage = ex.Message;
                return false;
            }

            if (result.TimedOut)
            {
                errorMessage = "markitdown conversion timed out.";
                return false;
            }

            if (!result.Success)
            {
                errorMessage = string.IsNullOrWhiteSpace(result.StandardError)
                    ? $"markitdown.exe exited with code {result.ExitCode}."
                    : result.StandardError;
                return false;
            }

            return true;
        }
    }
}
