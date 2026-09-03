# Security Audit & OWASP Mobile Top 10 Hardening Report

## Security Audit Summary

| OWASP Mobile Top 10 Category | Implementation & Defense Mechanism |
| :--- | :--- |
| **M1: Improper Credential Usage** | API keys (Gemini) are strictly stored **server-side** in `.env` / Secret Manager. Never baked into APK. Client uses short-lived JWTs. |
| **M2: Inadequate Supply Chain Security** | Explicit dependency pinning in Gradle Version Catalog (`libs.versions.toml`) and Python `requirements.txt`. |
| **M3: Insecure Authentication / Authorization** | PBKDF2-SHA256 password hashing with random salt, JWT access/refresh token rotation, and multi-tier rate limiting per account, IP, and endpoint. |
| **M4: Insufficient Input / Output Validation** | Strict Pydantic v2 schemas, file magic-byte inspection, Zip-bomb / decompression bomb defense on DOCX/PPTX/XLSX, and Prompt Injection sandboxing (`prompt_guard.py`). |
| **M5: Insecure Communication** | Enforced HTTPS / TLS 1.3 with cleartext traffic disabled via Android `network_security_config.xml` and security headers on FastAPI (`nosniff`, `DENY`, `HSTS`, `CSP`). |
| **M6: Inadequate Privacy Controls** | Multi-layer Educational-aware PII Scrubber + Ephemeral Document Processing policy with automatic file shredding. |
| **M7: Insufficient Binary Protections** | R8 / ProGuard minification, resource shrinking, and debug symbol stripping in release builds. |
| **M8: Security Misconfiguration** | Disabled cleartext HTTP, blocked uncompressed ZIP expansions > 50MB, strict token budgeting caps (16,000 tokens/job). |
| **M9: Insecure Data Storage** | Android Keystore with `EncryptedSharedPreferences` (AES-256 SIV/GCM) and Room Database sandbox isolation. |
| **M10: Insufficient Cryptography** | Industry-standard AES-256, HMAC-SHA256, and TLS 1.3. No custom crypto. |
