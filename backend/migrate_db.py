import sqlite3
import os

def migrate_database():
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')

    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(companions)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"[INFO] Current companions columns: {columns}")

        if 'prompt_version' in columns:
            print("[OK] prompt_version field already exists")
            conn.close()
            return True

        print("[INFO] Adding prompt_version field...")
        cursor.execute("""
            ALTER TABLE companions
            ADD COLUMN prompt_version VARCHAR(10) DEFAULT 'v1'
        """)

        conn.commit()
        print("[OK] prompt_version field added successfully")

        cursor.execute("PRAGMA table_info(companions)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"[INFO] After migration columns: {columns}")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Database Migration: Add prompt_version field")
    print("=" * 60)

    success = migrate_database()

    if success:
        print("\n[OK] Migration completed!")
    else:
        print("\n[ERROR] Migration failed!")
