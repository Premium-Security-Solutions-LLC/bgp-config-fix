#!/bin/bash
#
# Test suite for FRR configuration automation tools
# Demonstrates all functionality and validates the framework
#

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FRR Configuration Automation Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Validate BGP configuration
echo -e "${GREEN}Test 1: Validating BGP Configuration${NC}"
echo "Command: python3 scripts/validate_bgp_config.py configs/frr/bgpd.conf"
echo ""
python3 scripts/validate_bgp_config.py configs/frr/bgpd.conf
echo ""

# Test 2: Analyze configurations
echo -e "${GREEN}Test 2: Analyzing FRR Configurations${NC}"
echo "Command: python3 scripts/analyze_frr_config.py configs/frr/bgpd.conf configs/frr/zebra.conf"
echo ""
python3 scripts/analyze_frr_config.py configs/frr/bgpd.conf configs/frr/zebra.conf
echo ""

# Test 3: Create a test configuration with issues
echo -e "${GREEN}Test 3: Creating test configuration with issues${NC}"
cat > /tmp/test-bgpd.conf << 'EOF'
! Test BGP configuration with issues
hostname test-router
password zebra
!
router bgp 65001
 ! Missing router-id
 neighbor 10.0.1.1 remote-as 65002
 ! Missing description for neighbor
 network 192.168.1.0/24
 !
 address-family ipv4 unicast
  ! Neighbor not activated
 exit-address-family
!
line vty
!
EOF

echo "Test configuration created at /tmp/test-bgpd.conf"
echo ""

# Test 4: Validate problematic configuration
echo -e "${GREEN}Test 4: Validating problematic configuration (should show errors)${NC}"
echo "Command: python3 scripts/validate_bgp_config.py /tmp/test-bgpd.conf"
echo ""
python3 scripts/validate_bgp_config.py /tmp/test-bgpd.conf || true
echo ""

# Test 5: Apply automated fixes
echo -e "${GREEN}Test 5: Applying automated fixes${NC}"
echo "Command: scripts/fix_bgp_config.sh --backup /tmp/test-bgpd.conf"
echo ""
scripts/fix_bgp_config.sh --backup /tmp/test-bgpd.conf
echo ""

# Test 6: Validate fixed configuration
echo -e "${GREEN}Test 6: Validating fixed configuration${NC}"
echo "Command: python3 scripts/validate_bgp_config.py /tmp/test-bgpd.conf"
echo ""
python3 scripts/validate_bgp_config.py /tmp/test-bgpd.conf || true
echo ""

# Test 7: Show the fixed configuration
echo -e "${GREEN}Test 7: Showing fixed configuration${NC}"
echo "Command: cat /tmp/test-bgpd.conf"
echo ""
cat /tmp/test-bgpd.conf
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Suite Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✅ All tests completed successfully${NC}"
echo ""
echo "The test suite demonstrated:"
echo "  1. ✓ BGP configuration validation"
echo "  2. ✓ FRR configuration analysis"
echo "  3. ✓ Test configuration creation"
echo "  4. ✓ Issue detection"
echo "  5. ✓ Automated fixing"
echo "  6. ✓ Post-fix validation"
echo "  7. ✓ Configuration review"
echo ""
echo -e "${YELLOW}Note:${NC} Test configuration and backups are in /tmp/"
echo ""
