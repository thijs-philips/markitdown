# markitdown (staging folder)

This folder is **populated by the build pipeline** — it is intentionally empty in
source control (except for this README).

Stage 2 of the build (`scripts/integrate-engine.ps1`) copies the frozen/compiled
MarkItDown engine here:

```
markitdown/
  markitdown.exe        # the standalone engine
  _internal/  (PyInstaller)   OR   *.dll / *.pyd / data dirs (Nuitka)
```

At publish time, `MarkdownConverter.csproj` copies everything under
`markitdown\**` next to the app, and `MarkitdownHelper` invokes
`markitdown\markitdown.exe` at runtime.

Do not edit the staged files by hand — re-run the integrate step instead.
