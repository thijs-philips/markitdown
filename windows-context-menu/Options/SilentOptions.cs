using CommandLine;
namespace MarkdownConverter.Options
{
    /// <summary>
    /// Command-line options for running the application in silent mode.
    /// </summary>
    [Verb("silent", HelpText = "Run in silent mode")]
    class SilentOptions
    {
        [Option('s', "silent", Required = false, HelpText = "Run in silent mode")]
        public bool IsSilent { get; set; }
    }
}
