//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Batches file paths from multiple concurrent context-menu invocations into a
// single coordinator instance using a named mutex and a temporary batch file.
//------------------------------------------------------------------------------

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// When Windows Explorer calls our exe once per selected file, this class
    /// elects one coordinator instance that collects all file paths from the
    /// other (non-coordinator) instances.
    /// </summary>
    /// <remarks>
    /// <para>
    /// The first process to create the named mutex becomes the coordinator.
    /// It writes its own file path, waits for a short collection window so the
    /// other instances can append theirs, then reads and returns the full list.
    /// </para>
    /// <para>Non-coordinator instances append their file and exit immediately.</para>
    /// </remarks>
    internal static class ContextMenuFileBatcher
    {
        /// <summary>
        /// How long the coordinator waits for more files to accumulate (ms).
        /// </summary>
        private const int CollectionWindowMs = 800;

        /// <summary>
        /// Max retries when the batch file is locked by another instance.
        /// </summary>
        private const int FileWriteRetries = 20;

        /// <summary>
        /// Delay between file write retries (ms).
        /// </summary>
        private const int FileWriteRetryDelayMs = 50;

        /// <summary>
        /// Collects file paths from concurrent invocations that share the same batch key.
        /// </summary>
        /// <param name="batchKey">
        /// A key that groups invocations together (e.g., "markdown" or "convert_png").
        /// All instances using the same key are batched.
        /// </param>
        /// <param name="filePath">The file path from this invocation.</param>
        /// <returns>
        /// For the coordinator: a non-empty list of all collected file paths.
        /// For non-coordinators: an empty list (caller should exit).
        /// </returns>
        internal static List<string> CollectFiles(string batchKey, string filePath)
        {
            ArgumentNullException.ThrowIfNull(batchKey);
            ArgumentNullException.ThrowIfNull(filePath);

            string mutexName = $"Global\\MarkdownConverter_{batchKey}";
            string batchFilePath = Path.Combine(Path.GetTempPath(), $"MarkdownConverter_{batchKey}.batch");

            // Try to become the coordinator
            using var mutex = new Mutex(initiallyOwned: true, mutexName, out bool isCoordinator);

            // Always append our file (with retry for concurrent access)
            AppendLine(batchFilePath, filePath);

            if (!isCoordinator)
            {
                // Another instance is the coordinator — our file is queued, we can exit
                return [];
            }

            // We are the coordinator: wait for other instances to send their files
            Thread.Sleep(CollectionWindowMs);

            // Read all collected files
            List<string> files = ReadAndDelete(batchFilePath);

            // Release the mutex so a future batch can start fresh
            mutex.ReleaseMutex();

            return files;
        }

        private static void AppendLine(string path, string line)
        {
            for (int attempt = 0; attempt < FileWriteRetries; attempt++)
            {
                try
                {
                    using var stream = new FileStream(
                        path,
                        FileMode.Append,
                        FileAccess.Write,
                        FileShare.ReadWrite);

                    using var writer = new StreamWriter(stream);
                    writer.WriteLine(line);
                    return;
                }
                catch (IOException)
                {
                    Thread.Sleep(FileWriteRetryDelayMs);
                }
            }
        }

        private static List<string> ReadAndDelete(string path)
        {
            List<string> files = [];

            try
            {
                if (File.Exists(path))
                {
                    files = File.ReadAllLines(path)
                        .Where(line => !string.IsNullOrWhiteSpace(line))
                        .Distinct(StringComparer.OrdinalIgnoreCase)
                        .ToList();

                    File.Delete(path);
                }
            }
            catch (IOException)
            {
                // Best-effort cleanup; the temp file will be cleaned up eventually
            }

            return files;
        }
    }
}
