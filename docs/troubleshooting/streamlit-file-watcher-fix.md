# Streamlit File-Watcher Issue — Fix and Workarounds

## Problem description

When running the Streamlit web app, you may encounter exceptions from the file-watcher (watchdog) thread similar to:

```
Exception in thread Thread-9:
Traceback (most recent call last):
  File ".../lib/threading.py", line 1016, in _bootstrap_inner
    self.run()
  File ".../site-packages/watchdog/observers/api.py", line 213, in run
    self.dispatch_events(self.event_queue)
  ...
FileNotFoundError: [Errno 2] The system cannot find the file specified: '.../web/pages/__pycache__/config_management.cpython-310.pyc.2375409084592'
```

## Root causes

1. Python bytecode cache files: Python creates `.pyc` files under `__pycache__` while modules are imported.
2. Temporary filename patterns: Python may create temporary files with randomized suffixes.
3. Streamlit's watchdog attempts to monitor these transient files and may race with file deletion or renaming.
4. Race condition leads to FileNotFoundError when watchdog accesses files that were removed.

## Fixes

### Fix 1: Configure Streamlit file watcher (recommended)

Create or update `.streamlit/config.toml` with the following to exclude `__pycache__` and compiled files:

```toml
[server.fileWatcher]
# Use auto watcher; adjust if needed
watcherType = "auto"
# Exclude __pycache__ and compiled files
excludePatterns = [
  "**/__pycache__/**",
  "**/*.pyc",
  "**/*.pyo",
  "**/*.pyd",
  "**/.git/**",
  "**/node_modules/**",
  "**/.env",
  "**/venv/**",
  "**/env/**"
]
```

### Fix 2: Clean up cache files regularly

Remove Python cache directories from the project periodically:

```bash
# Windows PowerShell
Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force

# Linux/macOS
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### Fix 3: Prevent writing bytecode in some environments

Set the environment variable to disable writing `.pyc` files:

```bash
# Add to .env
PYTHONDONTWRITEBYTECODE=1
```

Or set it at runtime:

```python
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
```

## Validation steps

1. Restart Streamlit app:

```bash
python web/run_web.py
```

2. Verify `.streamlit/config.toml` is present and effective.
3. Check the logs for FileNotFoundError occurrences.

## Prevention

1. Keep `.gitignore` updated to include `__pycache__/` and `*.pyc`.
2. Periodically clean cache directories in development environments.
3. Configure Streamlit to ignore temporary and compiled files rather than disabling the watcher completely.

## References

- Streamlit configuration: https://docs.streamlit.io/library/advanced-features/configuration
- Python compiled files explanation: https://docs.python.org/3/tutorial/modules.html#compiled-python-files
- Watchdog documentation: https://python-watchdog.readthedocs.io/

*Last updated: 2025-07-03*