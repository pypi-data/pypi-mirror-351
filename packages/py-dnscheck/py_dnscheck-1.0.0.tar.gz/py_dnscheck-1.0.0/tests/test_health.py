from dnscheck import health

def test_check_dns_health():
    result = health.check_dns_health("google.com")
    assert isinstance(result, bool)
