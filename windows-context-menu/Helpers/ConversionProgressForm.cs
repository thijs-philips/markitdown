//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// A progress dialog that converts files sequentially, showing per-file status.
//------------------------------------------------------------------------------

using System.Windows.Forms;

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// Outcome of a single file conversion.
    /// </summary>
    internal enum FileStatus
    {
        Success,
        Skipped,
        Failed
    }

    /// <summary>
    /// Result of a single file conversion within a batch.
    /// </summary>
    internal sealed record FileConversionResult(
        string SourceFile,
        FileStatus Status,
        string ErrorMessage,
        string? OutputPath);

    /// <summary>
    /// Progress dialog that converts files sequentially and reports status to the user.
    /// </summary>
    internal sealed class ConversionProgressForm : Form
    {
        private readonly Label _lblCurrentFile;
        private readonly Label _lblProgress;
        private readonly ProgressBar _progressBar;
        private readonly Button _btnCancel;
        private readonly Button _btnClose;
        private readonly TextBox _txtLog;

        private readonly IReadOnlyList<string> _files;
        private readonly Func<string, ConflictResolver, Action<string>, FileConversionResult> _convertFile;
        private readonly ConflictResolver _resolver;
        private readonly string _targetDescription;

        private CancellationTokenSource? _cts;
        private readonly List<FileConversionResult> _results = [];

        /// <summary>
        /// Conversion results for all processed files. Available after the form closes.
        /// </summary>
        internal IReadOnlyList<FileConversionResult> Results => _results;

        /// <summary>
        /// Creates a new progress dialog.
        /// </summary>
        /// <param name="title">Window title (e.g., "Converting to Markdown").</param>
        /// <param name="targetDescription">Short description of target format (e.g., "Markdown", "PNG").</param>
        /// <param name="files">List of source file paths to convert.</param>
        /// <param name="initialConflict">
        /// A pre-decided conflict action applied without prompting (e.g. Overwrite when
        /// --overwrite is passed), or null to prompt the user on the first conflict.
        /// </param>
        /// <param name="convertFile">
        /// Callback that converts a single file. Receives the file path, a conflict
        /// resolver, and a log callback for real-time output streaming.
        /// </param>
        internal ConversionProgressForm(
            string title,
            string targetDescription,
            IReadOnlyList<string> files,
            ConflictAction? initialConflict,
            Func<string, ConflictResolver, Action<string>, FileConversionResult> convertFile)
        {
            ArgumentNullException.ThrowIfNull(files);
            ArgumentNullException.ThrowIfNull(convertFile);

            _files = files;
            _convertFile = convertFile;
            _resolver = new ConflictResolver(initialConflict, PromptForConflict);
            _targetDescription = targetDescription;

            Text = title;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            StartPosition = FormStartPosition.CenterScreen;
            MaximizeBox = false;
            MinimizeBox = false;
            ClientSize = new Size(500, 300);
            ShowInTaskbar = true;
            TopMost = true;

            _lblCurrentFile = new Label
            {
                AutoEllipsis = true,
                Location = new Point(16, 16),
                Size = new Size(468, 20),
                Text = "Preparing..."
            };

            _progressBar = new ProgressBar
            {
                Location = new Point(16, 44),
                Size = new Size(468, 28),
                Minimum = 0,
                Maximum = Math.Max(files.Count, 1),
                Style = ProgressBarStyle.Continuous
            };

            _lblProgress = new Label
            {
                Location = new Point(16, 78),
                Size = new Size(468, 20),
                Text = $"0 of {files.Count} files"
            };

            _txtLog = new TextBox
            {
                Location = new Point(16, 104),
                Size = new Size(468, 140),
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                Font = new Font("Consolas", 8.25f)
            };

            _btnCancel = new Button
            {
                Text = "Cancel",
                Size = new Size(90, 30),
                Location = new Point(394, 256)
            };
            _btnCancel.Click += BtnCancel_Click;

            _btnClose = new Button
            {
                Text = "Close",
                Size = new Size(90, 30),
                Location = new Point(394, 256),
                Visible = false
            };
            _btnClose.Click += (_, _) => Close();

            Controls.Add(_lblCurrentFile);
            Controls.Add(_progressBar);
            Controls.Add(_lblProgress);
            Controls.Add(_txtLog);
            Controls.Add(_btnCancel);
            Controls.Add(_btnClose);

            AcceptButton = _btnClose;
            Load += OnFormLoad;
        }

        private async void OnFormLoad(object? sender, EventArgs e)
        {
            _cts = new CancellationTokenSource();
            int completed = 0;
            int failed = 0;
            int skipped = 0;

            try
            {
                await Task.Run(() =>
                {
                    foreach (string file in _files)
                    {
                        if (_cts.Token.IsCancellationRequested)
                            break;

                        string fileName = Path.GetFileName(file);

                        UpdateUI(() =>
                        {
                            _lblCurrentFile.Text = $"Converting {fileName} to {_targetDescription}...";
                        });

                        AppendLog($"→ {fileName}");

                        FileConversionResult result = _convertFile(file, _resolver, line => AppendLog($"  {line}"));
                        _results.Add(result);

                        completed++;

                        switch (result.Status)
                        {
                            case FileStatus.Success:
                                AppendLog("  ✓ Done");
                                break;
                            case FileStatus.Skipped:
                                skipped++;
                                AppendLog("  ↷ Skipped (file already exists)");
                                break;
                            default:
                                failed++;
                                AppendLog($"  ✗ {result.ErrorMessage}");
                                break;
                        }

                        UpdateUI(() =>
                        {
                            _progressBar.Value = completed;
                            _lblProgress.Text = $"{completed} of {_files.Count} files";
                        });
                    }
                }, _cts.Token);
            }
            catch (OperationCanceledException)
            {
                AppendLog("Cancelled by user.");
            }
            catch (Exception ex)
            {
                AppendLog($"Unexpected error: {ex.Message}");
            }
            finally
            {
                _cts.Dispose();
                _cts = null;
            }

            string summary = (failed, skipped) switch
            {
                (0, 0) => $"All {completed} file(s) converted successfully.",
                (> 0, _) => $"Completed: {completed} of {_files.Count} ({failed} failed{(skipped > 0 ? $", {skipped} skipped" : string.Empty)})",
                _ => $"Completed: {completed} of {_files.Count} ({skipped} skipped)"
            };

            AppendLog(summary);

            if (failed == 0 && skipped == 0)
            {
                // Auto-close on a clean run, like a file copy dialog
                Close();
            }
            else
            {
                // Stay open so the user can review skips / errors
                UpdateUI(() =>
                {
                    _lblCurrentFile.Text = summary;
                    _btnCancel.Visible = false;
                    _btnClose.Visible = true;
                    _btnClose.Focus();
                });
            }
        }

        /// <summary>
        /// Shows the conflict dialog on the UI thread and returns the user's choice.
        /// Invoked synchronously from the background conversion loop.
        /// </summary>
        private (ConflictAction Action, bool ApplyToAll) PromptForConflict(string targetPath)
        {
            ConflictAction action = ConflictAction.Skip;
            bool applyToAll = false;

            UpdateUI(() =>
            {
                // Drop our TopMost while the modal prompt is open, otherwise the
                // prompt (even though modal) can be trapped behind this form in the
                // TopMost Z-order band. Restore it afterwards.
                bool wasTopMost = TopMost;
                TopMost = false;

                using ConflictPromptDialog dlg = new(targetPath);
                dlg.Shown += (_, _) =>
                {
                    dlg.Activate();
                    dlg.BringToFront();
                };
                dlg.ShowDialog(this);
                action = dlg.SelectedAction;
                applyToAll = dlg.ApplyToAll;

                TopMost = wasTopMost;
            });

            return (action, applyToAll);
        }

        private void BtnCancel_Click(object? sender, EventArgs e)
        {
            _cts?.Cancel();
            _btnCancel.Enabled = false;
            _btnCancel.Text = "Cancelling...";
            _lblCurrentFile.Text = "Cancelling after current file...";
        }

        private void AppendLog(string message)
        {
            UpdateUI(() =>
            {
                _txtLog.AppendText(message + Environment.NewLine);
            });
        }

        private void UpdateUI(Action action)
        {
            if (InvokeRequired)
                Invoke(action);
            else
                action();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _cts?.Dispose();
            }

            base.Dispose(disposing);
        }
    }
}
