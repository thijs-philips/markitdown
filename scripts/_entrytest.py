# Drives the new entry.py through several scenarios, capturing exit codes.
import subprocess, sys, os, tempfile

PY = r"D:\Github\markitdown\build_nuitka\.venv\Scripts\python.exe"
if not os.path.isfile(PY):
    PY = sys.executable
ENTRY = r"D:\Github\markitdown\build_nuitka\entry.py"

def run(args, stdin=None):
    p = subprocess.run([PY, ENTRY] + args, input=stdin,
                       capture_output=True, text=True)
    return p.returncode, (p.stdout or "")[:200], (p.stderr or "")[:300]

# 1. version
print("== --version =="); print(run(["--version"]))
# 2. bare (no input, with a TTY this prints help; piped empty stdin here is treated as piped)
print("== no args, empty stdin =="); print(run([], stdin=""))
# 3. '?' as filename -> friendly file-not-found, no traceback
print("== '?' =="); print(run(["?"]))
# 4. unknown flag
print("== --bogus =="); print(run(["--bogus"]))
# 5. missing file
print("== nope.pdf =="); print(run(["nope.pdf"]))
# 6. --stdin reading html
print("== --stdin -x html =="); print(run(["--stdin", "-x", "html"],
      stdin="<h1>Hi</h1><p>Body <b>x</b></p>"))
# 7. real file
tmp = os.path.join(tempfile.gettempdir(), "entrytest.html")
open(tmp, "w", encoding="utf-8").write("<h1>File</h1><p>ok</p>")
print("== file =="); print(run([tmp]))
os.remove(tmp)
print("DONE")
