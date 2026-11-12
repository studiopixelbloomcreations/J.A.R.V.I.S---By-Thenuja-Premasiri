"""
Capability 116: Local Network Dashboard
Discovers local network interfaces, gateway/DNS, ARP table hosts,
measures latency/throughput, and provides comprehensive network diagnostics.
"""

import os
import re
import socket
import subprocess
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class NetworkInterface:
    name: str
    ip_addresses: List[str] = field(default_factory=list)
    ipv6_addresses: List[str] = field(default_factory=list)
    mac_address: Optional[str] = None
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    is_up: bool = True
    speed_mbps: int = 0
    mtu: int = 1500


@dataclass
class NetworkHost:
    ip: str
    mac: str = "Unknown"
    hostname: str = "Unknown"
    latency_ms: Optional[float] = None
    status: str = "unknown"
    interface: str = "unknown"


@dataclass
class NetworkThroughput:
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    errin: int = 0
    errout: int = 0
    dropin: int = 0
    dropout: int = 0
    upload_kbps: float = 0.0
    download_kbps: float = 0.0


class LocalNetworkDashboard:
    """Dashboard and monitor for local network interfaces, hosts, and throughput."""

    def __init__(self):
        self._last_io = None
        self._last_io_time = None
        self._initialize_baseline_io()

    def _initialize_baseline_io(self):
        if psutil:
            try:
                self._last_io = psutil.net_io_counters()
                self._last_io_time = time.time()
            except Exception:
                self._last_io = None

    def get_interfaces(self) -> List[NetworkInterface]:
        """Discovers and parses all active local network interfaces."""
        interfaces: List[NetworkInterface] = []
        if not psutil:
            # Fallback to socket hostname resolution
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                interfaces.append(NetworkInterface(name="default", ip_addresses=[ip], is_up=True))
            except Exception:
                interfaces.append(NetworkInterface(name="loopback", ip_addresses=["127.0.0.1"], is_up=True))
            return interfaces

        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
        except Exception:
            return interfaces

        for iface_name, addr_list in addrs.items():
            stat = stats.get(iface_name)
            is_up = stat.isup if stat else True
            speed = stat.speed if stat else 0
            mtu = stat.mtu if stat else 1500

            iface = NetworkInterface(
                name=iface_name,
                is_up=is_up,
                speed_mbps=speed,
                mtu=mtu,
            )

            for addr in addr_list:
                family = getattr(addr, 'family', None)
                # AF_INET for IPv4
                if family == socket.AF_INET:
                    if addr.address:
                        iface.ip_addresses.append(addr.address)
                    if addr.netmask:
                        iface.netmask = addr.netmask
                    if addr.broadcast:
                        iface.broadcast = addr.broadcast
                # AF_INET6 for IPv6
                elif hasattr(socket, 'AF_INET6') and family == socket.AF_INET6:
                    if addr.address:
                        # Strip interface scope if present (e.g. fe80::...%12)
                        cleaned_v6 = addr.address.split('%')[0]
                        iface.ipv6_addresses.append(cleaned_v6)
                # MAC address (often AF_LINK or represented as raw string with colons/dashes)
                elif hasattr(psutil, 'AF_LINK') and family == psutil.AF_LINK:
                    if addr.address:
                        iface.mac_address = addr.address
                elif addr.address and (":" in addr.address or "-" in addr.address) and len(addr.address) in (17, 14):
                    iface.mac_address = addr.address

            interfaces.append(iface)

        return interfaces

    def get_gateway_and_dns(self) -> Dict[str, Any]:
        """Inspects default gateway, DNS resolvers, and primary host address."""
        info = {
            "hostname": socket.gethostname(),
            "local_ip": "127.0.0.1",
            "gateway": None,
            "dns_servers": [],
        }

        # Resolve local IP via outbound route probe without sending packets
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                info["local_ip"] = socket.gethostbyname(info["hostname"])
            except Exception:
                pass

        # Parse gateway from route or ipconfig on Windows
        try:
            out = subprocess.check_output("ipconfig", text=True, stderr=subprocess.DEVNULL, timeout=2)
            gw_matches = re.findall(r"Default Gateway[ .:]+([\d\.]+)", out)
            if gw_matches:
                info["gateway"] = gw_matches[0]
            dns_matches = re.findall(r"DNS Servers[ .:]+([\d\.]+)", out)
            if dns_matches:
                info["dns_servers"] = list(set(dns_matches))
        except Exception:
            # Fallback estimation for gateway
            parts = info["local_ip"].split(".")
            if len(parts) == 4 and parts[0] != "127":
                info["gateway"] = f"{parts[0]}.{parts[1]}.{parts[2]}.1"

        return info

    def scan_arp_cache(self) -> List[NetworkHost]:
        """Parses local ARP table cache to identify discovered network hosts."""
        hosts: List[NetworkHost] = []
        try:
            out = subprocess.check_output(["arp", "-a"], text=True, stderr=subprocess.DEVNULL, timeout=3)
            current_iface = "default"
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Windows Interface header
                if line.startswith("Interface:"):
                    match = re.search(r"Interface:\s*([\d\.]+)", line)
                    if match:
                        current_iface = match.group(1)
                    continue

                # Match IP and MAC address pairs
                match = re.search(r"([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})\s+([0-9a-fA-F\:\-]+)\s+(\w+)", line)
                if match:
                    ip, mac, entry_type = match.groups()
                    # Filter out multicast/broadcast ranges
                    if ip.startswith("224.") or ip.endswith(".255") or ip == "255.255.255.255":
                        continue
                    hosts.append(NetworkHost(
                        ip=ip,
                        mac=mac.replace("-", ":").lower(),
                        status="reachable",
                        interface=current_iface,
                    ))
        except Exception:
            pass

        # Ensure local IP is included
        gw_info = self.get_gateway_and_dns()
        local_ip = gw_info.get("local_ip", "127.0.0.1")
        if not any(h.ip == local_ip for h in hosts):
            hosts.append(NetworkHost(ip=local_ip, mac="00:00:00:00:00:00", status="online", interface="local"))

        return hosts

    def ping_host(self, host: str, port: int = 80, timeout: float = 1.0) -> Dict[str, Any]:
        """
        Measures network reachability and round-trip latency in milliseconds.
        Uses TCP connect socket probe (firewall friendly and non-privileged).
        """
        start = time.perf_counter()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            # 0 = Connected, 10061/111 = Connection refused (still reachable host!)
            reachable = (result == 0 or result in (10061, 111))
            return {
                "host": host,
                "port": port,
                "reachable": reachable,
                "latency_ms": round(elapsed_ms, 2) if reachable else None,
                "errno": result,
                "status": "online" if reachable else "offline"
            }
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "reachable": False,
                "latency_ms": None,
                "error": str(e),
                "status": "offline"
            }

    def get_throughput_metrics(self, sample_interval: float = 0.05) -> NetworkThroughput:
        """Calculates live I/O throughput rates in kbps."""
        if not psutil:
            return NetworkThroughput()

        try:
            curr_io = psutil.net_io_counters()
            curr_time = time.time()
        except Exception:
            return NetworkThroughput()

        upload_kbps = 0.0
        download_kbps = 0.0

        if self._last_io and self._last_io_time:
            dt = curr_time - self._last_io_time
            if dt > 0:
                bytes_sent_delta = curr_io.bytes_sent - self._last_io.bytes_sent
                bytes_recv_delta = curr_io.bytes_recv - self._last_io.bytes_recv
                upload_kbps = (bytes_sent_delta * 8.0) / (dt * 1024.0)
                download_kbps = (bytes_recv_delta * 8.0) / (dt * 1024.0)

        self._last_io = curr_io
        self._last_io_time = curr_time

        return NetworkThroughput(
            bytes_sent=curr_io.bytes_sent,
            bytes_recv=curr_io.bytes_recv,
            packets_sent=curr_io.packets_sent,
            packets_recv=curr_io.packets_recv,
            errin=curr_io.errin,
            errout=curr_io.errout,
            dropin=curr_io.dropin,
            dropout=curr_io.dropout,
            upload_kbps=round(max(0.0, upload_kbps), 2),
            download_kbps=round(max(0.0, download_kbps), 2),
        )

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Compiles complete network telemetry for J.A.R.V.I.S. HUD display."""
        interfaces = self.get_interfaces()
        gw_dns = self.get_gateway_and_dns()
        hosts = self.scan_arp_cache()
        throughput = self.get_throughput_metrics()

        active_ifaces = [i for i in interfaces if i.is_up and i.ip_addresses]
        local_latency = self.ping_host(gw_dns.get("local_ip", "127.0.0.1"), port=80, timeout=0.2)

        return {
            "status": "operational" if active_ifaces else "degraded",
            "host_summary": {
                "hostname": gw_dns["hostname"],
                "local_ip": gw_dns["local_ip"],
                "gateway": gw_dns["gateway"],
                "dns_servers": gw_dns["dns_servers"],
            },
            "interface_count": len(interfaces),
            "active_interfaces": [asdict(i) for i in active_ifaces],
            "discovered_hosts_count": len(hosts),
            "discovered_hosts": [asdict(h) for h in hosts[:15]],
            "throughput": asdict(throughput),
            "ping_latency_ms": local_latency.get("latency_ms"),
            "health": {
                "has_gateway": bool(gw_dns["gateway"]),
                "active_links": len(active_ifaces) > 0,
                "packet_errors": throughput.errin + throughput.errout,
                "packet_drops": throughput.dropin + throughput.dropout,
            }
        }
