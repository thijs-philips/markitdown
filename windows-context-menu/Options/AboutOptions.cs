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
    /// Displays information about the application.
    /// </summary>
    [Verb("about", HelpText = "Displays information about the application.")]
    class AboutOptions : SilentOptions
    {
    }
}
