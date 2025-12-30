"""
Database Setup Script untuk EMOTIVA-MATH
Membuat database MySQL dan tabel-tabel yang diperlukan
"""
import pymysql
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_database():
    """Membuat database MySQL dari schema.sql"""
    
    # MySQL connection settings
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    database_name = os.getenv('MYSQL_DATABASE', 'emotiva_math')
    
    print("="*60)
    print("🗄️  EMOTIVA-MATH Database Setup")
    print("="*60)
    print(f"📍 Host: {mysql_config['host']}:{mysql_config['port']}")
    print(f"👤 User: {mysql_config['user']}")
    print(f"🗃️  Database: {database_name}")
    print("="*60)
    
    try:
        # Connect to MySQL server (without database)
        print("\n⏳ Connecting to MySQL server...")
        connection = pymysql.connect(**mysql_config)
        cursor = connection.cursor()
        
        # Create database
        print(f"⏳ Creating database '{database_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database_name}' created successfully!")
        
        # Use database
        cursor.execute(f"USE `{database_name}`")
        
        # Read and execute schema.sql
        print("\n⏳ Creating tables from schema.sql...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    # Don't print every statement, just important ones
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split('TABLE')[1].split('(')[0].strip().split()[0]
                        print(f"  ✅ Table '{table_name}' created")
                except pymysql.Error as e:
                    # Skip errors for CREATE DATABASE and USE statements
                    if 'CREATE DATABASE' not in statement.upper() and 'USE' not in statement.upper():
                        print(f"  ⚠️  Warning: {e}")
        
        connection.commit()
        
        # Verify installation
        print("\n📊 Verifying installation...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n✅ Tables created:")
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  • {table_name}: {count} records")
        
        print("\n" + "="*60)
        print("✅ Database setup completed successfully!")
        print("="*60)
        print("\n📝 Next steps:")
        print("1. Update .env file dengan MySQL credentials Anda")
        print("2. Jalankan: python run.py")
        print("3. Test API: http://localhost:5000/api/health")
        print("="*60)
        
        cursor.close()
        connection.close()
        
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Pastikan MySQL server sudah running")
        print("2. Cek username dan password di .env")
        print("3. Pastikan user memiliki permission CREATE DATABASE")
        return False
    except FileNotFoundError:
        print("\n❌ Error: database/schema.sql not found!")
        print("Pastikan file schema.sql ada di folder database/")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
