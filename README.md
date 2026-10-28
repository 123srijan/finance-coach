Finance Coach, its features, technologies, setup steps, and required environment variables. Never put real passwords or API keys there.

## Run

From this folder:

```powershell
python main.py < input.txt
```

Paste a sample input into `input.txt`. For interactive problems, run `python main.py` directly in the terminal instead of redirecting input.

In VS Code, open this folder and use **Run contest solution** from the Run and Debug panel. The starter uses `sys.stdin.buffer` for fast input; put your solution logic in `solve()`.

## Environment

- Python 3.15 is available on this machine; no third-party packages are required.
- No C++ compiler or Java/Go/Rust toolchain was detected, so this workspace currently targets Python.
- The contest judge's supported language versions may differ from your local version. Use only features supported by the judge.
