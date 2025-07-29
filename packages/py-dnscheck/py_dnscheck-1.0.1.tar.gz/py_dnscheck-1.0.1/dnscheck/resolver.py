import socket

from dnscheck.logger import logger

def resolve(domain):
    try:
        ip_list = socket.gethostbyname_ex(domain)[2]
        logger.info(f"Resolved domain {domain} to {ip_list}")
        return ip_list
    except socket.gaierror as e:
        logger.info(f"Failed to resolve domain {domain}: {e}")
        return []
