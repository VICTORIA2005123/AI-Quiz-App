import re
from typing import Tuple, List, Set, Dict

# Known educational & scientific entities to protect from accidental redaction
EDUCATIONAL_WHITELIST: Set[str] = {
    "albert einstein", "isaac newton", "marie curie", "charles darwin", "alan turing",
    "aristotle", "plato", "socrates", "nikola tesla", "galileo galilei", "louis pasteur",
    "ada lovelace", "richard feynman", "stephen hawking", "niels bohr", "max planck",
    "gregor mendel", "james watson", "francis crick", "rosalind franklin",
    "mitochondria", "photosynthesis", "dna polymerase", "pythagorean theorem",
    "newton's laws", "theory of relativity", "quantum mechanics", "cellular respiration",
    "glycolysis", "citric acid cycle", "krebs cycle", "endoplasmic reticulum",
    "chloroplast", "ribosome", "golgi apparatus", "central dogma",
    "google inc", "apple inc", "microsoft corp", "amazon com", "ibm", "meta platforms"
}

# Regex patterns for personal private identifiers
PII_REGEX_PATTERNS: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "API_KEY": re.compile(r"\b(?:sk-[a-zA-Z0-9]{32,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})\b"),
    "JWT_TOKEN": re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"),
}


class EducationalAwarePIIScrubber:
    """
    Multi-layer privacy engine:
    1. Redacts sensitive personal information (Emails, Phones, SSNs, Credit Cards, Secrets)
    2. Enforces configurable sensitive-term blacklist
    3. Preserves educational, historical, scientific, and academic entities
    """
    def __init__(self, custom_sensitive_terms: List[str] = None):
        self.custom_sensitive_terms = [term.lower().strip() for term in (custom_sensitive_terms or []) if term.strip()]

    def scrub(self, text: str) -> Tuple[str, Dict[str, int]]:
        if not text:
            return "", {}

        stats: Dict[str, int] = {k: 0 for k in PII_REGEX_PATTERNS.keys()}
        stats["CUSTOM_TERMS"] = 0
        scrubbed = text

        # 1. Redact API keys & JWTs first (high sensitivity)
        for key_type in ["API_KEY", "JWT_TOKEN"]:
            pattern = PII_REGEX_PATTERNS[key_type]
            matches = pattern.findall(scrubbed)
            if matches:
                stats[key_type] += len(matches)
                scrubbed = pattern.sub(f"[REDACTED_{key_type}]", scrubbed)

        # 2. Redact SSNs and Credit Cards
        for key_type in ["SSN", "CREDIT_CARD"]:
            pattern = PII_REGEX_PATTERNS[key_type]
            matches = pattern.findall(scrubbed)
            if matches:
                stats[key_type] += len(matches)
                scrubbed = pattern.sub(f"[REDACTED_{key_type}]", scrubbed)

        # 3. Redact Emails (excluding educational whitelist domains if any)
        emails = PII_REGEX_PATTERNS["EMAIL"].findall(scrubbed)
        if emails:
            stats["EMAIL"] += len(emails)
            scrubbed = PII_REGEX_PATTERNS["EMAIL"].sub("[REDACTED_EMAIL]", scrubbed)

        # 4. Redact Phone numbers
        phones = PII_REGEX_PATTERNS["PHONE"].findall(scrubbed)
        if phones:
            stats["PHONE"] += len(phones)
            scrubbed = PII_REGEX_PATTERNS["PHONE"].sub("[REDACTED_PHONE]", scrubbed)

        # 5. Redact IP addresses (excluding common loopback/local)
        def replace_ip(match):
            ip = match.group(0)
            if ip in {"127.0.0.1", "0.0.0.0"}:
                return ip
            stats["IP_ADDRESS"] += 1
            return "[REDACTED_IP]"

        scrubbed = PII_REGEX_PATTERNS["IP_ADDRESS"].sub(replace_ip, scrubbed)

        # 6. Redact custom confidential project terms
        for term in self.custom_sensitive_terms:
            if term.lower() not in EDUCATIONAL_WHITELIST:
                term_pattern = re.compile(re.escape(term), re.IGNORECASE)
                matches = term_pattern.findall(scrubbed)
                if matches:
                    stats["CUSTOM_TERMS"] += len(matches)
                    scrubbed = term_pattern.sub("[CONFIDENTIAL_TERM]", scrubbed)

        return scrubbed, stats


pii_scrubber = EducationalAwarePIIScrubber()
