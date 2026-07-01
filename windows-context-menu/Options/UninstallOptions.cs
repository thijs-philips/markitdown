//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Represents the command-line options for uninstalling the context menu.
//------------------------------------------------------------------------------

using CommandLine;

namespace MarkdownConverter.Options
{
    /// <summary>
    /// Command-line options for uninstalling the Windows Explorer context menu.
    /// </summary>
    [Verb("uninstall", HelpText = "Remove context menu from Windows Explorer.")]
    class UninstallOptions : SilentOptions
    {
    }
}
