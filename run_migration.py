"""
Database Migration Script
Adds file upload columns to teacher_materials table
"""
import pymysql
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update if you have a password
    'database': 'emotiva-math',  # Fixed: use hyphen like in .env
    'charset': 'utf8mb4'
}

migration_sql = """
-- Add new columns for file upload support
ALTER TABLE teacher_materials
  ADD COLUMN IF NOT EXISTS file_path VARCHAR(500) NULL COMMENT 'Path to uploaded file' AFTER konten,
  ADD COLUMN IF NOT EXISTS file_name VARCHAR(255) NULL COMMENT 'Original filename' AFTER file_path,
  ADD COLUMN IF NOT EXISTS file_type VARCHAR(50) NULL COMMENT 'File extension (pdf, doc, etc)' AFTER file_name;

-- Make konten column nullable for backward compatibility
ALTER TABLE teacher_materials
  MODIFY COLUMN konten TEXT NULL COMMENT 'Materi lengkap dari guru (optional if file uploaded)';
"""

def run_migration():
    try:
        print("🔄 Connecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("📝 Running migration...")
        
        # Check if columns already exist
        cursor.execute("DESCRIBE teacher_materials")
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        # Add file_path if not exists
        if 'file_path' not in existing_columns:
            print("   Adding column: file_path")
            cursor.execute("""
                ALTER TABLE teacher_materials
                ADD COLUMN file_path VARCHAR(500) NULL COMMENT 'Path to uploaded file' AFTER konten
            """)
        else:
            print("   Column file_path already exists, skipping...")
        
        # Add file_name if not exists
        if 'file_name' not in existing_columns:
            print("   Adding column: file_name")
            cursor.execute("""
                ALTER TABLE teacher_materials
                ADD COLUMN file_name VARCHAR(255) NULL COMMENT 'Original filename' AFTER file_path
            """)
        else:
            print("   Column file_name already exists, skipping...")
        
        # Add file_type if not exists
        if 'file_type' not in existing_columns:
            print("   Adding column: file_type")
            cursor.execute("""
                ALTER TABLE teacher_materials
                ADD COLUMN file_type VARCHAR(50) NULL COMMENT 'File extension (pdf, doc, etc)' AFTER file_name
            """)
        else:
            print("   Column file_type already exists, skipping...")
        
        # Make konten nullable
        print("   Modifying konten column to be nullable...")
        cursor.execute("""
            ALTER TABLE teacher_materials
            MODIFY COLUMN konten TEXT NULL COMMENT 'Materi lengkap dari guru (optional if file uploaded)'
        """)
        
        connection.commit()
        
        # Verify the changes
        print("\n✅ Migration completed! Verifying table structure...")
        cursor.execute("DESCRIBE teacher_materials")
        columns = cursor.fetchall()
        
        print("\n📋 Current teacher_materials table structure:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        # Check if new columns exist
        column_names = [col[0] for col in columns]
        required_columns = ['file_path', 'file_name', 'file_type']
        
        if all(col in column_names for col in required_columns):
            print(f"\n✅ All required columns added successfully: {', '.join(required_columns)}")
        else:
            missing = [col for col in required_columns if col not in column_names]
            print(f"\n❌ Missing columns: {', '.join(missing)}")
            return False
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
