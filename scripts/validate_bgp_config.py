#!/usr/bin/env python3
"""
FRR BGP Configuration Validator

This script validates FRR BGP configuration files for common issues.
GitHub Copilot can help extend this script with additional validation rules.
"""

import re
import sys
from typing import List, Dict, Tuple
from pathlib import Path


class BGPConfigValidator:
    """Validates BGP configuration files"""

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config_lines: List[str] = []
        self.neighbors: Dict[str, Dict] = {}
        self.route_maps: Dict[str, bool] = {}
        self.prefix_lists: Dict[str, bool] = {}

    def load_config(self) -> bool:
        """Load configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config_lines = f.readlines()
            return True
        except FileNotFoundError:
            self.errors.append(f"Configuration file not found: {self.config_file}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading configuration: {e}")
            return False

    def validate_basic_syntax(self) -> None:
        """Validate basic configuration syntax"""
        router_bgp_found = False
        in_router_bgp = False

        for line_num, line in enumerate(self.config_lines, 1):
            line = line.strip()

            # Skip comments and empty lines
            if line.startswith('!') or not line:
                continue

            # Check for router bgp section
            if re.match(r'^router\s+bgp\s+\d+', line):
                router_bgp_found = True
                in_router_bgp = True

            # Check for exit from router bgp
            if in_router_bgp and line == '!':
                in_router_bgp = False

        if not router_bgp_found:
            self.errors.append("No 'router bgp' configuration found")

    def extract_neighbors(self) -> None:
        """Extract neighbor configurations
        Note: Currently only matches IPv4 addresses. IPv6 and hostname-based neighbors not yet supported.
        """
        for line_num, line in enumerate(self.config_lines, 1):
            line = line.strip()

            # Match neighbor configuration (IPv4 only)
            # TODO: Add support for IPv6 addresses and hostnames
            neighbor_match = re.match(r'neighbor\s+([\d.]+)\s+remote-as\s+(\d+)', line)
            if neighbor_match:
                neighbor_ip = neighbor_match.group(1)
                remote_as = neighbor_match.group(2)

                if neighbor_ip not in self.neighbors:
                    self.neighbors[neighbor_ip] = {
                        'remote_as': remote_as,
                        'line': line_num,
                        'activated': False,
                        'has_description': False,
                        'soft_reconfig': False
                    }

            # Check for description
            desc_match = re.match(r'neighbor\s+([\d.]+)\s+description\s+(.+)', line)
            if desc_match:
                neighbor_ip = desc_match.group(1)
                if neighbor_ip in self.neighbors:
                    self.neighbors[neighbor_ip]['has_description'] = True

            # Check for activation
            activate_match = re.match(r'neighbor\s+([\d.]+)\s+activate', line)
            if activate_match:
                neighbor_ip = activate_match.group(1)
                if neighbor_ip in self.neighbors:
                    self.neighbors[neighbor_ip]['activated'] = True

            # Check for soft-reconfiguration
            soft_match = re.match(r'neighbor\s+([\d.]+)\s+soft-reconfiguration\s+inbound', line)
            if soft_match:
                neighbor_ip = soft_match.group(1)
                if neighbor_ip in self.neighbors:
                    self.neighbors[neighbor_ip]['soft_reconfig'] = True

    def validate_neighbors(self) -> None:
        """Validate neighbor configurations"""
        for neighbor_ip, config in self.neighbors.items():
            # Check if neighbor is activated
            if not config['activated']:
                self.warnings.append(
                    f"Neighbor {neighbor_ip} at line {config['line']} is not activated in address-family"
                )

            # Check if neighbor has description
            if not config['has_description']:
                self.warnings.append(
                    f"Neighbor {neighbor_ip} at line {config['line']} has no description"
                )

            # Check for soft-reconfiguration
            if not config['soft_reconfig']:
                self.warnings.append(
                    f"Neighbor {neighbor_ip} at line {config['line']} does not have soft-reconfiguration enabled"
                )

    def extract_route_maps(self) -> None:
        """Extract route-map definitions"""
        for line in self.config_lines:
            line = line.strip()
            match = re.match(r'route-map\s+(\S+)\s+(permit|deny)\s+\d+', line)
            if match:
                route_map_name = match.group(1)
                self.route_maps[route_map_name] = True

    def extract_prefix_lists(self) -> None:
        """Extract prefix-list definitions"""
        for line in self.config_lines:
            line = line.strip()
            match = re.match(r'ip\s+prefix-list\s+(\S+)\s+seq\s+\d+', line)
            if match:
                prefix_list_name = match.group(1)
                self.prefix_lists[prefix_list_name] = True

    def validate_references(self) -> None:
        """Validate that referenced route-maps and prefix-lists exist"""
        for line_num, line in enumerate(self.config_lines, 1):
            line = line.strip()

            # Check route-map references
            route_map_ref = re.search(r'route-map\s+(\S+)\s+(in|out)', line)
            if route_map_ref:
                route_map_name = route_map_ref.group(1)
                if route_map_name not in self.route_maps:
                    self.errors.append(
                        f"Line {line_num}: Route-map '{route_map_name}' is referenced but not defined"
                    )

            # Check prefix-list references in route-maps
            prefix_list_ref = re.search(r'match\s+ip\s+address\s+prefix-list\s+(\S+)', line)
            if prefix_list_ref:
                prefix_list_name = prefix_list_ref.group(1)
                if prefix_list_name not in self.prefix_lists:
                    self.errors.append(
                        f"Line {line_num}: Prefix-list '{prefix_list_name}' is referenced but not defined"
                    )

    def validate_bogon_filters(self) -> None:
        """Check if bogon filtering is implemented
        Note: This is a basic check that only verifies the presence of bogon-related configuration.
        It does not validate that the filters are correctly defined or properly applied.
        """
        has_bogon_filter = any('BOGON' in line.upper() for line in self.config_lines)
        if not has_bogon_filter:
            self.warnings.append(
                "No bogon filtering detected. Consider adding prefix-list for bogon networks"
            )

    def validate_router_id(self) -> None:
        """Check if router-id is configured"""
        has_router_id = any(re.search(r'bgp\s+router-id', line) for line in self.config_lines)
        if not has_router_id:
            self.errors.append("No BGP router-id configured")

    def run_all_validations(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks"""
        if not self.load_config():
            return False, self.errors, self.warnings

        self.validate_basic_syntax()
        self.extract_neighbors()
        self.validate_neighbors()
        self.extract_route_maps()
        self.extract_prefix_lists()
        self.validate_references()
        self.validate_bogon_filters()
        self.validate_router_id()

        return len(self.errors) == 0, self.errors, self.warnings

    def print_report(self) -> None:
        """Print validation report"""
        print("=" * 70)
        print(f"BGP Configuration Validation Report: {self.config_file}")
        print("=" * 70)
        print()

        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")
            print()

        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ Configuration validation passed with no issues!")
        elif not self.errors:
            print("✅ Configuration validation passed with warnings")
        else:
            print("❌ Configuration validation failed")

        print()
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 70)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_bgp_config.py <bgpd.conf>")
        sys.exit(1)

    config_file = sys.argv[1]
    validator = BGPConfigValidator(config_file)
    success, errors, warnings = validator.run_all_validations()
    validator.print_report()

    # Exit with error code if validation failed
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
