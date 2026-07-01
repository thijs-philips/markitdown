//------------------------------------------------------------------------------
// Project:  MarkdownConverter.ContextMenu
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// "Convert to Markdown (clipboard)" command for the Windows 11 modern context
// menu. Converts supported documents and copies the Markdown to the clipboard
// instead of writing a .md file.
//------------------------------------------------------------------------------

using System.Runtime.InteropServices;

namespace MarkdownConverter.ContextMenu;

/// <summary>
/// COM-visible command that appears as "Convert to Markdown (clipboard)" in the
/// Windows 11 compact context menu for supported document file types.
/// </summary>
[ComVisible(true)]
[Guid("f1c4d8b3-2a76-4e90-9c5d-1b8e3f6a2d40")]
[ClassInterface(ClassInterfaceType.None)]
public sealed class MarkdownClipboardCommand : IExplorerCommand
{
    public void GetTitle(IShellItemArray? psiItemArray, out string ppszName)
    {
        ppszName = "Convert to Markdown (clipboard)";
    }

    public void GetIcon(IShellItemArray? psiItemArray, out string ppszIcon)
    {
        ppszIcon = CommandHelper.GetConverterExePath();
    }

    public void GetToolTip(IShellItemArray? psiItemArray, out string ppszInfotip)
    {
        ppszInfotip = "Convert document to Markdown and copy it to the clipboard";
    }

    public void GetCanonicalName(out Guid pguidCommandName)
    {
        pguidCommandName = new Guid("f1c4d8b3-2a76-4e90-9c5d-1b8e3f6a2d40");
    }

    public void GetState(IShellItemArray? psiItemArray, bool fOkToBeSlow, out ExplorerCommandState pCmdState)
    {
        string? ext = CommandHelper.GetFirstExtension(psiItemArray);

        if (ext is not null && FormatsConfig.MarkdownExtensions.Contains(ext))
        {
            pCmdState = ExplorerCommandState.ECS_ENABLED;
        }
        else
        {
            pCmdState = ExplorerCommandState.ECS_HIDDEN;
        }
    }

    public void Invoke(IShellItemArray? psiItemArray, IntPtr pbc)
    {
        List<string> paths = CommandHelper.GetSelectedPaths(psiItemArray);

        if (paths.Count == 0)
        {
            return;
        }

        // Build argument list: markdown "file1" "file2" ... --clipboard --silent
        string fileArgs = string.Join(" ", paths.Select(p => $"\"{p}\""));
        string args = $"markdown {fileArgs} --clipboard --silent";
        CommandHelper.LaunchConverter(args);
    }

    public void GetFlags(out ExplorerCommandFlag pdwFlags)
    {
        pdwFlags = ExplorerCommandFlag.ECF_DEFAULT;
    }

    public void EnumSubCommands(out IEnumExplorerCommand? ppEnum)
    {
        ppEnum = null;
    }
}
