//------------------------------------------------------------------------------
// Project:  MarkdownConverter
// Author:   Terry, ChatGPT
// Date:     2025-03-19
// License:  MIT License (https://mit-license.org/)
//
// Description:
// Provides methods to hide or show the console window.
//
//------------------------------------------------------------------------------ 

using System.Runtime.InteropServices;

namespace MarkdownConverter.Helpers
{
    /// <summary>
    /// Provides helper methods to manipulate the console window visibility.
    /// </summary>
    static class ConsoleHelper
    {
        [DllImport("kernel32.dll")]
        static extern nint GetConsoleWindow();

        [DllImport("kernel32.dll")]
        static extern bool FreeConsole();

        [DllImport("kernel32.dll")]
        static extern bool AllocConsole();

        [DllImport("user32.dll")]
        static extern bool ShowWindow(nint hWnd, int nCmdShow);

        private const int SW_HIDE = 0;
        private const int SW_SHOW = 5;

        /// <summary>
        /// Hides the console window and detaches from the console entirely.
        /// This prevents any flash when the app is launched from Explorer.
        /// </summary>
        public static void HideConsole()
        {
            nint hWnd = GetConsoleWindow();
            if (hWnd != nint.Zero)
            {
                ShowWindow(hWnd, SW_HIDE);
            }

            FreeConsole();
        }

        /// <summary>
        /// Allocates and shows a console window.
        /// Required when OutputType is WinExe and console output is needed.
        /// </summary>
        public static void ShowConsole()
        {
            AllocConsole();
        }

        public static void WriteHeading(string heading, bool centerText = false, int size = 30)
        {
            var message = $"=== {heading} ===";

            WriteLine(message, centerText, size);
        }

        public static void WriteLine(string message, bool centerText = false, int size = 30)
        {
            if (centerText)
            {
                Console.WriteLine(message.PadLeft((size + message.Length) / 2));
            }
            else
            {
                Console.WriteLine(message);
            }
        }

        public static void WriteLink( string url)
        {
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine(url);
            Console.ResetColor();
        }
        public static void WriteSeparator(int size = 30)
        {
            Console.WriteLine(new string('-', size));
        }
    }
}
