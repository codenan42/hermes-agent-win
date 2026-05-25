from agent.redact import redact_sensitive_text

def test_redact_env_quoted_with_spaces():
    text = 'SECRET="my secret with spaces and more text"'
    redacted = redact_sensitive_text(text)
    # length 35 >= 18, so partial mask
    assert redacted == 'SECRET="my sec...text"'
    assert "my secret" not in redacted

def test_redact_env_unquoted():
    text = 'SECRET=mysecretpasswordthatisverylong'
    redacted = redact_sensitive_text(text)
    # length 29 >= 18
    assert redacted == 'SECRET=mysecr...long'

def test_redact_auth_quoted_with_spaces():
    text = 'Authorization: Bearer "token with spaces that is long enough"'
    redacted = redact_sensitive_text(text)
    # length 38 >= 18
    assert redacted == 'Authorization: Bearer "token ...ough"'
    assert "token with" not in redacted

def test_redact_auth_unquoted():
    text = 'Authorization: Bearer mysecrettokenthatisverylong'
    redacted = redact_sensitive_text(text)
    # length 33 >= 18
    assert redacted == 'Authorization: Bearer mysecr...long'

def test_redact_env_single_quoted():
    text = "SECRET='secret with spaces that is long enough'"
    redacted = redact_sensitive_text(text)
    assert redacted == "SECRET='secret...ough'"
