import sys, os, io, subprocess

CORE = r"D:\Github\markitdown\build_common"
sys.path.insert(0, CORE)
import markitdown_cli_core as m  # noqa: E402

print("import OK")
p = m._build_parser("(test)")
print("parser OK; prog =", p.prog)

# Exercise the helper that classifies unknown flags.
try:
    m._try_reassemble_path(None, ["--bogus"])
    print("FAIL: expected CliError for unknown flag")
except m.CliError as e:
    print("unknown-flag -> CliError OK:", str(e).splitlines()[0])

# Bad path suggestion
try:
    m._suggest_path_fix("?")
    print("FAIL: expected CliError for '?'")
except m.CliError as e:
    print("bad-path '?' -> CliError OK:", str(e).splitlines()[0])

print("ALL CORE CHECKS PASSED")
