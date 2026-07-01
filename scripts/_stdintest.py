import subprocess, sys, os, tempfile

PY = r"D:\Github\markitdown\build_nuitka\.venv\Scripts\python.exe"
ENTRY = r"D:\Github\markitdown\build_nuitka\entry.py"

html = b"<h1>Hi</h1><p>Body <b>x</b> and <a href='https://x.com'>link</a></p>"

# A) pipe raw bytes via --stdin -x html
p = subprocess.run([PY, ENTRY, "--stdin", "-x", "html"], input=html,
                   capture_output=True)
print("A stdin -x html: rc=", p.returncode)
print("  stdout=", p.stdout)
print("  stderr=", p.stderr)

# B) file redirect equivalent: write file, feed via stdin
tmp = os.path.join(tempfile.gettempdir(), "redir.html")
open(tmp, "wb").write(html)
with open(tmp, "rb") as f:
    p = subprocess.run([PY, ENTRY, "--stdin", "-x", "html"], stdin=f,
                       capture_output=True)
print("B redirect: rc=", p.returncode)
print("  stdout=", p.stdout)
print("  stderr=", p.stderr)
os.remove(tmp)
