#!/bin/bash
#
# FRR Configuration Fix Script
# This script provides automated fixes for common FRR configuration issues
# GitHub Copilot can help extend this script with additional fix capabilities
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="/tmp/frr-backups-$(date +%Y%m%d-%H%M%S)"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS] <config-file>

Options:
    -b, --backup        Create backup before making changes
    -v, --validate      Validate configuration after fixes
    -h, --help          Show this help message

Examples:
    $0 -b -v configs/frr/bgpd.conf
    $0 --backup --validate /etc/frr/bgpd.conf

EOF
    exit 1
}

backup_config() {
    local config_file="$1"
    
    if [ ! -f "$config_file" ]; then
        log_error "Configuration file not found: $config_file"
        return 1
    fi
    
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/$(basename "$config_file").backup"
    cp "$config_file" "$backup_file"
    log_info "Backup created: $backup_file"
}

validate_config() {
    local config_file="$1"
    
    if [ ! -f "$SCRIPT_DIR/validate_bgp_config.py" ]; then
        log_warn "Validation script not found, skipping validation"
        return 0
    fi
    
    log_info "Validating configuration..."
    if python3 "$SCRIPT_DIR/validate_bgp_config.py" "$config_file"; then
        log_info "Validation passed"
        return 0
    else
        log_warn "Validation found issues"
        return 1
    fi
}

fix_missing_router_id() {
    local config_file="$1"
    
    # Check if router-id is missing
    if ! grep -q "bgp router-id" "$config_file"; then
        log_warn "Missing BGP router-id"
        log_warn "Router-ID should be manually configured using a loopback interface IP"
        log_warn "Automated router-id configuration skipped - please configure manually"
        # Note: We don't auto-generate router-id as it should be a stable, unique loopback IP
        # not a neighbor IP. This should be configured manually by the administrator.
    fi
}

fix_missing_descriptions() {
    local config_file="$1"
    local temp_file=$(mktemp)
    
    log_info "Checking for neighbors without descriptions..."
    
    # Extract all neighbor IPs (IPv4 only)
    local neighbors=$(grep "neighbor.*remote-as" "$config_file" | awk '{print $2}' | sort -u)
    
    for neighbor in $neighbors; do
        # Check if description exists for this neighbor
        if ! grep -q "neighbor $neighbor description" "$config_file"; then
            # Get the AS number for this neighbor
            local remote_as=$(grep "neighbor $neighbor remote-as" "$config_file" | awk '{print $4}' | head -1)
            log_info "Adding description for neighbor $neighbor (AS $remote_as)"
            # Add description after the remote-as line
            sed -i "/neighbor $neighbor remote-as/a\ neighbor $neighbor description Peer-AS-$remote_as" "$config_file"
        fi
    done
}

fix_missing_activation() {
    local config_file="$1"
    
    log_info "Checking for neighbors without address-family activation..."
    
    # Extract all neighbor IPs
    local neighbors=$(grep "neighbor.*remote-as" "$config_file" | awk '{print $2}' | sort -u)
    
    # Check if address-family section exists
    if grep -q "address-family ipv4 unicast" "$config_file"; then
        for neighbor in $neighbors; do
            # Check if neighbor is activated
            if ! grep -A 50 "address-family ipv4 unicast" "$config_file" | grep -q "neighbor $neighbor activate"; then
                log_info "Adding activation for neighbor $neighbor"
                # Add activation in address-family section
                sed -i "/address-family ipv4 unicast/a\ \ neighbor $neighbor activate" "$config_file"
            fi
        done
    else
        log_warn "No address-family ipv4 unicast section found"
        log_info "Adding address-family section with neighbor activations"
        
        # Add address-family section before the last '!' in router bgp section
        echo " !" >> "$config_file"
        echo " address-family ipv4 unicast" >> "$config_file"
        for neighbor in $neighbors; do
            echo "  neighbor $neighbor activate" >> "$config_file"
        done
        echo " exit-address-family" >> "$config_file"
    fi
}

add_soft_reconfiguration() {
    local config_file="$1"
    
    log_info "Adding soft-reconfiguration for peers..."
    log_warn "Note: Soft-reconfiguration increases memory usage. Use judiciously."
    
    # This is a simplified approach - in reality you'd need to identify eBGP vs iBGP
    # and only apply to eBGP peers or where frequent policy changes occur
    local neighbors=$(grep "neighbor.*remote-as" "$config_file" | awk '{print $2}' | sort -u)
    
    for neighbor in $neighbors; do
        if grep -A 50 "address-family ipv4 unicast" "$config_file" | grep -q "neighbor $neighbor activate"; then
            if ! grep -A 50 "address-family ipv4 unicast" "$config_file" | grep -q "neighbor $neighbor soft-reconfiguration inbound"; then
                log_info "Adding soft-reconfiguration for $neighbor"
                sed -i "/neighbor $neighbor activate/a\ \ neighbor $neighbor soft-reconfiguration inbound" "$config_file"
            fi
        fi
    done
}

apply_basic_fixes() {
    local config_file="$1"
    
    log_info "Applying basic configuration fixes..."
    
    fix_missing_router_id "$config_file"
    fix_missing_descriptions "$config_file"
    fix_missing_activation "$config_file"
    add_soft_reconfiguration "$config_file"
    
    log_info "Basic fixes applied"
}

main() {
    local config_file=""
    local do_backup=false
    local do_validate=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--backup)
                do_backup=true
                shift
                ;;
            -v|--validate)
                do_validate=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                config_file="$1"
                shift
                ;;
        esac
    done
    
    # Check if config file is provided
    if [ -z "$config_file" ]; then
        log_error "No configuration file specified"
        usage
    fi
    
    if [ ! -f "$config_file" ]; then
        log_error "Configuration file not found: $config_file"
        exit 1
    fi
    
    log_info "Processing configuration: $config_file"
    
    # Backup if requested
    if [ "$do_backup" = true ]; then
        backup_config "$config_file"
    fi
    
    # Apply fixes
    apply_basic_fixes "$config_file"
    
    # Validate if requested
    if [ "$do_validate" = true ]; then
        validate_config "$config_file"
    fi
    
    log_info "Configuration fixes completed successfully"
    
    if [ "$do_backup" = true ]; then
        log_info "Backup location: $BACKUP_DIR"
    fi
}

# Run main function
main "$@"
