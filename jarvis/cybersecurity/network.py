"""
Capability 51: Network Inventory (Authorized Local Interface Scanning)
Enumerates network interfaces, addresses, ARP cache entries, and performs
safe, non-destructive port and service discovery within authorized IP scopes.
"""

import socket
import subprocess
import platform
import re
import ipaddress
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class NetworkInterfaceInfo:
    name: str
    ip_addresses: List[str]
    mac_address: Optional[str]
    is_up: bool


@dataclass
class DiscoveredPort:
    port: int
    protocol: str
    service_name: str
    state: str  # OPEN, CLOSED, FILTERED
    banner: Optional[str] = None


@dataclass
class HostInventory:
    target_ip: str
    hostname: Optional[str]
    is_alive: bool
    open_ports: List[DiscoveredPort] = field(default_factory=list)


class NetworkInventoryScanner:
    """Discovers network interfaces and audits authorized network hosts and ports."""

    WELL_KNOWN_SERVICES = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        135: "MS-RPC",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        1433: "MSSQL",
        1521: "Oracle",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt",
    }

    # Strict authorization guardrails: Only loopback and standard RFC1918 private subnets allowed by default
    ALLOWED_DEFAULT_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("::1/128"),
    ]

    def __init__(self, additional_authorized_networks: Optional[List[str]] = None):
        self.authorized_networks = list(self.ALLOWED_DEFAULT_NETWORKS)
        if additional_authorized_networks:
            for net in additional_authorized_networks:
                self.authorized_networks.append(ipaddress.ip_network(net))

    def is_target_authorized(self, ip_str: str) -> bool:
        """Verifies if a target IP address falls strictly within authorized scope."""
        try:
            target_ip = ipaddress.ip_address(ip_str)
            return any(target_ip in net for net in self.authorized_networks)
        except ValueError:
            return False

    def get_local_interfaces(self) -> List[NetworkInterfaceInfo]:
        """Gathers local host network interfaces and bound IP addresses."""
        interfaces: List[NetworkInterfaceInfo] = []
        try:
            hostname = socket.gethostname()
            # Get all IP addresses resolved for hostname
            addrs = socket.gethostbyname_ex(hostname)[2]
            interfaces.append(
                NetworkInterfaceInfo(
                    name=hostname,
                    ip_addresses=addrs,
                    mac_address=None,
                    is_up=True,
                )
            )
        except Exception:
            pass

        # Loopback interface
        interfaces.append(
            NetworkInterfaceInfo(
                name="loopback",
                ip_addresses=["127.0.0.1", "::1"],
                mac_address="00:00:00:00:00:00",
                is_up=True,
            )
        )

        # Parse ipconfig on Windows if available
        if platform.system() == "Windows":
            try:
                res = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=3)
                if res.returncode == 0:
                    current_adapter = None
                    adapter_ips: List[str] = []
                    for line in res.stdout.splitlines():
                        line = line.strip()
                        if "adapter" in line.lower() and ":" in line:
                            if current_adapter and adapter_ips:
                                interfaces.append(
                                    NetworkInterfaceInfo(
                                        name=current_adapter,
                                        ip_addresses=adapter_ips,
                                        mac_address=None,
                                        is_up=True,
                                    )
                                )
                            current_adapter = line.rstrip(":")
                            adapter_ips = []
                        elif "ipv4" in line.lower():
                            m = re.search(r":\s*([\d\.]+)", line)
                            if m:
                                adapter_ips.append(m.group(1))
                    if current_adapter and adapter_ips:
                        interfaces.append(
                            NetworkInterfaceInfo(
                                name=current_adapter,
                                ip_addresses=adapter_ips,
                                mac_address=None,
                                is_up=True,
                            )
                        )
            except Exception:
                pass

        return interfaces

    def get_arp_cache(self) -> List[Dict[str, str]]:
        """Parses the local ARP cache for active neighborhood IP-to-MAC associations."""
        entries: List[Dict[str, str]] = []
        try:
            res = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 3 and re.match(r"^\d+\.\d+\.\d+\.\d+$", parts[0]):
                        entries.append({
                            "ip": parts[0],
                            "mac": parts[1],
                            "type": parts[2],
                        })
        except Exception:
            pass
        return entries

    def probe_port(self, target_ip: str, port: int, timeout: float = 0.3) -> DiscoveredPort:
        """Safely probes a single TCP port using a standard connect handshake."""
        service_name = self.WELL_KNOWN_SERVICES.get(port, "Unknown")
        banner = None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                state = "OPEN"
                # Non-destructive banner grab for HTTP or text protocols
                try:
                    if port in [80, 8080]:
                        sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                        raw_resp = sock.recv(256).decode("latin-1", errors="ignore")
                        first_line = raw_resp.split("\r\n")[0]
                        banner = first_line.strip()
                    elif port in [21, 22, 25]:
                        raw_resp = sock.recv(128).decode("latin-1", errors="ignore")
                        banner = raw_resp.strip()
                except Exception:
                    pass
            else:
                state = "CLOSED"
        except Exception:
            state = "FILTERED"
        finally:
            sock.close()

        return DiscoveredPort(
            port=port,
            protocol="TCP",
            service_name=service_name,
            state=state,
            banner=banner,
        )

    def scan_host(self, target_ip: str, ports: List[int], timeout: float = 0.2) -> HostInventory:
        """Audits authorized host for active open ports."""
        if not self.is_target_authorized(target_ip):
            raise PermissionError(
                f"Scope Violation: Target IP '{target_ip}' is outside authorized network range. "
                "Penetration and port scanning without authorization is strictly prohibited."
            )

        open_ports: List[DiscoveredPort] = []
        for port in ports:
            p_res = self.probe_port(target_ip, port, timeout=timeout)
            if p_res.state == "OPEN":
                open_ports.append(p_res)

        try:
            hostname = socket.gethostbyaddr(target_ip)[0]
        except Exception:
            hostname = None

        return HostInventory(
            target_ip=target_ip,
            hostname=hostname,
            is_alive=len(open_ports) > 0,
            open_ports=open_ports,
        )
