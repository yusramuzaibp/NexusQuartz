
from getpass import getpass

from auth.authentication import hash_password, validate_password
from database.database import get_connection

email = "admin@mdp.local"

password = getpass("Enter your NEW admin password: ")
confirm = getpass("Confirm your NEW admin password: ")

if password != confirm:
    print("ERROR: Passwords do not match.")

elif validate_password(password):
    print("ERROR: Password does not meet requirements:")
    for error in validate_password(password):
        print("-", error)

else:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password = %s
                WHERE email = %s AND role = 'admin'
                RETURNING id
                """,
                (hash_password(password), email)
            )

            result = cursor.fetchone()

    if result:
        print("SUCCESS: Admin password updated!")
    else:
        print("ERROR: Admin account not found.")
