"""
Credential handling utilities for OMST AVR Tool.
"""
import os
import getpass
import keyring

KEYRING_SERVICE = "omst-avrtool"
ENV_USERNAME = "OMST_AVR_USERNAME"
ENV_PASSWORD = "OMST_AVR_PASSWORD"


def get_credentials(share_name):
    """
    Get credentials for accessing network shares.
    
    Tries to retrieve credentials in the following order:
    1. Environment variables
    2. Keyring/password store
    3. Prompt user for input
    
    Args:
        share_name: Name of the share for keyring storage
        
    Returns:
        tuple: (username, password)
    """
    keyring.get_keyring()  # Ensure keyring is initialized
    # Try environment variables first
    username = os.environ.get(ENV_USERNAME)
    password = os.environ.get(ENV_PASSWORD)
    
    if username and password:
        return username, password
    
    # Try keyring
    if not username:
        username = keyring.get_password(KEYRING_SERVICE, f"{share_name}_username")
    if not password:
        password = keyring.get_password(KEYRING_SERVICE, f"{share_name}_password")
    
    # If still not found, prompt user
    if not username:
        username = input(f"Username for {share_name}: ")
        save = input("Save username for future use? (y/n): ").lower() == 'y'
        if save:
            keyring.set_password(KEYRING_SERVICE, f"{share_name}_username", username)
    
    if not password:
        password = getpass.getpass(f"Password for {share_name}: ")
        save = input("Save password for future use? (y/n): ").lower() == 'y'
        if save:
            keyring.set_password(KEYRING_SERVICE, f"{share_name}_password", password)
    
    return username, password