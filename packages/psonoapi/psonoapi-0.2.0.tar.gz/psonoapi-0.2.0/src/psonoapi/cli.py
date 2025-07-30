#!/usr/bin/env python3
"""
Psono CLI - Command line interface for Psono password manager
"""
import click
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from tabulate import tabulate
import getpass
from .psono import PsonoAPI
from .datamodels import PsonoServerConfig, psono_type_list
from .exceptions import PsonoException, PsonoPathNotFoundException, PsonoLoginException


# Configuration file path
CONFIG_DIR = Path.home() / '.psono'
CONFIG_FILE = CONFIG_DIR / 'config.json'


class Config:
    """CLI configuration management"""
    def __init__(self):
        self.api: Optional[PsonoAPI] = None
        self.config_data: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                self.config_data = json.load(f)
    
    def save_config(self):
        """Save configuration to file"""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=2)
        # Set restrictive permissions
        CONFIG_FILE.chmod(0o600)
    
    def get_api(self) -> PsonoAPI:
        """Get or create API instance"""
        if self.api is None:
            if not self.config_data:
                raise click.ClickException("Not configured. Run 'psono configure' first.")
            
            # Don't store sensitive keys in config, get them from env
            options = {
                'server_url': self.config_data.get('server_url'),
                'key_id': os.environ.get('PSONO_API_KEY_ID') or self.config_data.get('key_id'),
                'private_key': os.environ.get('PSONO_API_PRIVATE_KEY'),
                'secret_key': os.environ.get('PSONO_API_SECRET_KEY'),
                'ssl_verify': self.config_data.get('ssl_verify', True),
            }
            
            if not options['private_key']:
                raise click.ClickException(
                    "PSONO_API_PRIVATE_KEY environment variable not set. "
                    "Set it or use 'psono configure' to store credentials."
                )
            
            try:
                self.api = PsonoAPI(options)
            except PsonoLoginException as e:
                raise click.ClickException(f"Login failed: {str(e)}")
            except Exception as e:
                raise click.ClickException(f"Failed to connect: {str(e)}")
        
        return self.api


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug output')
@pass_config
def cli(config, debug):
    """Psono CLI - Secure password manager client"""
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option('--server-url', prompt=True, default='https://www.psono.pw/server', 
              help='Psono server URL')
@click.option('--key-id', prompt=True, help='API key ID')
@click.option('--private-key', prompt=True, hide_input=True, help='API private key')
@click.option('--secret-key', prompt=True, hide_input=True, help='API secret key')
@click.option('--ssl-verify/--no-ssl-verify', default=True, help='Verify SSL certificates')
@pass_config
def configure(config, server_url, key_id, private_key, secret_key, ssl_verify):
    """Configure Psono CLI"""
    # Test the configuration
    try:
        test_api = PsonoAPI({
            'server_url': server_url,
            'key_id': key_id,
            'private_key': private_key,
            'secret_key': secret_key,
            'ssl_verify': ssl_verify,
        })
        click.echo("✓ Successfully connected to Psono server")
    except Exception as e:
        raise click.ClickException(f"Failed to connect: {str(e)}")
    
    # Save configuration
    config.config_data = {
        'server_url': server_url,
        'ssl_verify': ssl_verify,
    }
    
    # Optionally store credentials (with warning)
    if click.confirm("Store API credentials in config file? (Less secure than environment variables)"):
        config.config_data['key_id'] = key_id
        # We could encrypt these, but for now just warn
        click.echo(click.style(
            "⚠️  Warning: Storing private keys in config file. Consider using environment variables instead:",
            fg='yellow'
        ))
        click.echo("  export PSONO_API_KEY_ID='your-key-id'")
        click.echo("  export PSONO_API_PRIVATE_KEY='your-private-key'")
        click.echo("  export PSONO_API_SECRET_KEY='your-secret-key'")
    else:
        click.echo("\nSet these environment variables:")
        click.echo(f"  export PSONO_API_KEY_ID='{key_id}'")
        click.echo(f"  export PSONO_API_PRIVATE_KEY='{private_key}'")
        click.echo(f"  export PSONO_API_SECRET_KEY='{secret_key}'")
    
    config.save_config()
    click.echo(f"\n✓ Configuration saved to {CONFIG_FILE}")


@cli.group()
def secret():
    """Manage secrets"""
    pass


@secret.command('list')
@click.argument('path', default='/')
@click.option('--recursive', '-r', is_flag=True, help='List recursively')
@click.option('--type', '-t', help='Filter by secret type')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'simple']), default='table')
@pass_config
def list_secrets(config, path, recursive, type, format):
    """List secrets and folders"""
    api = config.get_api()
    
    try:
        item = api.get_path(path)
    except PsonoPathNotFoundException:
        raise click.ClickException(f"Path not found: {path}")
    
    if hasattr(item, 'folders') or hasattr(item, 'items'):
        # It's a folder
        items = []
        
        # Add folders
        for folder in getattr(item, 'folders', []):
            if not folder.deleted:
                items.append({
                    'Type': 'folder',
                    'Name': folder.name,
                    'Path': folder.path or f"{path}/{folder.name}".replace('//', '/'),
                    'Shared': '✓' if folder.share_id else ''
                })
        
        # Add items
        for secret_item in getattr(item, 'items', []):
            if not secret_item.deleted and (not type or secret_item.type == type):
                items.append({
                    'Type': secret_item.type,
                    'Name': secret_item.name,
                    'Path': secret_item.path or f"{path}/{secret_item.name}".replace('//', '/'),
                    'Shared': ''
                })
        
        if format == 'json':
            click.echo(json.dumps(items, indent=2))
        elif format == 'simple':
            for item in items:
                click.echo(item['Path'])
        else:
            if items:
                click.echo(tabulate(items, headers='keys', tablefmt='grid'))
            else:
                click.echo("No items found")
    else:
        # It's a secret
        secret_data = api.get_path(path)
        if format == 'json':
            click.echo(secret_data.model_dump_json(indent=2))
        else:
            click.echo(f"Type: {secret_data.type}")
            click.echo(f"Path: {path}")
            if hasattr(secret_data, 'title') and secret_data.title:
                click.echo(f"Title: {secret_data.title}")


@secret.command('get')
@click.argument('path')
@click.option('--field', '-f', help='Get specific field')
@click.option('--show-password', '-p', is_flag=True, help='Show password in plain text')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
@pass_config
def get_secret(config, path, field, show_password, format):
    """Get a secret"""
    api = config.get_api()
    
    try:
        secret = api.get_path(path)
    except PsonoPathNotFoundException:
        raise click.ClickException(f"Secret not found: {path}")
    
    if format == 'json':
        data = secret.model_dump(exclude_none=True)
        if not show_password and 'password' in data:
            data['password'] = '********'
        click.echo(json.dumps(data, indent=2))
    else:
        if field:
            value = getattr(secret, field, None)
            if value is None and hasattr(secret, 'custom_fields_dict'):
                value = secret.custom_fields_dict.get(field)
            if value is None:
                raise click.ClickException(f"Field '{field}' not found")
            click.echo(value)
        else:
            # Display all fields
            click.echo(f"Type: {secret.type}")
            click.echo(f"Path: {path}")
            
            # Common fields
            if hasattr(secret, 'title') and secret.title:
                click.echo(f"Title: {secret.title}")
            if hasattr(secret, 'username') and secret.username:
                click.echo(f"Username: {secret.username}")
            if hasattr(secret, 'password') and secret.password:
                if show_password:
                    click.echo(f"Password: {secret.password}")
                else:
                    click.echo("Password: ********")
            if hasattr(secret, 'url') and secret.url:
                click.echo(f"URL: {secret.url}")
            if hasattr(secret, 'notes') and secret.notes:
                click.echo(f"Notes: {secret.notes}")
            
            # Custom fields
            if hasattr(secret, 'custom_fields') and secret.custom_fields:
                click.echo("\nCustom Fields:")
                for field in secret.custom_fields:
                    click.echo(f"  {field.name}: {field.value}")


@secret.command('create')
@click.argument('path')
@click.option('--type', '-t', type=click.Choice(list(psono_type_list)), 
              default='website_password', help='Secret type')
@click.option('--data', '-d', help='JSON data for the secret')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@pass_config
def create_secret(config, path, type, data, interactive):
    """Create a new secret"""
    api = config.get_api()
    
    secret_data = {
        'type': type,
        'path': path,
        'title': path.split('/')[-1]
    }
    
    if data:
        # Parse JSON data
        try:
            additional_data = json.loads(data)
            secret_data.update(additional_data)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON: {e}")
    elif interactive or not data:
        # Interactive mode
        click.echo(f"Creating {type} at {path}")
        
        if type == 'website_password':
            secret_data['username'] = click.prompt('Username', default='')
            secret_data['password'] = click.prompt('Password', hide_input=True, default='')
            secret_data['url'] = click.prompt('URL', default='')
            secret_data['notes'] = click.prompt('Notes', default='')
        elif type == 'note':
            secret_data['notes'] = click.edit('') or ''
        elif type == 'application_password':
            secret_data['username'] = click.prompt('Username', default='')
            secret_data['password'] = click.prompt('Password', hide_input=True, default='')
            secret_data['notes'] = click.prompt('Notes', default='')
        else:
            click.echo(f"Interactive mode not implemented for {type}")
            click.echo("Use --data with JSON instead")
            return
    
    try:
        result = api.write_secret(secret_data)
        if result.get('updated'):
            click.echo(f"✓ Updated existing secret at {path}")
        else:
            click.echo(f"✓ Created secret at {path}")
    except Exception as e:
        raise click.ClickException(f"Failed to create secret: {e}")


@secret.command('update')
@click.argument('path')
@click.option('--data', '-d', required=True, help='JSON data to update')
@pass_config
def update_secret(config, path, data):
    """Update an existing secret"""
    api = config.get_api()
    
    try:
        secret = api.get_path(path)
    except PsonoPathNotFoundException:
        raise click.ClickException(f"Secret not found: {path}")
    
    try:
        update_data = json.loads(data)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")
    
    # Update fields
    for key, value in update_data.items():
        if hasattr(secret, key):
            setattr(secret, key, value)
    
    try:
        api.update_secret(secret)
        click.echo(f"✓ Updated secret at {path}")
    except Exception as e:
        raise click.ClickException(f"Failed to update secret: {e}")


@secret.command('delete')
@click.argument('path')
@click.confirmation_option(prompt='Are you sure you want to delete this secret?')
@pass_config
def delete_secret(config, path):
    """Delete a secret"""
    api = config.get_api()
    
    try:
        api.delete_secret(path)
        click.echo(f"✓ Deleted secret at {path}")
    except Exception as e:
        raise click.ClickException(f"Failed to delete secret: {e}")


@secret.command('search')
@click.argument('query')
@click.option('--type', '-t', help='Filter by secret type')
@click.option('--field', '-f', default='title', help='Field to search in')
@pass_config
def search_secrets(config, query, type, field):
    """Search for secrets"""
    api = config.get_api()
    
    # For now, we'll do a simple implementation
    # In a real implementation, we'd want to search across all datastores
    click.echo(f"Searching for '{query}' in {field}...")
    
    # Get all datastores and search
    results = []
    
    def search_folder(folder, base_path=''):
        for item in getattr(folder, 'items', []):
            if item.deleted or (type and item.type != type):
                continue
            
            # Get the full secret to search fields
            try:
                secret = api.get_path(item.path)
                value = getattr(secret, field, '')
                if query.lower() in str(value).lower():
                    results.append({
                        'Path': item.path,
                        'Type': item.type,
                        'Name': item.name,
                        field.title(): str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                    })
            except:
                pass
        
        for subfolder in getattr(folder, 'folders', []):
            if not subfolder.deleted:
                search_folder(subfolder, f"{base_path}/{subfolder.name}")
    
    try:
        datastore = api.get_datastore()
        search_folder(datastore)
        
        if results:
            click.echo(tabulate(results, headers='keys', tablefmt='grid'))
        else:
            click.echo("No results found")
    except Exception as e:
        raise click.ClickException(f"Search failed: {e}")


@cli.group()
def folder():
    """Manage folders"""
    pass


@folder.command('create')
@click.argument('path')
@pass_config
def create_folder(config, path):
    """Create a folder"""
    api = config.get_api()
    
    # Create a dummy secret to force folder creation
    dummy_path = f"{path}/.placeholder"
    try:
        api.write_secret({
            'type': 'note',
            'path': dummy_path,
            'notes': 'Placeholder for folder creation'
        })
        # Immediately delete it
        api.delete_secret(dummy_path)
        click.echo(f"✓ Created folder at {path}")
    except Exception as e:
        raise click.ClickException(f"Failed to create folder: {e}")


@cli.command('export')
@click.option('--output', '-o', type=click.File('w'), default='-', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
@click.option('--include-passwords', is_flag=True, help='Include passwords in export')
@pass_config
def export_data(config, output, format, include_passwords):
    """Export all secrets"""
    api = config.get_api()
    
    click.echo("Exporting data...", err=True)
    
    all_secrets = []
    
    def collect_secrets(folder, base_path=''):
        for item in getattr(folder, 'items', []):
            if not item.deleted:
                try:
                    secret = api.get_path(item.path)
                    secret_dict = secret.model_dump(exclude_none=True)
                    if not include_passwords and 'password' in secret_dict:
                        secret_dict['password'] = '********'
                    all_secrets.append(secret_dict)
                except:
                    pass
        
        for subfolder in getattr(folder, 'folders', []):
            if not subfolder.deleted:
                collect_secrets(subfolder, f"{base_path}/{subfolder.name}")
    
    try:
        datastore = api.get_datastore()
        collect_secrets(datastore)
        
        if format == 'json':
            json.dump(all_secrets, output, indent=2)
        else:
            # CSV export (simplified)
            import csv
            if all_secrets:
                fieldnames = set()
                for s in all_secrets:
                    fieldnames.update(s.keys())
                writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(all_secrets)
        
        click.echo(f"✓ Exported {len(all_secrets)} secrets", err=True)
    except Exception as e:
        raise click.ClickException(f"Export failed: {e}")


@cli.command('import')
@click.option('--input', '-i', type=click.File('r'), default='-', help='Input file')
@click.option('--format', '-f', type=click.Choice(['json']), default='json')
@click.option('--dry-run', is_flag=True, help='Show what would be imported without doing it')
@pass_config
def import_data(config, input, format, dry_run):
    """Import secrets from file"""
    api = config.get_api()
    
    if dry_run:
        # Create API in test mode
        api.session.server.test_mode = True
    
    try:
        data = json.load(input)
        if not isinstance(data, list):
            raise click.ClickException("Expected a list of secrets")
        
        created = 0
        updated = 0
        errors = 0
        
        with click.progressbar(data, label='Importing secrets') as secrets:
            for secret_data in secrets:
                try:
                    result = api.write_secret(secret_data)
                    if result.get('updated'):
                        updated += 1
                    else:
                        created += 1
                except Exception as e:
                    errors += 1
                    click.echo(f"\nError importing {secret_data.get('path', 'unknown')}: {e}", err=True)
        
        click.echo(f"\n✓ Import complete: {created} created, {updated} updated, {errors} errors")
        
        if dry_run:
            click.echo("(This was a dry run - no changes were made)")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")
    except Exception as e:
        raise click.ClickException(f"Import failed: {e}")


@cli.command()
@click.argument('url')
@pass_config
def find_by_url(config, url):
    """Find secrets matching a URL"""
    api = config.get_api()
    
    try:
        matches = api.search_urlfilter(url)
        if matches:
            results = []
            for secret in matches:
                results.append({
                    'Path': secret.path,
                    'Username': getattr(secret, 'username', 'N/A'),
                    'URL': getattr(secret, 'url', 'N/A'),
                    'Title': getattr(secret, 'title', 'N/A')
                })
            click.echo(tabulate(results, headers='keys', tablefmt='grid'))
        else:
            click.echo("No matches found")
    except Exception as e:
        raise click.ClickException(f"Search failed: {e}")


@cli.command()
@pass_config
def status(config):
    """Show connection status and statistics"""
    try:
        api = config.get_api()
        click.echo("✓ Connected to Psono server")
        click.echo(f"  Server: {api.session.server.server_url}")
        click.echo(f"  User: {api.session.username}")
        
        # Count items
        datastore = api.get_datastore()
        
        def count_items(folder):
            items = 0
            folders = 0
            for item in getattr(folder, 'items', []):
                if not item.deleted:
                    items += 1
            for subfolder in getattr(folder, 'folders', []):
                if not subfolder.deleted:
                    folders += 1
                    sub_items, sub_folders = count_items(subfolder)
                    items += sub_items
                    folders += sub_folders
            return items, folders
        
        items, folders = count_items(datastore)
        click.echo(f"\n📊 Statistics:")
        click.echo(f"  Secrets: {items}")
        click.echo(f"  Folders: {folders}")
        
    except Exception as e:
        click.echo(f"✗ Not connected: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()