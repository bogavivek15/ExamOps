"""
Provision Platform Administrator in auth.users
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import execute_query, execute_mutation

def main():
    admin_email = os.getenv("PLATFORM_ADMIN_EMAIL", "admin@examops.institution.edu")
    admin_id = "adb5e511-f32a-51e5-8006-38eda2aa3d52"
    password = os.getenv("PLATFORM_ADMIN_PASSWORD", "ExamOps@Admin2026!")
    display_name = "Chief Platform Administrator"

    print(f"Provisioning {admin_email} with ID {admin_id}...")

    existing = execute_query(
        "SELECT id, email FROM auth.users WHERE LOWER(email) = %s;",
        (admin_email.lower(),),
        fetch_one=True
    )

    if not existing:
        execute_mutation(
            """
            INSERT INTO auth.users (
                id, instance_id, aud, role, email, encrypted_password,
                email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
                is_super_admin, is_sso_user, is_anonymous, created_at, updated_at
            ) VALUES (
                %s, '00000000-0000-0000-0000-000000000000',
                'authenticated', 'authenticated', %s,
                crypt(%s, gen_salt('bf', 10)), NOW(),
                '{"provider":"email","providers":["email"]}'::jsonb,
                jsonb_build_object('display_name', %s),
                false, false, false, NOW(), NOW()
            );
            """,
            (admin_id, admin_email, password, display_name)
        )
        execute_mutation(
            """
            INSERT INTO auth.identities (
                id, user_id, identity_data, provider, provider_id, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), %s, jsonb_build_object('sub', %s::text, 'email', %s),
                'email', %s::text, NOW(), NOW()
            );
            """,
            (admin_id, admin_id, admin_email, admin_id)
        )
        print("Inserted new auth.users and auth.identities record.")
    else:
        execute_mutation(
            """
            UPDATE auth.users
            SET encrypted_password = crypt(%s, gen_salt('bf', 10)),
                email_confirmed_at = COALESCE(email_confirmed_at, NOW()),
                updated_at = NOW()
            WHERE id = %s;
            """,
            (password, str(existing['id']))
        )
        print("Updated existing auth.users password.")

    # Also verify evaluator@examops.edu password
    evaluator_email = "evaluator@examops.edu"
    evaluator_id = "d88e966e-d605-40b0-8213-fa40e63e9f98"
    eval_pwd = os.getenv("EVALUATOR_PASSWORD", "ExamOps@Admin2026!")
    execute_mutation(
        """
        UPDATE auth.users
        SET encrypted_password = crypt(%s, gen_salt('bf', 10)),
            email_confirmed_at = COALESCE(email_confirmed_at, NOW()),
            updated_at = NOW()
        WHERE LOWER(email) = %s;
        """,
        (eval_pwd, evaluator_email.lower())
    )
    print(f"Updated {evaluator_email} password.")

    print("SUCCESSFULLY PROVISIONED CREDENTIALS.")

if __name__ == "__main__":
    main()
