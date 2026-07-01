//------------------------------------------------------------------------------
// Project:  MarkdownConverter.ContextMenu
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Shared helpers for IExplorerCommand implementations, including file path
// extraction from IShellItemArray and locating the main MarkdownConverter.exe.
//------------------------------------------------------------------------------

using System.Diagnostics;

namespace MarkdownConverter.ContextMenu;

/// <summary>
/// Shared utilities for shell command handlers.
/// </summary>
internal static class CommandHelper
{
    /// <summary>
    /// Extracts file system paths from the selected Shell items.
    /// </summary>
    internal static List<string> GetSelectedPaths(IShellItemArray? items)
    {
        List<string> paths = [];

        if (items is null)
        {
            return paths;
        }

        try
        {
            items.GetCount(out uint count);

            for (uint i = 0; i < count; i++)
            {
                items.GetItemAt(i, out IShellItem item);
                item.GetDisplayName(SIGDN.SIGDN_FILESYSPATH, out string path);
                paths.Add(path);
            }
        }
        catch
        {
            // Shell may pass unexpected item types; gracefully return what we have.
        }

        return paths;
    }

    /// <summary>
    /// Gets the extension of the first selected file, or null if none.
    /// </summary>
    internal static string? GetFirstExtension(IShellItemArray? items)
    {
        if (items is null)
        {
            return null;
        }

        try
        {
            items.GetCount(out uint count);
            if (count == 0)
            {
                return null;
            }

            items.GetItemAt(0, out IShellItem item);
            item.GetDisplayName(SIGDN.SIGDN_FILESYSPATH, out string path);
            return Path.GetExtension(path);
        }
        catch
        {
            return null;
        }
    }

    /// <summary>
    /// Locates MarkdownConverter.exe relative to the comhost DLL.
    /// </summary>
    internal static string GetConverterExePath()
    {
        // The comhost DLL is deployed alongside MarkdownConverter.exe
        return Path.Combine(AppContext.BaseDirectory, "MarkdownConverter.exe");
    }

    /// <summary>
    /// Launches MarkdownConverter.exe with the specified arguments in silent mode.
    /// </summary>
    internal static void LaunchConverter(string arguments)
    {
        string exePath = GetConverterExePath();

        if (!File.Exists(exePath))
        {
            return;
        }

        ProcessStartInfo psi = new()
        {
            FileName = exePath,
            Arguments = arguments,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        Process.Start(psi);
    }
}
