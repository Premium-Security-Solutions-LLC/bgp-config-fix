# Common FRR/BGP Routing Issues and Fixes

This document catalogs common routing issues in FRR and their solutions.

## BGP Issues

### 1. BGP Session Not Establishing

**Symptoms:**
- Neighbor state stuck in "Active" or "Connect"
- No route exchange happening

**Common Causes & Fixes:**

```bash
# Check neighbor status
vtysh -c "show ip bgp summary"

# Issue: Incorrect neighbor IP
# Fix: Verify neighbor IP in bgpd.conf
neighbor 10.0.1.2 remote-as 65002  # Ensure this matches peer config

# Issue: Firewall blocking TCP 179
# Fix: Allow BGP port in firewall
sudo iptables -A INPUT -p tcp --dport 179 -j ACCEPT

# Issue: No route to neighbor
# Fix: Add static route or ensure IGP is working
ip route 10.0.1.2/32 203.0.113.1
```

### 2. Routes Not Being Advertised

**Symptoms:**
- BGP session up but routes not propagated
- Empty BGP table on peer

**Common Causes & Fixes:**

```
! Issue: Network statement missing
! Fix: Add network statement
router bgp 65001
 network 192.168.1.0/24

! Issue: Route not in RIB
! Fix: Ensure route exists in routing table via connected/static/IGP

! Issue: Route filtered by outbound policy
! Fix: Check and adjust route-map
route-map PEER-OUT permit 10
 match ip address prefix-list ALLOWED-PREFIXES

! Issue: Neighbor not activated in address-family
! Fix: Activate neighbor
address-family ipv4 unicast
 neighbor 10.0.1.2 activate
exit-address-family
```

### 3. Routes Received But Not Installed

**Symptoms:**
- Routes in BGP table but not in RIB
- "show ip bgp" shows routes, but "show ip route" doesn't

**Common Causes & Fixes:**

```
! Issue: Route has worse administrative distance
! Fix: BGP route is valid but another protocol has better AD
! Solution: Check with "show ip route A.B.C.D"

! Issue: Next-hop not reachable
! Fix: Ensure next-hop is reachable
! Check: show ip bgp A.B.C.D
! Solution: Add static route to next-hop or configure next-hop-self

! Issue: Route marked as dampened
! Fix: Clear dampening
clear ip bgp dampening
```

### 4. Route Flapping

**Symptoms:**
- Routes appear and disappear frequently
- High CPU usage on router

**Common Causes & Fixes:**

```
! Issue: Unstable link
! Fix: Check physical layer and implement dampening
router bgp 65001
 bgp dampening 15 750 2000 60

! Issue: BGP session flapping
! Fix: Adjust timers
neighbor 10.0.1.2 timers 30 90
neighbor 10.0.1.2 timers connect 30
```

### 5. Asymmetric Routing

**Symptoms:**
- Traffic goes out one path but returns via another
- Different AS paths in each direction

**Common Causes & Fixes:**

```
! Fix: Use local-preference to control inbound traffic
route-map PREFER-ISP-A permit 10
 set local-preference 200

! Fix: Use AS-path prepending to control outbound traffic
route-map DEPREF-PATH permit 10
 set as-path prepend 65001 65001 65001
```

## Zebra/Kernel Issues

### 6. Routes Not Installing in Kernel

**Symptoms:**
- Routes in FRR RIB but not in kernel routing table
- "ip route" shows different routes than "show ip route"

**Common Causes & Fixes:**

```bash
# Issue: FIB sync issues
# Fix: Restart zebra or reload configuration
sudo systemctl restart frr

# Check kernel routing table
ip route show

# Check FRR routing table
vtysh -c "show ip route"

# Force route installation
vtysh -c "clear ip route *"
```

### 7. Interface Issues

**Symptoms:**
- Interface down or not configured correctly
- IP address conflicts

**Common Causes & Fixes:**

```
! Issue: Interface not enabled
! Fix: Enable interface in zebra.conf
interface eth0
 no shutdown

! Issue: Wrong IP address
! Fix: Correct IP address
interface eth0
 ip address 203.0.113.10/30

! Verify with:
! show interface eth0
```

## Route-Map and Filtering Issues

### 8. Incorrect Route Filtering

**Symptoms:**
- Too many or too few routes accepted/advertised
- Wrong routes being selected

**Common Causes & Fixes:**

```
! Issue: Prefix-list too permissive
! Fix: Tighten prefix-list rules
ip prefix-list CUSTOMER-ROUTES seq 5 permit 192.168.0.0/16 le 24

! Issue: Route-map deny all
! Fix: Ensure implicit permit or explicit permit at end
route-map FILTER permit 999
 ! Explicit permit all as last resort

! Issue: AS-path filter incorrect
! Fix: Verify regex pattern
ip as-path access-list 1 permit ^65100_

! Debug filtering:
debug bgp updates
debug bgp filters
```

### 9. Community Handling Issues

**Symptoms:**
- Communities not being set or matched correctly
- Traffic engineering not working

**Common Causes & Fixes:**

```
! Issue: Community not being sent
! Fix: Ensure send-community is enabled
address-family ipv4 unicast
 neighbor 10.0.1.2 send-community

! Issue: Community not matching
! Fix: Check community list syntax
ip community-list standard SPECIAL permit 65001:100

! Set community in route-map
route-map SET-COMM permit 10
 set community 65001:100
```

## Performance Issues

### 10. High Memory Usage

**Symptoms:**
- Router running out of memory
- OOM killer terminating FRR

**Common Causes & Fixes:**

```
! Issue: Too many routes
! Fix: Implement prefix limits
neighbor 10.0.1.2 maximum-prefix 100000 80 restart 30

! Issue: Soft-reconfig storing too much
! Fix: Use route-refresh instead
! Remove: neighbor X soft-reconfiguration inbound
! Ensure peer supports route-refresh capability
```

### 11. High CPU Usage

**Symptoms:**
- Router CPU at 100%
- Slow response from vtysh

**Common Causes & Fixes:**

```
! Issue: Too many route updates
! Fix: Implement update dampening
router bgp 65001
 bgp dampening

! Issue: Too much debugging enabled
! Fix: Disable unnecessary debugging
no debug bgp updates
no debug bgp keepalives

! Issue: Recursive next-hop lookups
! Fix: Use next-hop-self or static routes
neighbor 10.0.0.2 next-hop-self
```

## Troubleshooting Commands

```bash
# BGP Status
vtysh -c "show ip bgp summary"
vtysh -c "show ip bgp neighbors"
vtysh -c "show ip bgp"

# Route Details
vtysh -c "show ip bgp A.B.C.D"
vtysh -c "show ip route A.B.C.D"

# Policy Verification
vtysh -c "show route-map"
vtysh -c "show ip prefix-list"
vtysh -c "show ip as-path-access-list"
vtysh -c "show ip community-list"

# Debugging
vtysh -c "debug bgp updates"
vtysh -c "debug bgp keepalives"

# Clear Commands
vtysh -c "clear ip bgp *"
vtysh -c "clear ip bgp A.B.C.D soft"
```
