//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// License:  MIT License (https://mit-license.org/)
//
// Description:
// File-conflict resolution for batch conversions: an enum of possible actions,
// a resolver that remembers an "apply to all" decision, a small modal prompt
// dialog, and a helper to compute the next free "name (n).md" path.
//------------------------------------------------------------------------------

using System.Windows.Forms;

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// What to do when a target file already exists.
    /// </summary>
    internal enum ConflictAction
    {
        Overwrite,
        Skip,
        Rename
    }

    /// <summary>
    /// Resolves file conflicts for a batch, optionally remembering a decision so
    /// the user is only prompted once when they choose "apply to all".
    /// </summary>
    /// <remarks>
    /// Conversions run sequentially (one file at a time), so no locking is needed.
    /// </remarks>
    internal sealed class ConflictResolver
    {
        private readonly Func<string, (ConflictAction Action, bool ApplyToAll)> _prompt;
        private ConflictAction? _sticky;

        /// <summary>
        /// Creates a resolver.
        /// </summary>
        /// <param name="initialSticky">
        /// A pre-decided action applied to every conflict without prompting
        /// (e.g. <see cref="ConflictAction.Overwrite"/> when --overwrite is passed).
        /// Pass null to prompt on the first conflict.
        /// </param>
        /// <param name="prompt">
        /// Callback that asks the user how to handle a single conflict, returning the
        /// chosen action and whether it should apply to all remaining conflicts.
        /// </param>
        internal ConflictResolver(
            ConflictAction? initialSticky,
            Func<string, (ConflictAction Action, bool ApplyToAll)> prompt)
        {
            ArgumentNullException.ThrowIfNull(prompt);
            _sticky = initialSticky;
            _prompt = prompt;
        }

        /// <summary>
        /// Decides what to do about an existing <paramref name="targetPath"/>.
        /// </summary>
        internal ConflictAction Resolve(string targetPath)
        {
            if (_sticky.HasValue)
            {
                return _sticky.Value;
            }

            var (action, applyToAll) = _prompt(targetPath);

            if (applyToAll)
            {
                _sticky = action;
            }

            return action;
        }
    }

    /// <summary>
    /// Path helpers for conflict-aware output naming.
    /// </summary>
    internal static class PathHelper
    {
        /// <summary>
        /// Returns the first non-existing variant of <paramref name="path"/>,
        /// inserting " (2)", " (3)", … before the extension as needed.
        /// </summary>
        internal static string NextAvailablePath(string path)
        {
            if (!File.Exists(path))
            {
                return path;
            }

            string dir = Path.GetDirectoryName(path) ?? string.Empty;
            string name = Path.GetFileNameWithoutExtension(path);
            string ext = Path.GetExtension(path);

            for (int i = 2; ; i++)
            {
                string candidate = Path.Combine(dir, $"{name} ({i}){ext}");
                if (!File.Exists(candidate))
                {
                    return candidate;
                }
            }
        }
    }

    /// <summary>
    /// Modal dialog asking the user how to handle a single file conflict, with an
    /// optional "apply to all remaining conflicts" choice.
    /// </summary>
    internal sealed class ConflictPromptDialog : Form
    {
        /// <summary>The action the user selected.</summary>
        internal ConflictAction SelectedAction { get; private set; } = ConflictAction.Skip;

        /// <summary>Whether the choice should apply to all remaining conflicts.</summary>
        internal bool ApplyToAll => _chkApplyToAll.Checked;

        private readonly CheckBox _chkApplyToAll;

        internal ConflictPromptDialog(string targetPath)
        {
            string fileName = Path.GetFileName(targetPath);

            Text = "File already exists";
            FormBorderStyle = FormBorderStyle.FixedDialog;
            StartPosition = FormStartPosition.CenterParent;
            MaximizeBox = false;
            MinimizeBox = false;
            ShowInTaskbar = false;
            // The progress form is TopMost; a modal child that isn't TopMost would be
            // trapped behind it (separate Z-order band). Keep this prompt on top.
            TopMost = true;
            ClientSize = new Size(440, 170);

            Label message = new()
            {
                Location = new Point(16, 16),
                Size = new Size(408, 48),
                Text = $"\"{fileName}\" already exists.\nWhat would you like to do?"
            };

            _chkApplyToAll = new CheckBox
            {
                Location = new Point(16, 72),
                Size = new Size(408, 24),
                Text = "Apply to all remaining conflicts"
            };

            Button btnOverwrite = new()
            {
                Text = "Overwrite",
                Size = new Size(120, 32),
                Location = new Point(16, 120)
            };
            btnOverwrite.Click += (_, _) => Select(ConflictAction.Overwrite);

            Button btnRename = new()
            {
                Text = "Keep both",
                Size = new Size(120, 32),
                Location = new Point(160, 120)
            };
            btnRename.Click += (_, _) => Select(ConflictAction.Rename);

            Button btnSkip = new()
            {
                Text = "Skip",
                Size = new Size(120, 32),
                Location = new Point(304, 120)
            };
            btnSkip.Click += (_, _) => Select(ConflictAction.Skip);

            Controls.Add(message);
            Controls.Add(_chkApplyToAll);
            Controls.Add(btnOverwrite);
            Controls.Add(btnRename);
            Controls.Add(btnSkip);

            AcceptButton = btnOverwrite;
            CancelButton = btnSkip;
        }

        private void Select(ConflictAction action)
        {
            SelectedAction = action;
            DialogResult = DialogResult.OK;
            Close();
        }
    }
}
