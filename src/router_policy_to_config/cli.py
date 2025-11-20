"""
Command-line interface for router-policy-to-config.

Provides commands for policy validation, rendering, diff, and testing.
"""

import sys
from pathlib import Path
from typing import Optional
import argparse

from .policy_loader import load_policy_yaml, PolicyLoadError
from .policy_validator import validate_policy, ValidationError
from .backends.routeros_backend import RouterOSBackend
from .backends.openwrt_backend import OpenWrtBackend


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a policy file."""
    try:
        policy = load_policy_yaml(Path(args.policy))
        print(f"✓ Policy loaded successfully: {policy.meta.name}")
        
        errors = validate_policy(policy)
        if errors:
            print(f"\n✗ Validation failed with {len(errors)} error(s):")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        print("✓ Policy is valid")
        return 0
    except PolicyLoadError as e:
        print(f"✗ Failed to load policy: {e}", file=sys.stderr)
        return 1


def cmd_render(args: argparse.Namespace) -> int:
    """Render configuration from policy."""
    try:
        policy = load_policy_yaml(Path(args.policy), resolve_secrets=True)
        
        # Validate first
        errors = validate_policy(policy)
        if errors:
            print(f"✗ Policy validation failed with {len(errors)} error(s):")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        # Render based on target
        target = args.target
        if not target and policy.meta.target:
            target = policy.meta.target.vendor.value
        
        if not target:
            print("✗ No target specified. Use --target or set meta.target in policy", file=sys.stderr)
            return 1
        
        if target == "routeros":
            backend = RouterOSBackend()
            config = backend.render(policy)
            
            output_path = Path(args.out) if args.out else Path("routeros-config.rsc")
            with open(output_path, 'w') as f:
                f.write(config)
            print(f"✓ RouterOS configuration written to {output_path}")
            
        elif target == "openwrt":
            backend = OpenWrtBackend()
            configs = backend.render(policy)
            
            output_dir = Path(args.out) if args.out else Path("openwrt-config")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for filename, content in configs.items():
                file_path = output_dir / filename
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✓ Created {file_path}")
            
        else:
            print(f"✗ Unknown target: {target}", file=sys.stderr)
            return 1
        
        return 0
        
    except PolicyLoadError as e:
        print(f"✗ Failed to load policy: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Failed to render configuration: {e}", file=sys.stderr)
        return 1


def cmd_diff(args: argparse.Namespace) -> int:
    """Show diff between policy and current config."""
    print("✓ Diff command (not yet implemented)")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a new policy file."""
    output = Path(args.output) if args.output else Path("policy.yaml")
    
    if output.exists() and not args.force:
        print(f"✗ File already exists: {output}. Use --force to overwrite.", file=sys.stderr)
        return 1
    
    # Create a minimal policy template
    template = """meta:
  name: my-router
  description: My router configuration
  target:
    vendor: routeros
    version: v7

wan:
  type: dhcp
  interface: ether1

lans:
  - name: main
    subnet: 192.168.1.0/24
    gateway: 192.168.1.1
    dhcp:
      enabled: true
      range: 192.168.1.100-192.168.1.200
      lease_time: 24h

firewall:
  default_policy: drop
  rules:
    - name: allow_lan_to_internet
      from: [main]
      to: [wan]
      action: accept

nat:
  masquerade: true
"""
    
    with open(output, 'w') as f:
        f.write(template)
    
    print(f"✓ Created policy template: {output}")
    print("\nNext steps:")
    print(f"  1. Edit {output} to configure your network")
    print(f"  2. Validate with: router-policy validate {output}")
    print(f"  3. Render with: router-policy render {output} --target routeros")
    return 0


def cmd_ai_suggest(args: argparse.Namespace) -> int:
    """Generate policy from natural language description."""
    print("✓ AI suggest command (not yet implemented)")
    print("  This will use AI to convert natural language to policy YAML")
    return 0


def cmd_lab_test(args: argparse.Namespace) -> int:
    """Run lab tests."""
    print("✓ Lab test command (not yet implemented)")
    print("  This will test the policy in a Docker/QEMU lab environment")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="router-policy",
        description="AI-assisted copilot for router configuration"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize a new policy file')
    init_parser.add_argument('-o', '--output', help='Output file (default: policy.yaml)')
    init_parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing file')
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a policy file')
    validate_parser.add_argument('policy', help='Path to policy YAML file')
    
    # render command
    render_parser = subparsers.add_parser('render', help='Render configuration from policy')
    render_parser.add_argument('policy', help='Path to policy YAML file')
    render_parser.add_argument('-t', '--target', choices=['routeros', 'openwrt'],
                              help='Target vendor (overrides policy.meta.target)')
    render_parser.add_argument('-o', '--out', help='Output file or directory')
    
    # diff command
    diff_parser = subparsers.add_parser('diff', help='Show diff vs current config')
    diff_parser.add_argument('policy', help='Path to policy YAML file')
    diff_parser.add_argument('-t', '--target', choices=['routeros', 'openwrt'], required=True)
    diff_parser.add_argument('-c', '--current', required=True, help='Current config file/directory')
    
    # ai-suggest command
    ai_parser = subparsers.add_parser('ai-suggest', help='Generate policy from text description')
    ai_parser.add_argument('--from-text', required=True, help='Input text file with description')
    ai_parser.add_argument('-o', '--out', help='Output policy file')
    
    # lab-test command
    lab_parser = subparsers.add_parser('lab-test', help='Run lab tests')
    lab_parser.add_argument('policy', help='Path to policy YAML file')
    lab_parser.add_argument('--scenarios', help='Custom test scenarios file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handlers
    commands = {
        'init': cmd_init,
        'validate': cmd_validate,
        'render': cmd_render,
        'diff': cmd_diff,
        'ai-suggest': cmd_ai_suggest,
        'lab-test': cmd_lab_test,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
