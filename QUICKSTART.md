# Quick Start Guide

Get started with FRR configuration automation using GitHub Copilot in 5 minutes.

## Step 1: Explore Sample Configurations

View the sample BGP configuration:
```bash
cat configs/frr/bgpd.conf
```

View the sample Zebra configuration:
```bash
cat configs/frr/zebra.conf
```

## Step 2: Validate Configuration

Run the validation script:
```bash
python3 scripts/validate_bgp_config.py configs/frr/bgpd.conf
```

Expected output: Shows any errors or warnings in the configuration.

## Step 3: Analyze Configuration

Run the analysis script:
```bash
python3 scripts/analyze_frr_config.py configs/frr/bgpd.conf configs/frr/zebra.conf
```

Expected output: Detailed report showing peers, networks, policies, and interfaces.

## Step 4: Try Automated Fixes

Apply automated fixes (with backup):
```bash
scripts/fix_bgp_config.sh --backup --validate configs/frr/bgpd.conf
```

## Step 5: Deploy to Production (Optional)

Deploy configurations to your Linux server using GitHub Actions:

1. **Configure Secrets** (one-time setup):
   - Go to repository Settings → Secrets and variables → Actions
   - Add `SERVER_HOST`, `SERVER_USER`, and `SSH_PRIVATE_KEY`

2. **Run Deployment**:
   - Go to Actions tab → "Deploy FRR Configuration"
   - Click "Run workflow"
   - Select deployment options
   - Monitor the deployment progress

See [Deployment Guide](docs/deployment-guide.md) for detailed instructions.

## Step 6: Use with GitHub Copilot

Now you're ready to use GitHub Copilot! Try these prompts:

### Basic Analysis
```
"Analyze the BGP configuration in configs/frr/bgpd.conf"
```

### Find Issues
```
"Check configs/frr/bgpd.conf for any security issues or missing configurations"
```

### Add Configuration
```
"Add a new BGP neighbor to configs/frr/bgpd.conf for AS 65500 at IP 198.51.100.50"
```

### Fix Issues
```
"Fix any missing neighbor activations in configs/frr/bgpd.conf"
```

### Generate Documentation
```
"Document the route-maps defined in configs/frr/bgpd.conf"
```

## Common Tasks

### Add a New Neighbor

**Prompt**: "Add an eBGP neighbor to bgpd.conf with these details: AS 65100, IP 203.0.113.25, description 'Transit-Provider', with inbound and outbound route-maps"

### Create Route-Maps

**Prompt**: "Create route-maps for neighbor 10.0.1.2 to set local-preference to 200 on inbound routes and prepend AS path on outbound"

### Validate All Configs

**Prompt**: "Run the validation script on all configs in configs/frr/ and report any issues"

### Troubleshoot Issues

**Prompt**: "Based on the routing-issues.md guide, what could cause BGP session to neighbor 10.0.1.2 to stay in Active state?"

## Next Steps

### Local Development
1. Read the full [Copilot Guide](docs/copilot-guide.md)
2. Review [Common Routing Issues](configs/examples/routing-issues.md)
3. Study [Neighbor Configuration Examples](configs/examples/neighbor-configs.md)

### Production Deployment
1. Read the [Deployment Guide](docs/deployment-guide.md)
2. Set up GitHub Secrets (SERVER_HOST, SERVER_USER, SSH_PRIVATE_KEY)
3. Run the deployment workflow from GitHub Actions
4. Monitor BGP sessions and route propagation

## Tips

- Always validate after making changes
- Use `--backup` when applying automated fixes
- Start with simple prompts and gradually increase complexity
- Reference specific files in your Copilot prompts
- Review Copilot's suggestions before applying them

## Help

If you run into issues:
1. Check the [documentation](docs/)
2. Review the [examples](configs/examples/)
3. Run validation scripts to identify problems
4. Ask Copilot specific questions about the issue
