//------------------------------------------------------------------------------
// Project:  MarkdownConverter.ContextMenu
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Reads the formats.json configuration that defines which file extensions
// are eligible for document-to-Markdown conversion.
//------------------------------------------------------------------------------

using System.Text.Json;

namespace MarkdownConverter.ContextMenu;

/// <summary>
/// Provides access to the format conversion configuration loaded from formats.json.
/// </summary>
internal static class FormatsConfig
{
    private static readonly Lazy<FormatsData> _data = new(Load);

    /// <summary>
    /// File extensions eligible for document-to-Markdown conversion.
    /// </summary>
    internal static IReadOnlySet<string> MarkdownExtensions => _data.Value.MarkdownExtensionSet;

    private static FormatsData Load()
    {
        // formats.json lives next to the comhost DLL
        string dir = AppContext.BaseDirectory;
        string path = Path.Combine(dir, "formats.json");

        if (!File.Exists(path))
        {
            return new FormatsData();
        }

        using FileStream stream = File.OpenRead(path);
        JsonDocument doc = JsonDocument.Parse(stream);
        JsonElement root = doc.RootElement;

        var markdownExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        if (root.TryGetProperty("markdownExtensions", out JsonElement mdEl))
        {
            foreach (JsonElement item in mdEl.EnumerateArray())
            {
                string? ext = item.GetString();
                if (ext is not null)
                {
                    markdownExtensions.Add(ext);
                }
            }
        }

        return new FormatsData
        {
            MarkdownExtensionSet = markdownExtensions
        };
    }

    private sealed class FormatsData
    {
        internal IReadOnlySet<string> MarkdownExtensionSet { get; init; }
            = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
    }
}
