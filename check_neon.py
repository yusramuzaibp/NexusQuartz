from database.database import get_connection

with get_connection() as conn:
    with conn.cursor() as cursor:
        for table in ("users", "predictions"):
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position
            """, (table,))

            print(f"\n{table} columns:")
            for column in cursor.fetchall():
                print(column)
