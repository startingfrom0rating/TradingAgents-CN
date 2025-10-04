# 🔧 Export Troubleshooting Guide

## 🎯 Overview

This document provides detailed solutions for common export problems in TradingAgents-CN, including exporting to Word, PDF, and Markdown formats, and troubleshooting steps for each.

## 📄 Word export issues

### Issue 1: YAML parse error

Error message:

```
Pandoc died with exitcode "64" during conversion: 
YAML parse exception at line 1, column 1,
while scanning an alias:
did not find expected alphabetic or numeric character
```

Cause analysis:

- Pandoc may treat certain Markdown table separators like `|------|------|` as part of a YAML block.
- Special characters can trigger YAML parser failures.

Fix:

```python
# This is already added in the codebase as an automatic remediation
extra_args = ['--from=markdown-yaml_metadata_block']  # disable YAML metadata parsing
```

Verification:

```bash
# Test Word export
docker exec TradingAgents-web python test_conversion.py
```

### Issue 2: Chinese characters display incorrectly

Symptoms:

- Chinese text in Word shows as blocks or garbled characters.
- Special characters (¥, %) display incorrectly.

Fixes:

1. Docker environment (recommended):

```bash
# Docker images usually include CJK fonts; no extra config required
docker-compose up -d
```
2. Local environment:

```bash
# Windows: ensure Chinese fonts are installed system-wide

# Linux
sudo apt-get install fonts-noto-cjk

# macOS: Chinese fonts are usually available by default
```

### Issue 3: Generated .docx file cannot be opened or is corrupted

Symptoms:

- The created .docx cannot be opened by Word
- The file size is zero or unusually small

Diagnostic steps:

```bash
# 1. Check where generated files are located
docker exec TradingAgents-web ls -la /app/test_*.docx

# 2. Verify pandoc is installed
docker exec TradingAgents-web pandoc --version

# 3. Run the conversion test
docker exec TradingAgents-web python test_conversion.py
```

Fix:

```bash
# Rebuild the Docker image
docker-compose down
docker build -t tradingagents-cn:latest . --no-cache
docker-compose up -d
```

## 📰 PDF export issues

### Issue 1: PDF engine missing

Error message:

```
PDF generation failed, last error: wkhtmltopdf not found
```

Fixes:

1. In Docker (recommended):

```bash
# Check PDF engines installed
docker exec TradingAgents-web wkhtmltopdf --version
docker exec TradingAgents-web weasyprint --version
```
2. Local environment:

```bash
# Windows
choco install wkhtmltopdf

# macOS
brew install wkhtmltopdf

# Linux
sudo apt-get install wkhtmltopdf
```

### Issue 2: PDF generation times out

Symptoms:

- The PDF generation process stalls and never completes.

Fix:

```python
# Increase execution timeout (configured in the codebase)
max_execution_time = 180  # 3 minutes
```

Temporary remedy:

```bash
# Restart the web service
docker-compose restart web
```

### Issue 3: Chinese text missing or layout broken in PDF

Symptoms:

- Chinese content appears blank or as blocks in the PDF
- Layout is distorted

Fix:

```bash
# Rebuild Docker image (Docker images include required fonts in recommended configuration)
docker build -t tradingagents-cn:latest . --no-cache
```

## 📝 Markdown export issues

### Issue 1: Special character conversions

Symptoms:

- Special characters (like &, <, >) appear incorrectly in exports
- Tables render incorrectly

Fix:

```python
# Automatic escaping of special characters (already implemented)
text = text.replace('&', '&')
text = text.replace('<', '<')
text = text.replace('>', '>')
```

### Issue 2: File encoding problems

Symptoms:

- Downloaded Markdown is garbled
- Chinese characters show incorrectly

Fix:

```python
# Ensure UTF-8 encoding (configured by default)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

## 🔎 Common troubleshooting steps

### Diagnostic tools

1. Conversion smoke tests:

```bash
# Basic conversion test
docker exec TradingAgents-web python test_conversion.py

# Test real-world report conversion
docker exec TradingAgents-web python test_real_conversion.py

# Test conversion of existing reports
docker exec TradingAgents-web python test_existing_reports.py
```
2. Check system status:

```bash
# Check containers
docker-compose ps

# Check logs
docker logs TradingAgents-web --tail 50

# Check disk space
docker exec TradingAgents-web df -h
```
3. Verify dependencies:

```bash
# Check Python packages
docker exec TradingAgents-web pip list | grep -E "(pandoc|docx|pypandoc)"

# Verify system tools
docker exec TradingAgents-web which pandoc
docker exec TradingAgents-web which wkhtmltopdf
```

### Environment reset

If the problem persists, try a full environment reset:

```bash
# 1. Stop all services
docker-compose down

# 2. Clean Docker resources
docker system prune -f

# 3. Rebuild images
docker build -t tradingagents-cn:latest . --no-cache

# 4. Start services
docker-compose up -d

# 5. Verify functionality
docker exec TradingAgents-web python test_conversion.py
```

### Performance tips

1. Memory limits:

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G  # increase memory limit
```
2. Clean temporary files:

```bash
# Remove temporary generated files
docker exec TradingAgents-web find /tmp -name "*.docx" -delete
docker exec TradingAgents-web find /tmp -name "*.pdf" -delete
```

## 📞 Collect logs for support

When reporting an issue, collect the following information:

1. Error logs:

```bash
docker logs TradingAgents-web --tail 100 > error.log
```
2. System info:

```bash
docker exec TradingAgents-web python --version
docker exec TradingAgents-web pandoc --version
docker --version
docker-compose --version
```
3. Test output:

```bash
docker exec TradingAgents-web python test_conversion.py > test_result.log 2>&1
```

### Common problems summary

| Issue type | Quick fix | Details |
| --- | --- | --- |
| YAML parse error | Restart web service | Check code for automatic YAML remediation |
| Missing PDF engine | Use Docker image | Install PDF engine manually if running locally |
| Chinese display | Use Docker image or install CJK fonts | Install fonts on local system |
| Corrupt files | Regenerate | Rebuild Docker image |
| Out of memory | Restart container | Increase memory limit |
| Network timeout | Check network | Increase timeouts |

### Preventative measures

1. Keep the repository updated:

```bash
git pull origin develop
docker-compose pull
```
2. Monitor resources:

```bash
docker stats TradingAgents-web
```
3. Backup configuration:

```bash
cp .env .env.backup
```

---

*Last updated: 2025-07-13*
*Version: v0.1.7*
