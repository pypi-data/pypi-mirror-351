from dnscheck import dns_info

def test_get_nameservers():
    result = dns_info.get_nameservers()
    assert isinstance(result, list)

def test_get_authoritative_dns():
    result = dns_info.get_authoritative_dns("google.com")
    assert isinstance(result, list)
