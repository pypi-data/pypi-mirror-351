import argparse

from dnscheck import resolver, dns_info, reachablity
from dnscheck.logger import setup_logger

def main():
    DNSCHECK_DESCRIPTION = "A Python module and CLI tool to check DNS health, resolve domains, inspect and configure system DNS settings — made for sysadmins, developers, and network engineers \n\n  --> Resolve domains to IP addresses \n  --> Check DNS and network health with ping \n  --> Get system-configured DNS nameservers \n  --> Query authoritative DNS servers (NS records) \n  --> Change system DNS configuration (Linux only) \n\n  \tExample: \n \t* dnscheck [positional arguments] [domains] \n \t* dnscheck -v [positional arguments] [domains]"
    parser = argparse.ArgumentParser(description=DNSCHECK_DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (Note: Option only works after the command, not after the positional arguments)")

    subparsers = parser.add_subparsers(dest="command")

    parser_health = subparsers.add_parser("reachablity", help="Check domain reachablity with ping (default: dns.google.com)")
    parser_health.add_argument( "domain", nargs="?", default="dns.google.com", help="Optional domain (default: dns.google.com)")
    
    parser_resolve = subparsers.add_parser("resolve", help="Resolve a domain")
    parser_resolve.add_argument("domain", help="Domain to resolve")

    parser_ns = subparsers.add_parser("nameservers", help="Get system DNS nameservers")

    parser_auth = subparsers.add_parser("authoritative", help="Get authoritative DNS")
    parser_auth.add_argument("domain", help="Domain to query")

    parser_setdns = subparsers.add_parser("setdns", help="Set system DNS (Linux only)")
    parser_setdns.add_argument("dns", nargs="+", help="DNS IPs to set")

    args = parser.parse_args()

    setup_logger(verbose=args.verbose)

    if args.command == "reachablity":
        reachablity.check_dns_health(args.domain)
    elif args.command == "resolve":
        print(resolver.resolve(args.domain))
    elif args.command == "nameservers":
        print(dns_info.get_nameservers())
    elif args.command == "authoritative":
        print(dns_info.get_authoritative_dns(args.domain))
    elif args.command == "setdns":
        dns_info.set_dns(args.dns)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
