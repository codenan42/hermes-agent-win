from agent.redact import redact_sensitive_text

def test_quoted_value_with_spaces():
    # This currently fails: it only masks up to the first space
    text = 'MY_PASSWORD="secret password with spaces"'
    result = redact_sensitive_text(text)
    assert 'secret password' not in result
    assert result == 'MY_PASSWORD="***"' or result == 'MY_PASSWORD="secret...aces"'

def test_single_quoted_value_with_spaces():
    text = "MY_PASSWORD='secret password with spaces'"
    result = redact_sensitive_text(text)
    assert 'secret password' not in result
    assert result == "MY_PASSWORD='***'" or result == "MY_PASSWORD='secret...aces'"

def test_unquoted_value():
    text = "MY_PASSWORD=secretpassword123"
    result = redact_sensitive_text(text)
    assert "secretpassword123" not in result
    assert "MY_PASSWORD=***" in result
