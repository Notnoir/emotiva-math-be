"""
Test MySQL Connection
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing MySQL Connection...")
print("="*60)

try:
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'emotiva_math'),
        charset='utf8mb4'
    )
    
    print("✅ MySQL Connection Successful!")
    print(f"Host: {os.getenv('MYSQL_HOST', 'localhost')}")
    print(f"Database: {os.getenv('MYSQL_DATABASE', 'emotiva_math')}")
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print(f"\n📋 Tables in database:")
    for table in tables:
        print(f"  • {table[0]}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "="*60)
    print("✅ Database is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nCheck your .env file:")
    print("- MYSQL_PASSWORD correct?")
    print("- MySQL server running?")
