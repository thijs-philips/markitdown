//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// General-purpose wrapper for running external processes with captured output.
//------------------------------------------------------------------------------

using System.Diagnostics;
using System.Text;

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// Immutable result of a completed process execution.
    /// </summary>
    internal sealed record ProcessResult
    {
        /// <summary>Process exit code (0 typically means success).</summary>
        public required int ExitCode { get; init; }

        /// <summary>Complete standard output captured from the process.</summary>
        public required string StandardOutput { get; init; }

        /// <summary>Complete standard error captured from the process.</summary>
        public required string StandardError { get; init; }

        /// <summary>True when the process was terminated because it exceeded the timeout.</summary>
        public required bool TimedOut { get; init; }

        /// <summary>Wall-clock duration of the process execution.</summary>
        public required TimeSpan Elapsed { get; init; }

        /// <summary>True when the process exited with code 0 and did not time out.</summary>
        public bool Success => ExitCode == 0 && !TimedOut;
    }

    /// <summary>
    /// Runs external processes and captures their output, errors, and exit code.
    /// </summary>
    /// <remarks>
    /// <para>Stdout and stderr are read asynchronously to avoid deadlocks when buffers fill up.</para>
    /// <para>A configurable timeout kills the process tree if the child hangs.</para>
    /// </remarks>
    internal static class ProcessHandler
    {
        /// <summary>Default timeout when none is specified (30 seconds).</summary>
        private static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(30);

        /// <summary>
        /// Runs an executable with the given arguments and waits for completion.
        /// </summary>
        /// <param name="executable">Full path to the executable.</param>
        /// <param name="arguments">Command-line arguments.</param>
        /// <param name="workingDirectory">
        /// Working directory for the process. When null, defaults to the executable's directory.
        /// </param>
        /// <param name="timeout">
        /// Maximum wall-clock time before the process is killed. When null, defaults to 30 seconds.
        /// </param>
        /// <param name="onOutputLine">
        /// Optional callback invoked for each line of standard output as it arrives (real-time streaming).
        /// Called from a background thread — callers must marshal to the UI thread if needed.
        /// </param>
        /// <param name="onErrorLine">
        /// Optional callback invoked for each line of standard error as it arrives (real-time streaming).
        /// Called from a background thread — callers must marshal to the UI thread if needed.
        /// </param>
        /// <returns>A <see cref="ProcessResult"/> with captured output, errors, exit code, and timing.</returns>
        /// <exception cref="FileNotFoundException">Thrown when <paramref name="executable"/> does not exist.</exception>
        internal static ProcessResult Run(
            string executable,
            string arguments,
            string? workingDirectory = null,
            TimeSpan? timeout = null,
            Action<string>? onOutputLine = null,
            Action<string>? onErrorLine = null)
        {
            ArgumentNullException.ThrowIfNull(executable);

            if (!File.Exists(executable))
            {
                throw new FileNotFoundException($"Executable not found: {executable}", executable);
            }

            var effectiveTimeout = timeout ?? DefaultTimeout;
            var resolvedWorkingDir = workingDirectory ?? Path.GetDirectoryName(executable) ?? string.Empty;

            var psi = new ProcessStartInfo
            {
                FileName = executable,
                Arguments = arguments,
                WorkingDirectory = resolvedWorkingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            var stdoutBuilder = new StringBuilder();
            var stderrBuilder = new StringBuilder();
            bool timedOut = false;

            var stopwatch = Stopwatch.StartNew();

            using var process = new Process { StartInfo = psi, EnableRaisingEvents = true };

            // Subscribe to async data events BEFORE Start to avoid missing early output
            process.OutputDataReceived += (_, e) =>
            {
                if (e.Data is not null)
                {
                    onOutputLine?.Invoke(e.Data);
                    lock (stdoutBuilder) { stdoutBuilder.AppendLine(e.Data); }
                }
            };

            process.ErrorDataReceived += (_, e) =>
            {
                if (e.Data is not null)
                {
                    onErrorLine?.Invoke(e.Data);
                    lock (stderrBuilder) { stderrBuilder.AppendLine(e.Data); }
                }
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            if (!process.WaitForExit((int)effectiveTimeout.TotalMilliseconds))
            {
                timedOut = true;
                KillProcessTree(process);
            }

            // Second WaitForExit (no timeout) ensures async output handlers have flushed
            process.WaitForExit();

            stopwatch.Stop();

            return new ProcessResult
            {
                ExitCode = process.ExitCode,
                StandardOutput = stdoutBuilder.ToString().TrimEnd(),
                StandardError = stderrBuilder.ToString().TrimEnd(),
                TimedOut = timedOut,
                Elapsed = stopwatch.Elapsed
            };
        }

        /// <summary>
        /// Kills the process and its entire child process tree.
        /// </summary>
        private static void KillProcessTree(Process process)
        {
            try
            {
                process.Kill(entireProcessTree: true);
            }
            catch (InvalidOperationException)
            {
                // Process already exited between the timeout check and the kill call
            }
        }
    }
}
