import dns.resolver
import os
import platform

from dnscheck.logger import logger

def get_nameservers():
    try:
        res = dns.resolver.Resolver()
        ns = res.nameservers
        logger.info(f"Current system nameservers: {ns}")
        return ns
    except Exception as e:
        logger.error(f"Error fetching nameservers: {e}")
        return []

def get_authoritative_dns(domain):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        ns_list = [rdata.to_text() for rdata in answers]
        logger.info(f"Authoritative DNS for {domain}: {ns_list}")
        return ns_list
    except Exception as e:
        logger.error(f"Error getting NS records for {domain}: {e}")
        return []

def set_dns(dns_list):
    try:
        if platform.system() == "Linux":
            resolv_conf = "/etc/resolv.conf"
            with open(resolv_conf, "w") as f:
                for dns_server in dns_list:
                    f.write(f"nameserver {dns_server}")
            logger.info(f"Updated DNS servers to {dns_list}")
            return True
        else:
            logger.warning("Setting DNS is currently supported only on Linux.")
            return False
    except Exception as e:
        logger.error(f"Failed to set DNS servers: {e}")
        return False
