#!/usr/bin/env python3
"""
Generate a secret key for JWT tokens.
Run this and copy the output to your .env file.
"""

import secrets

if __name__ == "__main__":
    print("=" * 60)
    print("JWT Secret Key Generator")
    print("=" * 60)
    print("\nGenerating a secure random key...\n")
    
    secret_key = secrets.token_hex(32)
    
    print(f"JWT_SECRET_KEY={secret_key}")
    print("\n" + "=" * 60)
    print("Copy the line above to your .env file")
    print("=" * 60)
