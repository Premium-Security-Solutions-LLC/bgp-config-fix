# FRR BGP Neighbor Configuration Examples

This directory contains example neighbor configurations for various scenarios.

## Example 1: Basic eBGP Peer

```
neighbor 203.0.113.1 remote-as 65100
neighbor 203.0.113.1 description Example-ISP
neighbor 203.0.113.1 ebgp-multihop 1
```

## Example 2: iBGP Peer with Route Reflector

```
neighbor 10.0.0.100 remote-as 65001
neighbor 10.0.0.100 description Route-Reflector
neighbor 10.0.0.100 update-source lo
neighbor 10.0.0.100 route-reflector-client
```

## Example 3: Peer with Prefix Filtering

```
neighbor 203.0.113.2 remote-as 65200
neighbor 203.0.113.2 description Filtered-Peer
!
address-family ipv4 unicast
 neighbor 203.0.113.2 activate
 neighbor 203.0.113.2 prefix-list ACCEPT-FROM-PEER in
 neighbor 203.0.113.2 prefix-list ANNOUNCE-TO-PEER out
exit-address-family
```

## Example 4: Peer with Route Map Policy

```
neighbor 203.0.113.3 remote-as 65300
neighbor 203.0.113.3 description Policy-Peer
!
address-family ipv4 unicast
 neighbor 203.0.113.3 activate
 neighbor 203.0.113.3 route-map SET-LP-200 in
 neighbor 203.0.113.3 route-map PREPEND-PATH out
exit-address-family
!
route-map SET-LP-200 permit 10
 set local-preference 200
!
route-map PREPEND-PATH permit 10
 set as-path prepend 65001 65001
```

## Common Neighbor Configuration Issues

### Issue 1: Missing neighbor activation in address-family
**Problem:** Neighbor is configured but not activated in address-family
**Solution:** Add `neighbor X.X.X.X activate` under address-family

### Issue 2: Incorrect AS number
**Problem:** remote-as doesn't match peer's actual AS
**Solution:** Verify and correct the remote-as value

### Issue 3: Missing update-source for iBGP
**Problem:** iBGP peer using physical interface instead of loopback
**Solution:** Add `neighbor X.X.X.X update-source lo`

### Issue 4: No soft-reconfiguration
**Problem:** Cannot view received routes before policy application
**Solution:** Add `neighbor X.X.X.X soft-reconfiguration inbound`

### Issue 5: Missing next-hop-self for iBGP
**Problem:** Routes not properly propagated in iBGP mesh
**Solution:** Add `neighbor X.X.X.X next-hop-self` for iBGP peers
