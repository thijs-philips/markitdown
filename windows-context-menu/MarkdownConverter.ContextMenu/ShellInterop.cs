//------------------------------------------------------------------------------
// Project:  MarkdownConverter.ContextMenu
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// COM interface definitions for Windows Shell IExplorerCommand integration.
// These interfaces enable items in the Windows 11 modern (compact) context menu.
//------------------------------------------------------------------------------

using System.Runtime.InteropServices;

namespace MarkdownConverter.ContextMenu;

#pragma warning disable CS0108 // Hides inherited member (intentional COM interface re-declaration)

/// <summary>
/// Represents an Explorer command for the Windows 11 modern context menu.
/// </summary>
[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("a08ce4d0-fa25-44ab-b57c-c7b1c323e0b9")]
public interface IExplorerCommand
{
    void GetTitle([In] IShellItemArray? psiItemArray, [MarshalAs(UnmanagedType.LPWStr)] out string ppszName);
    void GetIcon([In] IShellItemArray? psiItemArray, [MarshalAs(UnmanagedType.LPWStr)] out string ppszIcon);
    void GetToolTip([In] IShellItemArray? psiItemArray, [MarshalAs(UnmanagedType.LPWStr)] out string ppszInfotip);
    void GetCanonicalName(out Guid pguidCommandName);
    void GetState([In] IShellItemArray? psiItemArray, [In] bool fOkToBeSlow, out ExplorerCommandState pCmdState);
    void Invoke([In] IShellItemArray? psiItemArray, [In] IntPtr pbc);
    void GetFlags(out ExplorerCommandFlag pdwFlags);
    void EnumSubCommands(out IEnumExplorerCommand? ppEnum);
}

/// <summary>
/// Enumerates a collection of <see cref="IExplorerCommand"/> objects.
/// </summary>
[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("a88826f8-186f-4987-aade-ea0cef8fbfe8")]
public interface IEnumExplorerCommand
{
    [PreserveSig]
    int Next(uint celt,
             [Out, MarshalAs(UnmanagedType.LPArray, ArraySubType = UnmanagedType.Interface, SizeParamIndex = 0)]
             IExplorerCommand[] pUICommand,
             out uint pceltFetched);

    [PreserveSig]
    int Skip(uint celt);

    [PreserveSig]
    int Reset();

    [PreserveSig]
    int Clone(out IEnumExplorerCommand? ppenum);
}

/// <summary>
/// Represents an array of Shell items.
/// </summary>
[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("b63ea76d-1f85-456f-a19c-48159efa858b")]
public interface IShellItemArray
{
    // We only need GetCount and GetItemAt for enumerating selected files.
    void BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppvOut);
    void GetPropertyStore(int flags, ref Guid riid, out IntPtr ppv);
    void GetPropertyDescriptionList(IntPtr keyType, ref Guid riid, out IntPtr ppv);
    void GetAttributes(int AttribFlags, uint sfgaoMask, out uint psfgaoAttribs);
    void GetCount(out uint pdwNumItems);
    void GetItemAt(uint dwIndex, out IShellItem ppsi);
    void EnumItems(out IntPtr ppenumShellItems);
}

/// <summary>
/// Represents a single Shell item (file, folder, etc.).
/// </summary>
[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("43826d1e-e718-42ee-bc55-a1e261c37bfe")]
public interface IShellItem
{
    void BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppv);
    void GetParent(out IShellItem ppsi);
    void GetDisplayName(SIGDN sigdnName, [MarshalAs(UnmanagedType.LPWStr)] out string ppszName);
    void GetAttributes(uint sfgaoMask, out uint psfgaoAttribs);
    void Compare(IShellItem psi, uint hint, out int piOrder);
}

/// <summary>
/// Shell item display name types.
/// </summary>
public enum SIGDN : uint
{
    SIGDN_FILESYSPATH = 0x80058000
}

/// <summary>
/// Explorer command state flags returned by <see cref="IExplorerCommand.GetState"/>.
/// </summary>
[Flags]
public enum ExplorerCommandState : uint
{
    ECS_ENABLED = 0x00,
    ECS_DISABLED = 0x01,
    ECS_HIDDEN = 0x02
}

/// <summary>
/// Explorer command behavior flags returned by <see cref="IExplorerCommand.GetFlags"/>.
/// </summary>
[Flags]
public enum ExplorerCommandFlag : uint
{
    ECF_DEFAULT = 0x00,
    ECF_HASSUBCOMMANDS = 0x01,
    ECF_HASSPLITBUTTON = 0x02,
    ECF_HIDELABEL = 0x04,
    ECF_ISSEPARATOR = 0x08,
    ECF_HASLUASHIELD = 0x10,
    ECF_SEPARATORBEFORE = 0x20,
    ECF_SEPARATORAFTER = 0x40,
    ECF_ISDROPDOWN = 0x80
}

#pragma warning restore CS0108

/// <summary>
/// HRESULT constants used by COM method return values.
/// </summary>
internal static class HResult
{
    internal const int S_OK = 0;
    internal const int S_FALSE = 1;
    internal const int E_NOTIMPL = unchecked((int)0x80004001);
}
