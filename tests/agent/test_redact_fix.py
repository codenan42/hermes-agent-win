from agent.redact import redact_sensitive_text

def test_redact_quoted_secret_with_spaces():
    text = 'MY_SECRET="this is a secret with spaces"'
    result = redact_sensitive_text(text)
    # The value "this is a secret with spaces" has length 28.
    # _mask_token("this is a secret with spaces") -> "this i...aces"
    assert "this is a secret with spaces" not in result
    assert 'MY_SECRET="this i...aces"' in result

def test_redact_single_quoted_secret_with_spaces():
    text = "ANOTHER_SECRET='single quoted secret'"
    result = redact_sensitive_text(text)
    # length 20 -> "single...cret"
    assert "single quoted secret" not in result
    assert "ANOTHER_SECRET='single...cret'" in result

def test_redact_unquoted_secret():
    text = "PASSWORD=mypassword123"
    result = redact_sensitive_text(text)
    # length 13 -> "***"
    assert "mypassword123" not in result
    assert "PASSWORD=***" in result

def test_redact_mixed_env_dump():
    env_dump = """
    HOME=/home/user
    MY_SECRET="this is a secret with spaces"
    OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012
    """
    result = redact_sensitive_text(env_dump)
    assert "HOME=/home/user" in result
    assert "this is a secret with spaces" not in result
    assert "abc123def456" not in result
