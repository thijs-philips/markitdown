//------------------------------------------------------------------------------
// Project:  MarkdownConverter.ContextMenu
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// "Convert to Markdown" command for the Windows 11 modern context menu.
// Visible only for document types supported by markitdown.
//------------------------------------------------------------------------------

using System.Runtime.InteropServices;

namespace MarkdownConverter.ContextMenu;

/// <summary>
/// COM-visible command that appears as "Convert to Markdown" in the Windows 11
/// compact context menu for supported document file types.
/// </summary>
[ComVisible(true)]
[Guid("e7b3c5a2-9d14-4f67-b8e1-6c2a4d7f9e03")]
[ClassInterface(ClassInterfaceType.None)]
public sealed class MarkdownConvertCommand : IExplorerCommand
{
    public void GetTitle(IShellItemArray? psiItemArray, out string ppszName)
    {
        ppszName = "Convert to Markdown";
    }

    public void GetIcon(IShellItemArray? psiItemArray, out string ppszIcon)
    {
        ppszIcon = CommandHelper.GetConverterExePath();
    }

    public void GetToolTip(IShellItemArray? psiItemArray, out string ppszInfotip)
    {
        ppszInfotip = "Convert document to Markdown using markitdown";
    }

    public void GetCanonicalName(out Guid pguidCommandName)
    {
        pguidCommandName = new Guid("e7b3c5a2-9d14-4f67-b8e1-6c2a4d7f9e03");
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

        // Build argument list: markdown "file1" "file2" ... --silent
        string fileArgs = string.Join(" ", paths.Select(p => $"\"{p}\""));
        string args = $"markdown {fileArgs} --silent";
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
