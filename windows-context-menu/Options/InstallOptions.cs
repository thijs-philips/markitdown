//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Represents the command-line options for installing the context menu.
//------------------------------------------------------------------------------

using CommandLine;

namespace MarkdownConverter.Options
{
    /// <summary>
    /// Command-line options for installing the Windows Explorer context menu.
    /// </summary>
    [Verb("install", HelpText = "Register context menu for Windows Explorer.")]
    class InstallOptions : SilentOptions
    {
    }
}
