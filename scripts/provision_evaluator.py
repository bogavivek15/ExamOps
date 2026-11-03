"""
ExamOps Evaluator Account Provisioning Script
Provisions or updates a dedicated Evaluator account with:
- Role: ACADEMIC_ADMINISTRATOR
- Display Name: ExamOps Evaluator
- Status: ACTIVE
- Linked Supabase Auth user record (auth.users and auth.identities)

Security Notice:
Credentials are read strictly from environment variables (EVALUATOR_EMAIL, EVALUATOR_PASSWORD)
or passed via CLI parameters during runtime. Never hardcode credentials into this script.
"""
import os
import sys
import secrets
import string
import psycopg2
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.config import settings

def generate_strong_password(length: int = 16) -> str:
    """Generates a cryptographically strong random password."""
    alphabet = string.ascii_letters + string.digits + "!@#%*="
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd)
            and any(c.isupper() for c in pwd)
            and any(c.isdigit() for c in pwd)
            and any(c in "!@#%*=" for c in pwd)):
            return pwd

def provision_evaluator(
    email: str = None,
    password: str = None,
    display_name: str = "ExamOps Evaluator",
):
    print("=" * 70)
    print("ExamOps — Dedicated Evaluator Account Provisioning")
    print("=" * 70)

    # Resolve email strictly from CLI parameter or environment variable
    target_email = email or os.getenv("EVALUATOR_EMAIL", "evaluator@examops.edu")
    email_clean = target_email.strip().lower()

    # Resolve password strictly from CLI parameter or environment variable
    target_password = password or os.getenv("EVALUATOR_PASSWORD")
    if not target_password:
        target_password = generate_strong_password()
        generated = True
    else:
        generated = False

    print(f"\nTarget Evaluator Email: {email_clean}")
    print(f"Target Role:            ACADEMIC_ADMINISTRATOR")
    print(f"Target Display Name:    {display_name}")

    if not settings.DATABASE_URL or "[YOUR-PASSWORD]" in settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured with a valid connection string.")

    conn = psycopg2.connect(settings.DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Step 1: Check if user exists in auth.users
        cur.execute("SELECT id, email, email_confirmed_at FROM auth.users WHERE LOWER(email) = %s;", (email_clean,))
        existing_auth_user = cur.fetchone()

        if existing_auth_user:
            auth_uid = str(existing_auth_user[0])
            print(f"\n[INFO] Existing auth.users record found: UID {auth_uid}")
            # Update password and confirm email
            cur.execute("""
                UPDATE auth.users
                SET encrypted_password = crypt(%s, gen_salt('bf', 10)),
                    email_confirmed_at = COALESCE(email_confirmed_at, NOW()),
                    raw_user_meta_data = jsonb_build_object('display_name', %s),
                    updated_at = NOW()
                WHERE id = %s;
            """, (target_password, display_name, auth_uid))
            print("[OK] Updated password and confirmed status in auth.users.")
        else:
            print("\n[INFO] Creating new auth.users record...")
            cur.execute("""
                INSERT INTO auth.users (
                    id, instance_id, aud, role, email, encrypted_password,
                    email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
                    is_super_admin, is_sso_user, is_anonymous, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), '00000000-0000-0000-0000-000000000000',
                    'authenticated', 'authenticated', %s,
                    crypt(%s, gen_salt('bf', 10)), NOW(),
                    '{"provider":"email","providers":["email"]}'::jsonb,
                    jsonb_build_object('display_name', %s),
                    false, false, false, NOW(), NOW()
                ) RETURNING id;
            """, (email_clean, target_password, display_name))
            auth_uid = str(cur.fetchone()[0])
            print(f"[OK] Created auth.users entry with UID: {auth_uid}")

            # Insert identity (email is GENERATED ALWAYS from identity_data->>'email')
            cur.execute("""
                INSERT INTO auth.identities (
                    id, user_id, identity_data, provider, provider_id, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), %s, jsonb_build_object('sub', %s::text, 'email', %s),
                    'email', %s::text, NOW(), NOW()
                );
            """, (auth_uid, auth_uid, email_clean, auth_uid))
            print("[OK] Created auth.identities entry for email provider.")

        # Step 2: Ensure user_profiles row exists and matches auth_uid
        cur.execute("SELECT id, email, role, status FROM user_profiles WHERE id = %s OR LOWER(email) = %s;", (auth_uid, email_clean))
        existing_profile = cur.fetchone()

        if existing_profile:
            cur.execute("""
                UPDATE user_profiles
                SET id = %s,
                    email = %s,
                    display_name = %s,
                    role = 'ACADEMIC_ADMINISTRATOR',
                    status = 'ACTIVE',
                    updated_at = NOW()
                WHERE id = %s OR LOWER(email) = %s;
            """, (auth_uid, email_clean, display_name, auth_uid, email_clean))
            print("[OK] Synchronized and updated existing user_profiles record to ACADEMIC_ADMINISTRATOR.")
        else:
            cur.execute("""
                INSERT INTO user_profiles (
                    id, email, display_name, role, status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, 'ACADEMIC_ADMINISTRATOR', 'ACTIVE', NOW(), NOW()
                );
            """, (auth_uid, email_clean, display_name))
            print("[OK] Inserted new user_profiles record linked to auth UID.")

        conn.commit()
        print("\n" + "=" * 70)
        print("EVALUATOR PROVISIONING SUCCESSFUL!")
        print("=" * 70)
        print(f"Auth UID:     {auth_uid}")
        print(f"Email:        {email_clean}")
        if generated:
            print(f"Password:     {target_password}  (generated)")
        else:
            print(f"Password:     [Provided via environment/argument]")
        print(f"Role:         ACADEMIC_ADMINISTRATOR")
        print(f"Status:       ACTIVE")
        print("=" * 70)
        return {"email": email_clean, "password": target_password, "auth_uid": auth_uid}

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Evaluator provisioning failed: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Provision ExamOps Evaluator Account")
    parser.add_argument("--email", default=None, help="Evaluator email (defaults to EVALUATOR_EMAIL env or evaluator@examops.edu)")
    parser.add_argument("--password", default=None, help="Evaluator password (defaults to EVALUATOR_PASSWORD env or auto-generated)")
    args = parser.parse_args()
    provision_evaluator(email=args.email, password=args.password)
