//------------------------------------------------------------------------------
// Project: MarkdownConverter
// Author:  Terry
// License: MIT License (https://mit-license.org/)
//
// Description:
// Converts documents (PDF, Office, HTML, etc.) to Markdown via the bundled
// markitdown executable, with Windows Explorer context-menu integration.
//------------------------------------------------------------------------------

using CommandLine;
using MarkdownConverter.Helpers;
using MarkdownConverter.Options;
using Microsoft.Win32;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

namespace MarkdownConverter
{
    internal class Program
    {
        static bool   isSilent = false;
        static string version = "1.0.0";

        // COM CLSID for the Windows 11 modern context menu handler.
        // Must match the [Guid] attribute in MarkdownConverter.ContextMenu project.
        const string MarkdownConvertCommandClsid = "{e7b3c5a2-9d14-4f67-b8e1-6c2a4d7f9e03}";

        // COM CLSID for the "Convert to Markdown (clipboard)" handler.
        const string MarkdownClipboardCommandClsid = "{f1c4d8b3-2a76-4e90-9c5d-1b8e3f6a2d40}";

        [STAThread]
        static void Main(string[] args)
        {
            version = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "1.0.0";

            var parser = new Parser(with => with.HelpWriter = Console.Out);
            var result = Parser.Default.ParseArguments<AboutOptions, InstallOptions, MarkdownOptions, UninstallOptions>(args);

            // Check if "about" was typed to prevent silent mode
            if (args.Length > 0 && args[0].Equals("about", StringComparison.OrdinalIgnoreCase))
            {
                // Force "about" to always show, even if --silent was used
                ConsoleHelper.ShowConsole();
                HandleAbout();
                return;
            }

            isSilent = (args.Contains("-s") || args.Contains("--silent"));

            if (isSilent)
            {
                ConsoleHelper.HideConsole();
            }
            else
            {
                ConsoleHelper.ShowConsole();
                ShowTitle();
            }

            result.WithParsed<InstallOptions>(opts => HandleInstall(opts))
                  .WithParsed<MarkdownOptions>(opts => HandleMarkdown(opts))
                  .WithParsed<UninstallOptions>(opts => HandleUninstall(opts))
                  .WithNotParsed(errors => {
                      if (!isSilent)
                      {
                          Console.WriteLine("Invalid command. Use -h for help.");
                      }
                  });

            if (isSilent)
            {
                Environment.Exit(0);
            }
            else
            {
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
            }
        }

        /// <summary>
        /// Registers a COM CLSID in HKLM\Software\Classes\CLSID pointing to the comhost DLL.
        /// </summary>
        static void RegisterComServer(string clsid, string comHostPath)
        {
            string clsidKeyPath = $@"Software\Classes\CLSID\{clsid}";

            using (RegistryKey key = Registry.LocalMachine.CreateSubKey($@"{clsidKeyPath}\InprocServer32"))
            {
                key.SetValue("", comHostPath);
                key.SetValue("ThreadingModel", "Both");
            }
        }

        /// <summary>
        /// Removes a COM CLSID registration from HKLM\Software\Classes\CLSID.
        /// </summary>
        static void UnregisterComServer(string clsid)
        {
            Registry.LocalMachine.DeleteSubKeyTree($@"Software\Classes\CLSID\{clsid}", false);
        }

        /// <summary>
        /// Registers a Windows 11 modern context menu entry using ExplorerCommandHandler.
        /// </summary>
        static void RegisterExplorerCommand(string fileExtension, string verbName, string displayName, string clsid, string exePath, int iconIndex = 0)
        {
            string baseKeyPath = $@"SystemFileAssociations\{fileExtension}\shell\{verbName}";

            using (RegistryKey key = Registry.ClassesRoot.CreateSubKey(baseKeyPath))
            {
                key.SetValue("", displayName);
                key.SetValue("ExplorerCommandHandler", clsid);
                key.SetValue("Icon", $"{exePath},{iconIndex}");
            }
        }

        /// <summary>
        /// Removes a Windows 11 modern context menu entry.
        /// </summary>
        static void UnregisterExplorerCommand(string fileExtension, string verbName)
        {
            Registry.ClassesRoot.DeleteSubKeyTree($@"SystemFileAssociations\{fileExtension}\shell\{verbName}", false);
        }

        static void HandleAbout()
        {
            Console.OutputEncoding = Encoding.UTF8;
            ShowTitle();
            ConsoleHelper.WriteLine("Author(s):");
            Console.WriteLine("Terry");
            Console.WriteLine();
            ConsoleHelper.WriteLine("Description:");
            Console.WriteLine("A free, lightweight, Windows-compatible document-to-Markdown converter written in C# .NET 9.");
            Console.WriteLine("This tool integrates directly with Windows Explorer by adding a right-click context menu option for quick document-to-Markdown conversion.");
            Console.WriteLine();
            ConsoleHelper.WriteLine("Dependencies:");
            Console.Write("CommandLineParser ");
            ConsoleHelper.WriteLink("https://www.nuget.org/packages/CommandLineParser/");
            Console.Write("markitdown ");
            ConsoleHelper.WriteLink("https://github.com/microsoft/markitdown");
            Console.WriteLine();
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }

        static void HandleInstall(InstallOptions opts)
        {
            // Check if running as administrator (required for registry access)
            if (!IsAdministrator())
            {
                RestartAsAdmin("install");
                return;
            }

            string exePath = Process.GetCurrentProcess().MainModule!.FileName;
            string appDir = Path.GetDirectoryName(exePath)!;
            string comHostPath = Path.Combine(appDir, "MarkdownConverter.ContextMenu.comhost.dll");
            bool comHostExists = File.Exists(comHostPath);

            // ── Windows 11 modern (compact) context menu via COM ──
            if (comHostExists)
            {
                RegisterComServer(MarkdownConvertCommandClsid, comHostPath);
                RegisterComServer(MarkdownClipboardCommandClsid, comHostPath);

                if (!isSilent)
                {
                    Console.WriteLine("Registered COM servers for Windows 11 context menu.");
                }

                // Register Markdown ExplorerCommandHandler per extension
                foreach (string ext in MarkitdownHelper.SupportedExtensions)
                {
                    RegisterExplorerCommand(
                        ext,
                        "ConvertToMarkdownW11",
                        "Convert to Markdown",
                        MarkdownConvertCommandClsid,
                        exePath);

                    RegisterExplorerCommand(
                        ext,
                        "ConvertToMarkdownClipboardW11",
                        "Convert to Markdown (clipboard)",
                        MarkdownClipboardCommandClsid,
                        exePath);

                    if (!isSilent)
                    {
                        Console.WriteLine($"Registered Win11 Markdown context menu for {ext}");
                    }
                }
            }
            else if (!isSilent)
            {
                Console.WriteLine("comhost DLL not found — skipping Windows 11 context menu registration.");
            }

            // ── Classic context menu (Windows 10 / "Show more options") ──
            foreach (string ext in MarkitdownHelper.SupportedExtensions)
            {
                string baseKeyPath = $@"SystemFileAssociations\{ext}\shell\ConvertToMarkdown";

                using (RegistryKey key = Registry.ClassesRoot.CreateSubKey(baseKeyPath))
                {
                    key.SetValue("MUIVerb", "Convert to Markdown");
                    key.SetValue("Icon", $"{exePath},0");
                }

                using (RegistryKey key = Registry.ClassesRoot.CreateSubKey($@"{baseKeyPath}\command"))
                {
                    key.SetValue("", $"\"{exePath}\" markdown \"%1\" --silent");
                }

                string clipKeyPath = $@"SystemFileAssociations\{ext}\shell\ConvertToMarkdownClipboard";

                using (RegistryKey key = Registry.ClassesRoot.CreateSubKey(clipKeyPath))
                {
                    key.SetValue("MUIVerb", "Convert to Markdown (clipboard)");
                    key.SetValue("Icon", $"{exePath},0");
                }

                using (RegistryKey key = Registry.ClassesRoot.CreateSubKey($@"{clipKeyPath}\command"))
                {
                    key.SetValue("", $"\"{exePath}\" markdown \"%1\" --clipboard --silent");
                }

                if (!isSilent)
                {
                    Console.WriteLine($"Registering classic Markdown context menu for {ext}...");
                }
            }

            // Notify Explorer that file associations changed so context menus refresh
            SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, IntPtr.Zero, IntPtr.Zero);

            if (!isSilent)
            {
                Console.WriteLine("Context menu installed.");
            }
        }

        static void HandleUninstall(UninstallOptions opts)
        {
            // Check if running as administrator (required for registry access)
            if (!IsAdministrator())
            {
                RestartAsAdmin("uninstall");
                return;
            }

            // ── Remove Windows 11 modern context menu registrations ──
            UnregisterComServer(MarkdownConvertCommandClsid);
            UnregisterComServer(MarkdownClipboardCommandClsid);

            if (!isSilent)
            {
                Console.WriteLine("Removed COM server registrations.");
            }

            foreach (string ext in MarkitdownHelper.SupportedExtensions)
            {
                UnregisterExplorerCommand(ext, "ConvertToMarkdownW11");
                UnregisterExplorerCommand(ext, "ConvertToMarkdownClipboardW11");
            }

            if (!isSilent)
            {
                Console.WriteLine("Removed Windows 11 context menu entries.");
            }

            // ── Remove classic context menu registrations ──
            foreach (string ext in MarkitdownHelper.SupportedExtensions)
            {
                Registry.ClassesRoot.DeleteSubKeyTree($@"SystemFileAssociations\{ext}\shell\ConvertToMarkdown", false);
                Registry.ClassesRoot.DeleteSubKeyTree($@"SystemFileAssociations\{ext}\shell\ConvertToMarkdownClipboard", false);

                if (!isSilent)
                {
                    Console.WriteLine($"Uninstalled classic Markdown context menu for {ext}.");
                }
            }

            // Notify Explorer that file associations changed so context menus refresh
            SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, IntPtr.Zero, IntPtr.Zero);

            if (!isSilent)
            {
                Console.WriteLine("Context menu uninstalled.");
            }
        }

        static bool IsAdministrator()
        {
            return new System.Security.Principal.WindowsPrincipal(System.Security.Principal.WindowsIdentity.GetCurrent()).IsInRole(System.Security.Principal.WindowsBuiltInRole.Administrator);
        }

        [DllImport("shell32.dll", CharSet = CharSet.Auto)]
        private static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);

        private const int SHCNE_ASSOCCHANGED = 0x08000000;
        private const int SHCNF_IDLIST = 0x0000;

        static void RestartAsAdmin(string command)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName        = Process.GetCurrentProcess().MainModule!.FileName,
                Arguments       = command,
                Verb            = "runas",
                UseShellExecute = true
            };

            Process.Start(psi);
        }

        static void HandleMarkdown(MarkdownOptions opts)
        {
            List<string> files;
            string batchKey = opts.ToClipboard ? "markdown_clipboard" : "markdown";

            if (isSilent)
            {
                // Context menu: batch files from parallel invocations
                string firstFile = opts.SourceFilePaths.First();
                files = ContextMenuFileBatcher.CollectFiles(batchKey, firstFile);

                if (files.Count == 0)
                {
                    // We are not the coordinator — another instance handles the UI
                    return;
                }
            }
            else
            {
                files = opts.SourceFilePaths.ToList();
            }

            // Validate all files up front
            files = files.Where(f =>
            {
                if (!File.Exists(f))
                {
                    Console.WriteLine($"Skipping missing file: {f}");
                    return false;
                }

                string ext = Path.GetExtension(f);
                if (!MarkitdownHelper.IsSupported(ext))
                {
                    Console.WriteLine($"Skipping unsupported format ({ext}): {f}");
                    return false;
                }

                return true;
            }).ToList();

            if (files.Count == 0)
            {
                if (!isSilent) Console.WriteLine("No valid files to convert.");
                return;
            }

            if (opts.ToClipboard)
            {
                HandleMarkdownToClipboard(files);
                return;
            }

            // File mode: --overwrite pins the conflict policy; otherwise prompt the user.
            ConflictAction? initialConflict = opts.AllowOverwrite ? ConflictAction.Overwrite : null;

            ShowProgressDialog(
                "Converting to Markdown",
                "Markdown",
                files,
                initialConflict,
                (file, resolver, log) => ConvertSingleDocument(file, resolver, log));
        }

        static void HandleMarkdownToClipboard(List<string> files)
        {
            // Sink collects (sourceFile, markdown) in processing order.
            List<(string Source, string Markdown)> sink = [];

            ShowProgressDialog(
                "Converting to Markdown (clipboard)",
                "Markdown",
                files,
                ConflictAction.Overwrite,   // temp files only — never prompts
                (file, _, log) => ConvertToClipboardText(file, sink, log));

            if (sink.Count == 0)
            {
                return;
            }

            string combined = sink.Count == 1
                ? sink[0].Markdown.TrimEnd()
                : string.Join(
                    Environment.NewLine + Environment.NewLine,
                    sink.Select(s => $"<!-- {Path.GetFileName(s.Source)} -->{Environment.NewLine}{s.Markdown.TrimEnd()}"));

            try
            {
                Clipboard.SetText(combined);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Conversion succeeded but copying to the clipboard failed:{Environment.NewLine}{ex.Message}",
                    "Markdown Converter",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
                return;
            }

            MessageBox.Show(
                $"Copied {sink.Count} document(s) to the clipboard as Markdown.",
                "Markdown Converter",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
        }

        static FileConversionResult ConvertSingleDocument(string sourceFilePath, ConflictResolver conflicts, Action<string>? log = null)
        {
            string targetFilePath = Path.ChangeExtension(sourceFilePath, ".md");

            if (File.Exists(targetFilePath))
            {
                switch (conflicts.Resolve(targetFilePath))
                {
                    case ConflictAction.Skip:
                        return new FileConversionResult(sourceFilePath, FileStatus.Skipped, string.Empty, null);
                    case ConflictAction.Rename:
                        targetFilePath = PathHelper.NextAvailablePath(targetFilePath);
                        break;
                    case ConflictAction.Overwrite:
                    default:
                        break;
                }
            }

            if (MarkitdownHelper.Convert(sourceFilePath, targetFilePath, out string errorMessage, onOutputLine: log))
            {
                return new FileConversionResult(sourceFilePath, FileStatus.Success, string.Empty, targetFilePath);
            }

            return new FileConversionResult(sourceFilePath, FileStatus.Failed, errorMessage, null);
        }

        static FileConversionResult ConvertToClipboardText(
            string sourceFilePath,
            List<(string Source, string Markdown)> sink,
            Action<string>? log = null)
        {
            string tempPath = Path.Combine(Path.GetTempPath(), $"mdconv_{Guid.NewGuid():N}.md");

            try
            {
                if (!MarkitdownHelper.Convert(sourceFilePath, tempPath, out string errorMessage, onOutputLine: log))
                {
                    return new FileConversionResult(sourceFilePath, FileStatus.Failed, errorMessage, null);
                }

                string text = File.ReadAllText(tempPath);
                sink.Add((sourceFilePath, text));
                return new FileConversionResult(sourceFilePath, FileStatus.Success, string.Empty, null);
            }
            catch (Exception ex)
            {
                return new FileConversionResult(sourceFilePath, FileStatus.Failed, ex.Message, null);
            }
            finally
            {
                try
                {
                    if (File.Exists(tempPath)) File.Delete(tempPath);
                }
                catch
                {
                    // Best-effort temp cleanup.
                }
            }
        }

        static void ShowProgressDialog(
            string title,
            string targetDescription,
            List<string> files,
            ConflictAction? initialConflict,
            Func<string, ConflictResolver, Action<string>, FileConversionResult> convertFile)
        {
            Application.EnableVisualStyles();
            Application.SetHighDpiMode(HighDpiMode.SystemAware);

            using ConversionProgressForm form = new(title, targetDescription, files, initialConflict, convertFile);
            Application.Run(form);
        }

        static void ShowTitle()
        {
            ConsoleHelper.WriteSeparator();
            ConsoleHelper.WriteLine($"Markdown Converter - v{version}", true);
            ConsoleHelper.WriteSeparator();
        }

    }
}
