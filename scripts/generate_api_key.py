#!/usr/bin/env python3
"""
Generate API keys for portal users.
Creates secure random API keys that can be inserted into dbo.portal_users table.
"""

import secrets
import string

def generate_api_key(prefix="aicp", length=32):
    """Generate a secure random API key."""
    # Generate random alphanumeric string
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}_{random_part}"


def generate_multiple_keys(count=5):
    """Generate multiple API keys."""
    keys = []
    for i in range(count):
        key = generate_api_key()
        keys.append(key)
    return keys


if __name__ == "__main__":
    print("=" * 70)
    print("AICP API Key Generator")
    print("=" * 70)
    print()
    
    # Generate a single key
    print("Single API Key:")
    print("-" * 70)
    api_key = generate_api_key()
    print(f"  {api_key}")
    print()
    
    # Generate multiple keys
    print("Multiple API Keys (5):")
    print("-" * 70)
    keys = generate_multiple_keys(5)
    for i, key in enumerate(keys, 1):
        print(f"  {i}. {key}")
    print()
    
    # SQL Insert example
    print("=" * 70)
    print("SQL Insert Example:")
    print("=" * 70)
    print()
    print("-- For a Doctor:")
    print(f"""
INSERT INTO dbo.portal_users 
    (display_name, role, doctor_id, pharmacy_id, api_key, is_active)
VALUES 
    ('Dr. John Smith', 'doctor', 1, NULL, '{api_key}', 1);
""")
    
    print("-- For a Pharmacy:")
    pharmacy_key = generate_api_key()
    print(f"""
INSERT INTO dbo.portal_users 
    (display_name, role, doctor_id, pharmacy_id, api_key, is_active)
VALUES 
    ('Downtown Pharmacy', 'pharmacy', NULL, 5, '{pharmacy_key}', 1);
""")
    
    print("-- For an Admin:")
    admin_key = generate_api_key()
    print(f"""
INSERT INTO dbo.portal_users 
    (display_name, role, doctor_id, pharmacy_id, api_key, is_active)
VALUES 
    ('System Admin', 'admin', NULL, NULL, '{admin_key}', 1);
""")
    
    print("=" * 70)
    print("Note: Run these SQL statements in your database to create users.")
    print("=" * 70)
