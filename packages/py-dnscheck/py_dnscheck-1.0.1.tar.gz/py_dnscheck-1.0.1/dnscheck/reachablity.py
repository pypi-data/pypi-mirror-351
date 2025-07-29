import subprocess
import platform

from dnscheck.logger import logger

def check_dns_health(domain="dns.google.com"):
    try:
        if platform.system() == "Linux":
            ping_command = f"ping -c 3 {domain}"
        else:
            ping_command = f"ping {domain}"

        output = subprocess.run(ping_command, capture_output=True, shell=True)
        if output.returncode == 0:
            logger.info(f"{domain} is reachable")
            return True
        else:
            logger.info(f"{domain} is not reachable")
            return False
    except Exception as e:
        logger.info(f"Exception during domain reachablity: {e}")
        return False
