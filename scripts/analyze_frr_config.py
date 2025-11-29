#!/usr/bin/env python3
"""
FRR Configuration Analyzer

This script analyzes FRR configurations and provides insights.
GitHub Copilot can help extend this with additional analysis capabilities.
"""

import re
import sys
from typing import Dict, List, Set
from pathlib import Path


class FRRConfigAnalyzer:
    """Analyzes FRR configuration files"""

    def __init__(self, bgpd_conf: str = None, zebra_conf: str = None):
        self.bgpd_conf = bgpd_conf
        self.zebra_conf = zebra_conf
        self.bgp_config: List[str] = []
        self.zebra_config: List[str] = []

    def load_configs(self) -> bool:
        """Load configuration files"""
        try:
            if self.bgpd_conf and Path(self.bgpd_conf).exists():
                with open(self.bgpd_conf, 'r') as f:
                    self.bgp_config = f.readlines()

            if self.zebra_conf and Path(self.zebra_conf).exists():
                with open(self.zebra_conf, 'r') as f:
                    self.zebra_config = f.readlines()

            return True
        except Exception as e:
            print(f"Error loading configurations: {e}")
            return False

    def analyze_bgp_peers(self) -> Dict:
        """Analyze BGP peer configurations"""
        peers = {}
        current_as = None

        for line in self.bgp_config:
            line = line.strip()

            # Get local AS
            as_match = re.match(r'router\s+bgp\s+(\d+)', line)
            if as_match:
                current_as = as_match.group(1)

            # Get neighbor info
            neighbor_match = re.match(r'neighbor\s+([\d.]+)\s+remote-as\s+(\d+)', line)
            if neighbor_match:
                neighbor_ip = neighbor_match.group(1)
                remote_as = neighbor_match.group(2)

                peer_type = "iBGP" if remote_as == current_as else "eBGP"

                peers[neighbor_ip] = {
                    'remote_as': remote_as,
                    'type': peer_type,
                    'policies': []
                }

            # Get policy info
            policy_match = re.match(r'neighbor\s+([\d.]+)\s+route-map\s+(\S+)\s+(in|out)', line)
            if policy_match:
                neighbor_ip = policy_match.group(1)
                route_map = policy_match.group(2)
                direction = policy_match.group(3)

                if neighbor_ip in peers:
                    peers[neighbor_ip]['policies'].append(f"{route_map} ({direction})")

        return peers

    def analyze_route_maps(self) -> Dict:
        """Analyze route-map configurations"""
        route_maps = {}

        for line in self.bgp_config:
            line = line.strip()

            match = re.match(r'route-map\s+(\S+)\s+(permit|deny)\s+(\d+)', line)
            if match:
                name = match.group(1)
                action = match.group(2)
                seq = match.group(3)

                if name not in route_maps:
                    route_maps[name] = []

                route_maps[name].append(f"seq {seq}: {action}")

        return route_maps

    def analyze_networks(self) -> List[str]:
        """Analyze advertised networks"""
        networks = []

        for line in self.bgp_config:
            line = line.strip()

            match = re.match(r'network\s+([\d./]+)', line)
            if match:
                networks.append(match.group(1))

        return networks

    def analyze_interfaces(self) -> Dict:
        """Analyze interface configurations"""
        interfaces = {}
        current_interface = None

        for line in self.zebra_config:
            line = line.strip()

            # Match interface definition
            if_match = re.match(r'interface\s+(\S+)', line)
            if if_match:
                current_interface = if_match.group(1)
                interfaces[current_interface] = {
                    'addresses': [],
                    'description': None,
                    'status': 'up'
                }

            if current_interface:
                # Get IP address
                ip_match = re.match(r'ip\s+address\s+([\d./]+)', line)
                if ip_match:
                    interfaces[current_interface]['addresses'].append(ip_match.group(1))

                # Get description
                desc_match = re.match(r'description\s+(.+)', line)
                if desc_match:
                    interfaces[current_interface]['description'] = desc_match.group(1)

                # Check shutdown status
                if line == 'shutdown':
                    interfaces[current_interface]['status'] = 'down'

        return interfaces

    def check_best_practices(self) -> List[str]:
        """Check for BGP best practices"""
        recommendations = []

        # Check for router-id
        has_router_id = any(re.search(r'bgp\s+router-id', line) for line in self.bgp_config)
        if not has_router_id:
            recommendations.append("⚠️  Consider configuring explicit BGP router-id")

        # Check for log-neighbor-changes
        has_logging = any('log-neighbor-changes' in line for line in self.bgp_config)
        if not has_logging:
            recommendations.append("⚠️  Enable 'bgp log-neighbor-changes' for better monitoring")

        # Check for maximum-prefix
        has_max_prefix = any('maximum-prefix' in line for line in self.bgp_config)
        if not has_max_prefix:
            recommendations.append("⚠️  Consider configuring maximum-prefix limits on peers")

        # Check for soft-reconfiguration
        has_soft_reconfig = any('soft-reconfiguration' in line for line in self.bgp_config)
        if not has_soft_reconfig:
            recommendations.append("⚠️  Consider enabling soft-reconfiguration for policy changes")

        # Check for bogon filtering
        has_bogon = any('BOGON' in line.upper() for line in self.bgp_config)
        if not has_bogon:
            recommendations.append("⚠️  Implement bogon prefix filtering for security")

        return recommendations

    def generate_report(self) -> None:
        """Generate comprehensive analysis report"""
        print("=" * 70)
        print("FRR Configuration Analysis Report")
        print("=" * 70)
        print()

        # BGP Peers
        peers = self.analyze_bgp_peers()
        if peers:
            print("BGP Peer Summary:")
            print("-" * 70)
            for ip, info in peers.items():
                print(f"  Peer: {ip}")
                print(f"    AS: {info['remote_as']} ({info['type']})")
                if info['policies']:
                    print(f"    Policies: {', '.join(info['policies'])}")
                print()

        # Advertised Networks
        networks = self.analyze_networks()
        if networks:
            print("Advertised Networks:")
            print("-" * 70)
            for net in networks:
                print(f"  • {net}")
            print()

        # Route Maps
        route_maps = self.analyze_route_maps()
        if route_maps:
            print("Route Maps:")
            print("-" * 70)
            for name, sequences in route_maps.items():
                print(f"  {name}:")
                for seq in sequences:
                    print(f"    {seq}")
            print()

        # Interfaces
        interfaces = self.analyze_interfaces()
        if interfaces:
            print("Interface Summary:")
            print("-" * 70)
            for name, info in interfaces.items():
                status_icon = "✅" if info['status'] == 'up' else "❌"
                print(f"  {status_icon} {name}")
                if info['description']:
                    print(f"      Description: {info['description']}")
                for addr in info['addresses']:
                    print(f"      IP: {addr}")
                print()

        # Best Practices
        recommendations = self.check_best_practices()
        if recommendations:
            print("Best Practice Recommendations:")
            print("-" * 70)
            for rec in recommendations:
                print(f"  {rec}")
            print()

        print("=" * 70)


def main():
    """Main function"""
    bgpd_conf = None
    zebra_conf = None

    # Parse command line arguments
    if len(sys.argv) > 1:
        bgpd_conf = sys.argv[1]
    if len(sys.argv) > 2:
        zebra_conf = sys.argv[2]

    if not bgpd_conf and not zebra_conf:
        print("Usage: python analyze_frr_config.py <bgpd.conf> [zebra.conf]")
        sys.exit(1)

    analyzer = FRRConfigAnalyzer(bgpd_conf, zebra_conf)
    if analyzer.load_configs():
        analyzer.generate_report()
    else:
        print("Failed to load configuration files")
        sys.exit(1)


if __name__ == "__main__":
    main()
