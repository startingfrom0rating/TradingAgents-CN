# ⚠️ Web Application Startup Troubleshooting Guide

## 🚨 Common issues

### 1. ModuleNotFoundError: No module named 'tradingagents'

Description:

```
ModuleNotFoundError: No module named 'tradingagents'
```

Cause: The project package isn't installed into the Python environment, so Python cannot import the module.

Solutions:

Option A — Install in editable mode (recommended for development):

```bash
# 1. Activate virtual environment
# Windows
.\env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 2. Install the project into the venv
pip install -e .

# 3. Start the web app
python start_web.py
```

Option B — Use the one‑click installer script:

```bash
# 1. Activate venv
.\env\Scripts\activate  # Windows

# 2. Run the installer script
python scripts/install_and_run.py
```

Option C — Add project root to PYTHONPATH (quick workaround):

```bash
# Windows
set PYTHONPATH=%CD%;%PYTHONPATH%
streamlit run web/app.py

# Linux/macOS
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run web/app.py
```

### 2. ModuleNotFoundError: No module named 'streamlit'

Description:

```
ModuleNotFoundError: No module named 'streamlit'
```

Fix:

```bash
# Install Streamlit and related packages
pip install streamlit plotly altair

# Or install the full web dependencies
pip install -r requirements_web.txt
```

### 3. Virtual environment issues

Description: It's unclear whether the code is running inside the intended virtual environment.

Checks:

```bash
# Check Python prefix
python -c "import sys; print(sys.prefix)"

# Check if running in a venv
python -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"
```

Fix:

```bash
# Create a venv if missing
python -m venv env

# Activate it
# Windows
.\env\Scripts\activate
# Linux/macOS
source env/bin/activate
```

### 4. Port already in use

Description:

```
OSError: [Errno 48] Address already in use
```

Fixes:

```bash
# Option 1: Run on a different port
streamlit run web/app.py --server.port 8502

# Option 2: Kill the process occupying the port
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

### 5. Permission issues

Description: Permission denied errors on some systems.

Fix:

```bash
# Ensure scripts are executable
chmod +x start_web.py
chmod +x web/run_web.py

# Or run with Python explicitly
python start_web.py
```

## 🛠️ Startup method comparison

| Startup method | Pros | Cons | Recommendation |
|---|---:|---|---:|
| `python start_web.py` | Simple; handles path setup | Requires project root | ⭐⭐⭐⭐⭐ |
| `pip install -e . && streamlit run web/app.py` | Standard, stable | Requires install step | ⭐⭐⭐⭐ |
| `python web/run_web.py` | Full features; includes checks | Might require extra imports | ⭐⭐⭐ |
| `PYTHONPATH=. streamlit run web/app.py` | No install required | Slightly more environment setup | ⭐⭐ |

## 🔍 Diagnostic tools

### Environment check script

```bash
# Run environment checks
python scripts/check_api_config.py
```

### Manual checks (quick)

```python
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("In virtualenv:", hasattr(sys, 'real_prefix'))

try:
    import tradingagents
    print("✅ tradingagents module import OK")
except ImportError as e:
    print("❌ tradingagents not importable:", e)

try:
    import streamlit
    print("✅ streamlit import OK")
except ImportError as e:
    print("❌ streamlit not importable:", e)
```

## ✅ Pre-start checklist

- [ ] Virtual environment activated
- [ ] Python >= 3.10
- [ ] Project installed (`pip install -e .`)
- [ ] Streamlit installed
- [ ] `.env` configured
- [ ] Port 8501 available

## Start recommendation

```bash
# Recommended start method
python start_web.py
```

## After start verification

- [ ] Open http://localhost:8501 in the browser
- [ ] UI loads without errors
- [ ] Sidebar configuration appears
- [ ] You can select analyst and stock symbol

## 📞 Get help

If the above steps don't resolve the issue:

1. Collect startup logs:

```bash
python start_web.py 2>&1 | tee startup.log
```

2. Check environment details:

```bash
python --version
pip list | grep -E "(streamlit|tradingagents)"
```

3. Reinstall:

```bash
pip uninstall tradingagents
pip install -e .
```

4. Open an Issue on GitHub and include logs and environment details.
