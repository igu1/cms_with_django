#!/usr/bin/env python3
"""
Script to generate a secure Django secret key and update the .env file.
"""

import os
import sys
import re
from django.core.management.utils import get_random_secret_key

def generate_secret_key():
    """Generate a secure Django secret key."""
    return get_random_secret_key()

def update_env_file(env_file, new_secret_key):
    """Update the SECRET_KEY in the .env file."""
    if not os.path.exists(env_file):
        print(f"Error: {env_file} not found!")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the SECRET_KEY line
    pattern = r'SECRET_KEY=.*'
    replacement = f'SECRET_KEY={new_secret_key}'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        with open(env_file, 'w') as f:
            f.write(new_content)
        return True
    else:
        print(f"Error: SECRET_KEY line not found in {env_file}")
        return False

def main():
    """Main function."""
    # Check if an env file was specified
    if len(sys.argv) > 1:
        env_file = sys.argv[1]
    else:
        env_file = '.env'
    
    # Generate a new secret key
    new_secret_key = generate_secret_key()
    
    # Update the .env file
    if update_env_file(env_file, new_secret_key):
        print(f"✅ SECRET_KEY updated in {env_file}")
        print(f"New SECRET_KEY: {new_secret_key}")
    else:
        print("❌ Failed to update SECRET_KEY")
        print(f"Generated SECRET_KEY: {new_secret_key}")
        print("You can manually add this to your .env file")

if __name__ == "__main__":
    main()
