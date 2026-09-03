# Privacy Policy: AI Quiz Master

**Last Updated:** August 30, 2026

## 1. Introduction
AI Quiz Master ("we", "our", or "the App") is committed to protecting your privacy. This Privacy Policy explains how our native Android application and FastAPI backend handle your documents and data.

## 2. Ephemeral Document Processing Policy
- **No Document Retention:** When you upload documents (PDF, DOCX, PPTX, XLSX, CSV, TXT, MD, HTML, or images) to generate a quiz, the document is transmitted via encrypted HTTPS/TLS 1.3 to our secure backend.
- **In-Memory & Ephemeral Storage:** The document content is held strictly in temporary memory solely for the duration of the parsing, chunking, and AI quiz generation process.
- **Immediate Destruction:** Once the quiz questions and source citations are generated, all temporary files and raw document texts are immediately and securely shredded from our servers.
- **Zero Persistent Storage of Uploaded Text:** Our persistent database only stores your account email, usage quotas, quiz titles, and generated quiz questions. Raw document text is never stored.

## 3. Educational-Aware PII Redaction
Before any document chunk is submitted to the AI generator, our multi-layer PII scrubber automatically identifies and redacts personal identifiable information including emails, phone numbers, Social Security Numbers, credit cards, and private API keys, while strictly preserving educational, scientific, and academic terms.

## 4. Grounded AI & Transparency
Our AI generation pipeline requires that all quiz questions cite exact quotes from the provided document chunks. We do not use your private study documents to train foundation AI models.

## 5. Security & Device Storage
- On Android devices, credentials and study preferences are secured using **Android Keystore (AES-256 GCM)**.
- Quizzes saved locally are stored in a private **Room Database** accessible only by the application sandbox.
- Users can optionally enable **Biometric App Lock** to require fingerprint or face unlock before viewing saved quizzes.
