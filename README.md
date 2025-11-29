# FRR BGP Configuration Fix Repository

This repository provides tools, configurations, and documentation to help automate the analysis and fixing of FRR (Free Range Routing) BGP and Zebra configurations using GitHub Copilot Coding Agent.

## Purpose

Enable GitHub Copilot to effectively:
- Analyze FRR configuration files (bgpd.conf, zebra.conf)
- Identify common routing issues and misconfigurations
- Generate neighbor configurations
- Validate and fix BGP configuration problems
- Provide automation scripts for configuration management
- **Deploy configurations to production servers via GitHub Actions**

## Repository Structure

```
bgp-config-fix/
├── .github/
│   └── workflows/
│       ├── deploy-frr-config.yml # Automated deployment workflow
│       └── README.md             # Workflow documentation
├── configs/
│   ├── frr/                      # Sample FRR configurations
│   │   ├── bgpd.conf            # BGP daemon configuration
│   │   └── zebra.conf           # Zebra routing daemon configuration
│   └── examples/                 # Configuration examples and patterns
│       ├── neighbor-configs.md  # Neighbor configuration examples
│       └── routing-issues.md    # Common routing problems and solutions
├── scripts/
│   ├── validate_bgp_config.py   # Configuration validator
│   ├── analyze_frr_config.py    # Configuration analyzer
│   └── fix_bgp_config.sh        # Automated fix script
├── docs/
│   ├── copilot-guide.md         # Guide for using GitHub Copilot
│   └── deployment-guide.md      # Deployment guide for GitHub Actions
└── README.md                     # This file
```

## Features

### 1. Sample Configurations
- **bgpd.conf**: Comprehensive BGP configuration with:
  - Multiple neighbor types (iBGP, eBGP)
  - Route-maps and filtering
  - Prefix-lists including bogon filters
  - AS-path and community lists
  
- **zebra.conf**: Zebra configuration with:
  - Interface definitions
  - Static routing examples
  - Access control lists

### 2. Validation Tools
- **validate_bgp_config.py**: Validates BGP configurations for:
  - Missing neighbor activations
  - Undefined route-maps and prefix-lists
  - Missing router-id
  - Missing descriptions
  - Security best practices

### 3. Analysis Tools
- **analyze_frr_config.py**: Analyzes configurations to show:
  - BGP peer summary (iBGP vs eBGP)
  - Applied policies
  - Advertised networks
  - Interface status
  - Best practice recommendations

### 4. Automated Fixes
- **fix_bgp_config.sh**: Automatically fixes common issues:
  - Missing router-id
  - Missing neighbor descriptions
  - Missing address-family activations
  - Missing soft-reconfiguration

### 5. Automated Deployment
- **GitHub Actions Workflow**: Deploy configurations to production servers:
  - SSH connection with secure credential management
  - Configuration validation and analysis
  - Automated fix application
  - FRR service restart
  - BGP neighbor verification
  - Connectivity and route propagation checks

## Quick Start

### Local Usage

#### Validate a Configuration

```bash
python scripts/validate_bgp_config.py configs/frr/bgpd.conf
```

#### Analyze Configurations

```bash
python scripts/analyze_frr_config.py configs/frr/bgpd.conf configs/frr/zebra.conf
```

#### Apply Automated Fixes

```bash
scripts/fix_bgp_config.sh --backup --validate configs/frr/bgpd.conf
```

### Automated Deployment to Production

Deploy FRR configurations to your Linux server using GitHub Actions:

1. **Configure GitHub Secrets**:
   - `SERVER_HOST`: Your server hostname or IP
   - `SERVER_USER`: SSH username
   - `SSH_PRIVATE_KEY`: SSH private key for authentication

2. **Run the Workflow**:
   - Go to Actions tab → "Deploy FRR Configuration"
   - Click "Run workflow"
   - Select options (apply fixes, restart services)
   - Monitor the deployment logs

3. **Verify Deployment**:
   - Check BGP neighbor status
   - Verify route propagation
   - Review connectivity tests

See the [Deployment Guide](docs/deployment-guide.md) for detailed instructions.

## Using with GitHub Copilot

This repository is optimized for use with GitHub Copilot Coding Agent. See [docs/copilot-guide.md](docs/copilot-guide.md) for detailed guidance.

### Example Copilot Prompts

1. **Configuration Analysis**:
   - "Analyze the BGP configuration in configs/frr/bgpd.conf and explain the neighbor relationships"
   - "Identify security issues in the current BGP setup"

2. **Issue Detection**:
   - "Check if all BGP neighbors are properly activated"
   - "Find neighbors without soft-reconfiguration enabled"

3. **Configuration Generation**:
   - "Add a new eBGP peer for AS 65200 at IP 203.0.113.100"
   - "Create a route-map to set local-preference to 200"

4. **Automated Fixes**:
   - "Fix all missing neighbor activations in bgpd.conf"
   - "Add descriptions to all neighbors"

## Configuration Examples

### Adding a BGP Neighbor

```
neighbor 203.0.113.100 remote-as 65200
neighbor 203.0.113.100 description Customer-Network
neighbor 203.0.113.100 ebgp-multihop 2
!
address-family ipv4 unicast
 neighbor 203.0.113.100 activate
 neighbor 203.0.113.100 soft-reconfiguration inbound
 neighbor 203.0.113.100 route-map CUSTOMER-IN in
 neighbor 203.0.113.100 route-map CUSTOMER-OUT out
exit-address-family
```

### Creating Route-Maps

```
route-map CUSTOMER-IN permit 10
 match ip address prefix-list CUSTOMER-PREFIXES
 set local-preference 150
!
route-map CUSTOMER-OUT permit 10
 match ip address prefix-list OUR-NETWORKS
```

## Common Issues and Solutions

See [configs/examples/routing-issues.md](configs/examples/routing-issues.md) for a comprehensive guide to:
- BGP session establishment issues
- Route advertisement problems
- Route installation failures
- Route flapping
- Asymmetric routing
- And more...

## Requirements

- Python 3.6 or higher (for validation and analysis scripts)
- Bash (for automated fix script)
- FRR (for production use)

## Documentation

- [Deployment Guide](docs/deployment-guide.md) - Complete guide for automated deployment via GitHub Actions
- [Workflow Documentation](.github/workflows/README.md) - GitHub Actions workflow details
- [Copilot Usage Guide](docs/copilot-guide.md) - Comprehensive guide for using GitHub Copilot with this repository
- [Neighbor Configurations](configs/examples/neighbor-configs.md) - Examples of various neighbor configurations
- [Routing Issues](configs/examples/routing-issues.md) - Common routing problems and their solutions

## Contributing

This repository is designed to be extended. You can:
- Add new validation rules to `validate_bgp_config.py`
- Enhance analysis capabilities in `analyze_frr_config.py`
- Add more example configurations
- Document additional routing issues and solutions

## Security Considerations

The sample configurations include:
- Bogon prefix filtering
- Maximum prefix limits (recommended)
- Route-map security policies
- Access control lists

Always review and customize configurations for your specific security requirements.

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions, please use the GitHub issue tracker or consult the documentation in the `docs/` directory.