import os

import click
from griddot.provision_keycloak import import_realm, get_user_uuid_by_username, get_access_token, delete_user
from griddot.tools import encrypt_secrets, create_new_key, decrypt_secrets


@click.group()
def cli():
    """CLI for GridDot platform tools"""
    pass


@cli.command("provision-keycloak", short_help="Provision Keycloak with realms and users")
@click.option('--url', help='Keycloak server URL')
@click.option('--username', help='User name')
@click.option('--password', help='Username password')
@click.option('--realms-dir', help='Path to the directory with realm JSON files')
@click.option('--delete-user-when-provisioned', type=click.Choice(['Yes', 'No'], case_sensitive=False), default='Yes')
@click.option('--email-password', help='Email provider password')
def provision(url, username, password, realms_dir, delete_user_when_provisioned, email_password):
    """Keycloak provisioning tool"""

    for realm_path in os.listdir(realms_dir):
        full_path = os.path.join(realms_dir, realm_path)
        print(f"Importing realm from {full_path}")
        import_realm(url, username, password, full_path, email_password, True)

    if delete_user_when_provisioned.lower() == 'yes':
        token = get_access_token(url, username, password)
        user_id = get_user_uuid_by_username(url, "master", token, username)
        delete_user(url, "master", token, user_id)
        print(f"Deleted user {username} from master realm.")


@cli.command("decrypt-secrets", short_help="Decrypt secrets files using the private key .secrets/key.pem")
@click.option('--file', '-f', multiple=True, help='Path to the encrypted secrets file(s)')
def decrypt_secrets_command(file: tuple[str]):
    decrypt_secrets(list(file))


@cli.command("create-key", short_help="Create a new RSA key pair: .secrets/key.pem and .secrets/key.pub")
def create_new_key_command():
    create_new_key()


@cli.command("encrypt-secrets", short_help="Encrypt secrets files using the public key .secrets/key.pub")
@click.option('--file', '-f', multiple=True, help='Path to the secrets file(s) to encrypt')
def encrypt_secrets_command(file: tuple[str]):
    encrypt_secrets(list(file))
