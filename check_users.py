from database.database import get_connection

with get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)

        for row in cursor.fetchall():
            print(row[0])