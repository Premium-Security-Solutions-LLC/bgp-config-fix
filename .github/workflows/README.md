# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating FRR (Free Range Routing) configuration deployment and management.

## Available Workflows

### Deploy FRR Configuration (`deploy-frr-config.yml`)

This workflow automates the deployment of FRR configuration fixes to a connected Linux server.

#### Features

1. **SSH Connection**: Securely connects to the target server using credentials stored in GitHub Secrets
2. **Configuration Validation**: Validates `bgpd.conf` and `zebra.conf` using the validation script
3. **Configuration Analysis**: Analyzes BGP and GRE tunnel setup and generates a comprehensive report
4. **Automated Fixes**: Applies automated fixes to configuration files
5. **Service Management**: Restarts FRR services to apply changes
6. **Connectivity Checks**: Performs connectivity tests and verifies BGP neighbors
7. **Route Verification**: Confirms that BGP routes are propagating globally

#### Required GitHub Secrets

Before running this workflow, you must configure the following secrets in your GitHub repository:

- `SERVER_HOST`: The hostname or IP address of the target Linux server
- `SERVER_USER`: The SSH username for connecting to the server
- `SSH_PRIVATE_KEY`: The SSH private key for authentication (in PEM format)

To add these secrets:
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the appropriate value

#### How to Run

This workflow is configured to run manually using `workflow_dispatch`:

1. Go to the "Actions" tab in your GitHub repository
2. Select "Deploy FRR Configuration" from the workflows list
3. Click "Run workflow"
4. Configure the workflow options:
   - **Apply automated fixes**: Enable/disable automated configuration fixes (default: true)
   - **Restart FRR services**: Enable/disable service restart after deployment (default: true)
5. Click "Run workflow" to start the deployment

#### Workflow Steps

The workflow executes the following steps in order:

1. **Checkout repository**: Gets the latest code and configuration files
2. **Set up Python**: Prepares the Python environment for running scripts
3. **Setup SSH key**: Configures SSH authentication using the provided private key
4. **Test SSH connection**: Verifies connectivity to the target server
5. **Copy configuration files**: Transfers `bgpd.conf` and `zebra.conf` to the server
6. **Copy scripts**: Transfers validation, analysis, and fix scripts to the server
7. **Validate BGP configuration**: Runs validation checks on both configuration files
8. **Analyze FRR configuration**: Generates a detailed analysis report
9. **Apply configuration fixes** (optional): Applies automated fixes to the configuration
10. **Backup current FRR configuration**: Creates backups of existing configurations
11. **Deploy configuration files**: Copies configurations to the FRR directory (`/etc/frr/`)
12. **Validate deployed configuration**: Uses FRR tools to verify syntax
13. **Restart FRR services** (optional): Restarts the FRR daemon
14. **Verify FRR daemons**: Checks that FRR services are running
15. **Check BGP neighbor status**: Verifies BGP session status
16. **Check BGP routes**: Displays the BGP routing table
17. **Perform connectivity checks**: Tests network connectivity to BGP peers
18. **Verify route propagation**: Confirms routes are being advertised and received
19. **Generate deployment report**: Creates a summary of all actions performed
20. **Cleanup**: Removes temporary files from the server

#### Output and Logs

Each step in the workflow produces detailed output that can be viewed in the GitHub Actions log. Key sections include:

- **Validation Report**: Shows errors and warnings found in configuration files
- **Analysis Report**: Displays BGP peer summary, route maps, interfaces, and recommendations
- **Fix Application**: Shows what fixes were applied
- **BGP Status**: Shows neighbor status and route information
- **Connectivity Results**: Shows network connectivity test results

#### Server Requirements

The target Linux server must have:

- SSH server running and accessible
- FRR (Free Range Routing) installed
- Python 3.x installed
- Sudo access for the SSH user (for FRR service management)
- Standard networking tools (`ping`, `ip`, etc.)

#### Directory Structure

The workflow expects the following directory structure in the repository:

```
bgp-config-fix/
├── .github/
│   └── workflows/
│       ├── deploy-frr-config.yml  # Main deployment workflow
│       └── README.md              # This file
├── configs/
│   └── frr/
│       ├── bgpd.conf              # BGP daemon configuration
│       └── zebra.conf             # Zebra routing daemon configuration
└── scripts/
    ├── validate_bgp_config.py     # Configuration validator
    ├── analyze_frr_config.py      # Configuration analyzer
    └── fix_bgp_config.sh          # Automated fix script
```

#### Security Considerations

- The SSH private key is stored as a GitHub Secret and never exposed in logs
- The private key is created with secure permissions (600) using `install` command
- The private key is removed from the runner after the workflow completes
- Configuration backups are created before any changes are applied
- Host keys are verified using ssh-keyscan (no StrictHostKeyChecking bypass)
- All FRR configuration files are set with appropriate permissions (640) and ownership (frr:frr)
- Workflow uses explicit minimal permissions (contents: read)

#### Troubleshooting

**SSH Connection Failed**
- Verify that `SERVER_HOST`, `SERVER_USER`, and `SSH_PRIVATE_KEY` secrets are correctly configured
- Ensure the SSH private key is in the correct format (PEM)
- Check that the server's SSH port (22) is accessible

**Configuration Validation Errors**
- Review the validation output in the workflow logs
- Fix errors in the configuration files before deploying
- Consider using the automated fixes option

**BGP Neighbors Not Established**
- Check network connectivity to peer IP addresses
- Verify that peer routers are configured and accepting connections
- Review firewall rules on both sides
- Check that interface IP addresses are correctly configured

**FRR Service Failed to Start**
- Review the systemd service logs on the server: `sudo journalctl -u frr -n 50`
- Check FRR daemon logs: `/var/log/frr/bgpd.log` and `/var/log/frr/zebra.log`
- Verify configuration syntax using: `sudo vtysh -f /etc/frr/bgpd.conf -C`

#### Best Practices

1. **Test in a non-production environment first**: Always test configuration changes in a staging environment
2. **Review validation output**: Check validation results before applying fixes
3. **Monitor after deployment**: Watch BGP session establishment and route propagation after deployment
4. **Keep backups**: The workflow creates backups, but maintain your own backup strategy as well
5. **Use version control**: Keep all configuration changes in Git for traceability
6. **Gradual rollout**: When making significant changes, consider deploying to one router at a time

#### Customization

You can customize the workflow by:

- Modifying the validation and analysis scripts to add more checks
- Adding additional post-deployment verification steps
- Integrating with monitoring systems to track deployment success
- Adding notification steps (e.g., Slack, email) for deployment status
- Customizing the fix script to handle additional configuration issues

## Contributing

To add new workflows or improve existing ones:

1. Create or modify the workflow YAML file in `.github/workflows/`
2. Test the workflow in a fork or feature branch
3. Document any new secrets or requirements
4. Submit a pull request with your changes

## Support

For issues or questions about the workflows:

1. Check the troubleshooting section above
2. Review the workflow logs in the GitHub Actions tab
3. Consult the FRR documentation at https://frrouting.org/
4. Open an issue in the repository with detailed information about the problem
