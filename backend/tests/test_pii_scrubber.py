from app.services.pii_scrubber import EducationalAwarePIIScrubber, pii_scrubber


def test_redact_personal_identifiers():
    sample_text = (
        "Student Contact: john.doe@university.edu or call +1-555-432-8765. "
        "SSN: 123-45-6789, Credit Card: 4111-2222-3333-4444. "
        "Developer key: sk-abcdef1234567890abcdef1234567890."
    )
    scrubbed, stats = pii_scrubber.scrub(sample_text)

    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed
    assert "[REDACTED_SSN]" in scrubbed
    assert "[REDACTED_CREDIT_CARD]" in scrubbed
    assert "[REDACTED_API_KEY]" in scrubbed
    assert "john.doe@university.edu" not in scrubbed
    assert "123-45-6789" not in scrubbed


def test_preserve_educational_entities():
    academic_text = (
        "Albert Einstein proposed the theory of relativity in 1905. "
        "Photosynthesis in plants occurs within the chloroplast, where light energy is converted into chemical energy. "
        "Isaac Newton formulated the three laws of motion."
    )
    scrubbed, stats = pii_scrubber.scrub(academic_text)

    # Ensure educational concepts remain completely unredacted
    assert "Albert Einstein" in scrubbed
    assert "theory of relativity" in scrubbed
    assert "Photosynthesis" in scrubbed
    assert "chloroplast" in scrubbed
    assert "Isaac Newton" in scrubbed
    assert "laws of motion" in scrubbed


def test_custom_confidential_terms():
    scrubber = EducationalAwarePIIScrubber(custom_sensitive_terms=["Project Titan", "SecretXCodename"])
    text = "Under Project Titan, we analyzed cell division. Also SecretXCodename was tested."
    scrubbed, stats = scrubber.scrub(text)

    assert "[CONFIDENTIAL_TERM]" in scrubbed
    assert "Project Titan" not in scrubbed
    assert "SecretXCodename" not in scrubbed
    assert "cell division" in scrubbed
