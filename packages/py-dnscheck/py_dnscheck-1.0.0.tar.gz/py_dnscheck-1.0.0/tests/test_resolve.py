from dnscheck import resolve

def test_resolve_valid():
    result = resolve.resolve("google.com")
    assert isinstance(result, list)
    assert result

def test_resolve_invalid():
    result = resolve.resolve("nonexistentdomain.abcxyz")
    assert result == []
