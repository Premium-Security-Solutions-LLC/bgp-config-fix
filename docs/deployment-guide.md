# FRR Deployment Guide

This guide explains how to use the automated GitHub Actions workflow to deploy FRR configurations to your Linux servers.

## Overview

The deployment workflow automates the entire process of:
- Validating configuration files
- Analyzing BGP and GRE tunnel setups
- Applying automated fixes
- Deploying configurations to production servers
- Restarting services
- Verifying connectivity and route propagation

## Prerequisites

### 1. Target Server Requirements

Your Linux server must have:

- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+, or similar)
- **FRR Version**: 7.5 or higher (recommended: latest stable)
- **Python**: Python 3.6 or higher
- **SSH**: OpenSSH server running
- **Permissions**: User with sudo access

### 2. Server Setup

Install FRR on your target server:

**Ubuntu/Debian:**
```bash
# Add FRR GPG key
curl -s https://deb.frrouting.org/frr/keys.asc | gpg --dearmor | sudo tee /usr/share/keyrings/frrouting.gpg > /dev/null

# Add FRR repository
echo "deb [signed-by=/usr/share/keyrings/frrouting.gpg] https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable" | sudo tee -a /etc/apt/sources.list.d/frr.list

# Install FRR
sudo apt update
sudo apt install frr frr-pythontools -y

# Enable daemons
sudo sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons
sudo sed -i 's/zebra=no/zebra=yes/' /etc/frr/daemons

# Start FRR service
sudo systemctl enable frr
sudo systemctl start frr
```

**CentOS/RHEL:**
```bash
# Add FRR repository
curl -O https://rpm.frrouting.org/repo/frr-stable-repo-1-0.el8.noarch.rpm
sudo dnf install frr-stable-repo-1-0.el8.noarch.rpm -y

# Install FRR
sudo dnf install frr frr-pythontools -y

# Enable daemons
sudo sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons
sudo sed -i 's/zebra=no/zebra=yes/' /etc/frr/daemons

# Start FRR service
sudo systemctl enable frr
sudo systemctl start frr
```

### 3. SSH Key Setup

Generate an SSH key pair for GitHub Actions (using modern Ed25519 for better security):

```bash
# On your local machine - recommended: Ed25519 key
ssh-keygen -t ed25519 -f ~/.ssh/github_actions_key -N ""

# Alternative: RSA 4096 (if Ed25519 is not supported)
# ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_key -N ""

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/github_actions_key.pub user@your-server.com

# Test the connection
ssh -i ~/.ssh/github_actions_key user@your-server.com
```

### 4. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each of the following:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SERVER_HOST` | Server hostname or IP | `bgp-router.example.com` or `203.0.113.10` |
| `SERVER_USER` | SSH username | `admin` or `ubuntu` |
| `SSH_PRIVATE_KEY` | SSH private key content | Contents of `~/.ssh/github_actions_key` |

To get your private key content:
```bash
cat ~/.ssh/github_actions_key
```

Copy the entire output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) and paste it as the `SSH_PRIVATE_KEY` secret value.

## Configuration Files

### Prepare Your Configurations

Before running the deployment, ensure your configuration files are properly set up:

1. **Edit `configs/frr/bgpd.conf`**:
   - Set your AS number
   - Configure your BGP neighbors
   - Define route-maps and prefix-lists
   - Set your router-id

2. **Edit `configs/frr/zebra.conf`**:
   - Configure network interfaces
   - Set IP addresses
   - Define static routes (if needed)

### Validation

Before deployment, validate your configurations locally:

```bash
# Validate BGP configuration
python3 scripts/validate_bgp_config.py configs/frr/bgpd.conf

# Analyze configurations
python3 scripts/analyze_frr_config.py configs/frr/bgpd.conf configs/frr/zebra.conf

# Apply and test fixes (optional)
scripts/fix_bgp_config.sh --backup --validate configs/frr/bgpd.conf
```

## Running the Deployment

### Option 1: Manual Workflow Dispatch (Recommended)

1. Navigate to your repository on GitHub
2. Click the "Actions" tab
3. Select "Deploy FRR Configuration" from the workflows list
4. Click "Run workflow" button
5. Configure options:
   - **Apply automated fixes**: ✓ (recommended for first deployment)
   - **Restart FRR services**: ✓ (required for changes to take effect)
6. Click "Run workflow"

### Option 2: Automated Deployment (Advanced)

You can trigger the workflow automatically by modifying the workflow file to include additional triggers:

```yaml
on:
  workflow_dispatch:
    # ... existing configuration ...
  push:
    branches:
      - main
    paths:
      - 'configs/frr/**'
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
```

## Monitoring the Deployment

### Viewing Logs

1. Click on the running workflow in the Actions tab
2. Click on the job name ("Deploy and Validate FRR Configuration")
3. Expand each step to view detailed output

### Key Sections to Monitor

- **Validate BGP configuration**: Check for errors and warnings
- **Analyze FRR configuration**: Review peer summary and recommendations
- **Apply configuration fixes**: See what changes were made
- **Check BGP neighbor status**: Verify neighbors are established
- **Perform connectivity checks**: Ensure network connectivity

## Post-Deployment Verification

After the deployment completes successfully:

### 1. Verify BGP Sessions

Connect to your server and check BGP status:

```bash
# Check BGP summary
sudo vtysh -c "show ip bgp summary"

# Check specific neighbor
sudo vtysh -c "show ip bgp neighbors 10.0.1.2"

# Check BGP routes
sudo vtysh -c "show ip bgp"
```

### 2. Verify Route Propagation

```bash
# Check advertised routes
sudo vtysh -c "show ip bgp neighbors 10.0.1.2 advertised-routes"

# Check received routes
sudo vtysh -c "show ip bgp neighbors 10.0.1.2 routes"
```

### 3. Check Interface Status

```bash
# View interface status
ip addr show

# Check routing table
ip route show

# Verify FRR is managing routes
sudo vtysh -c "show ip route"
```

### 4. Test Connectivity

```bash
# Ping BGP peers
ping -c 4 10.0.1.2

# Trace route to a destination
traceroute 8.8.8.8

# Check for packet loss
mtr -r -c 10 10.0.1.2
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: SSH Connection Failed

**Symptoms:**
- "Permission denied" errors
- "Connection refused" errors

**Solutions:**
1. Verify SSH key is correctly formatted in GitHub Secrets
2. Ensure the public key is in `~/.ssh/authorized_keys` on the server
3. Check SSH service is running: `sudo systemctl status sshd`
4. Verify firewall allows SSH: `sudo ufw status` or `sudo firewall-cmd --list-all`

#### Issue: BGP Neighbors Not Establishing

**Symptoms:**
- Neighbors show "Idle" or "Active" state
- No routes received

**Solutions:**
1. Check network connectivity to peer: `ping <peer-ip>`
2. Verify peer is configured correctly on remote side
3. Check firewall allows BGP (TCP port 179): `sudo iptables -L -n | grep 179`
4. Review BGP logs: `sudo tail -f /var/log/frr/bgpd.log`
5. Check interface status: `ip addr show`

#### Issue: Configuration Validation Errors

**Symptoms:**
- Workflow fails at validation step
- Errors reported in configuration

**Solutions:**
1. Review validation output in workflow logs
2. Fix errors in configuration files
3. Run validation locally before deploying
4. Use automated fixes: enable "Apply automated fixes" option

#### Issue: FRR Service Won't Start

**Symptoms:**
- Service shows as "failed"
- Deployment completes but BGP not working

**Solutions:**
1. Check service status: `sudo systemctl status frr`
2. Review service logs: `sudo journalctl -u frr -n 50`
3. Check FRR daemon logs: `sudo tail -f /var/log/frr/*.log`
4. Validate configuration syntax: `sudo vtysh -f /etc/frr/bgpd.conf -C`
5. Ensure daemons are enabled in `/etc/frr/daemons`

#### Issue: Routes Not Propagating

**Symptoms:**
- BGP sessions established but no routes
- Routes not appearing in routing table

**Solutions:**
1. Check if networks are configured: `sudo vtysh -c "show run" | grep network`
2. Verify route-maps are not blocking: `sudo vtysh -c "show route-map"`
3. Check maximum-prefix limits: `sudo vtysh -c "show ip bgp neighbors" | grep "Maximum prefixes"`
4. Review prefix-lists: `sudo vtysh -c "show ip prefix-list"`
5. Check if routes are being filtered: `sudo vtysh -c "show ip bgp neighbors <peer> routes"`

## Best Practices

### Before Deployment

1. **Test in staging**: Always test configuration changes in a non-production environment first
2. **Review changes**: Use `git diff` to review all configuration changes
3. **Validate locally**: Run validation and analysis scripts before deploying
4. **Plan maintenance window**: Schedule deployments during low-traffic periods
5. **Notify stakeholders**: Inform relevant parties about the deployment

### During Deployment

1. **Monitor logs**: Watch the GitHub Actions logs in real-time
2. **Be ready to rollback**: Keep previous configuration backups accessible
3. **Stay available**: Be ready to troubleshoot if issues arise
4. **Monitor BGP sessions**: Watch for neighbor state changes

### After Deployment

1. **Verify all neighbors**: Ensure all BGP sessions are established
2. **Check route counts**: Verify expected number of routes are received
3. **Test connectivity**: Perform connectivity tests to critical destinations
4. **Monitor for 24 hours**: Watch for any unexpected behavior
5. **Document changes**: Update documentation with any configuration changes made

## Rollback Procedures

If you need to rollback a deployment:

### Quick Rollback

The workflow automatically creates backups before deployment. To restore:

```bash
# SSH to the server
ssh user@your-server.com

# Find the backup
ls -la /etc/frr/backups/

# Restore the backup
sudo cp /etc/frr/backups/bgpd.conf.backup-YYYYMMDD-HHMMSS /etc/frr/bgpd.conf
sudo cp /etc/frr/backups/zebra.conf.backup-YYYYMMDD-HHMMSS /etc/frr/zebra.conf

# Restart FRR
sudo systemctl restart frr

# Verify
sudo vtysh -c "show ip bgp summary"
```

### Git-based Rollback

If you need to redeploy a previous version:

1. Revert the commit in Git:
   ```bash
   git revert <commit-hash>
   git push
   ```

2. Run the deployment workflow again with the reverted configuration

## Advanced Topics

### Multiple Server Deployment

To deploy to multiple servers, create separate workflow files or use matrix strategy:

```yaml
strategy:
  matrix:
    server:
      - host: server1.example.com
        user: admin
      - host: server2.example.com
        user: admin
```

### Monitoring Integration

Integrate with monitoring systems:

```yaml
- name: Send deployment notification
  run: |
    curl -X POST https://monitoring.example.com/api/deployments \
      -H "Content-Type: application/json" \
      -d '{"service": "frr", "status": "deployed", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
```

### Automated Testing

Add automated tests after deployment:

```yaml
- name: Run integration tests
  run: |
    ssh ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} "
      # Test BGP session establishment
      if sudo vtysh -c 'show ip bgp summary' | grep -q 'Established'; then
        echo 'BGP sessions established'
        exit 0
      else
        echo 'BGP sessions not established'
        exit 1
      fi
    "
```

## Security Considerations

1. **Secure Secrets**: Never commit SSH keys or credentials to Git
2. **Limit Access**: Restrict who can run the deployment workflow
3. **Audit Logs**: Review GitHub Actions logs regularly
4. **Key Rotation**: Rotate SSH keys periodically
5. **Principle of Least Privilege**: Use a dedicated user with minimal required permissions
6. **Network Segmentation**: Deploy from trusted networks only

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review the workflow README: `.github/workflows/README.md`
3. Consult FRR documentation: https://docs.frrouting.org/
4. Open an issue on GitHub with:
   - Workflow logs
   - Server information (OS, FRR version)
   - Configuration files (sanitized)
   - Error messages

## Additional Resources

- [FRR Documentation](https://docs.frrouting.org/)
- [BGP Configuration Guide](https://docs.frrouting.org/en/latest/bgp.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Repository README](../README.md)
- [Copilot Usage Guide](./copilot-guide.md)
