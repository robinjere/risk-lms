"""
MSSQL Database Setup and Connection Test Script
Run this script to verify your MSSQL connection before running Django migrations.
"""
import os
import sys

def test_pyodbc_installation():
    """Test if pyodbc is installed"""
    print("=" * 60)
    print("STEP 1: Checking pyodbc installation...")
    print("=" * 60)
    try:
        import pyodbc
        print(f"✅ pyodbc version: {pyodbc.version}")
        return True
    except ImportError:
        print("❌ pyodbc is not installed!")
        print("   Run: pip install pyodbc mssql-django")
        return False

def list_odbc_drivers():
    """List available ODBC drivers"""
    print("\n" + "=" * 60)
    print("STEP 2: Checking ODBC Drivers...")
    print("=" * 60)
    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers()]
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_drivers:
            print("✅ Available SQL Server ODBC drivers:")
            for driver in sql_drivers:
                print(f"   - {driver}")
            return sql_drivers[0]  # Return first available driver
        else:
            print("❌ No SQL Server ODBC drivers found!")
            print("   Please install 'ODBC Driver 17 for SQL Server'")
            print("   Download: https://go.microsoft.com/fwlink/?linkid=2249004")
            return None
    except Exception as e:
        print(f"❌ Error listing drivers: {e}")
        return None

def test_connection(driver, server, database, username, password, port='1433'):
    """Test MSSQL connection"""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Database Connection...")
    print("=" * 60)
    
    import pyodbc
    
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    
    print(f"   Server: {server}:{port}")
    print(f"   Database: {database}")
    print(f"   User: {username}")
    print(f"   Driver: {driver}")
    
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"\n✅ Connection successful!")
        print(f"   SQL Server Version: {version[:50]}...")
        conn.close()
        return True
    except pyodbc.Error as e:
        print(f"\n❌ Connection failed!")
        print(f"   Error: {e}")
        return False

def test_database_exists(driver, server, database, username, password, port='1433'):
    """Check if database exists, create if not"""
    print("\n" + "=" * 60)
    print("STEP 4: Checking Database Exists...")
    print("=" * 60)
    
    import pyodbc
    
    # Connect to master database first
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server},{port};"
        f"DATABASE=master;"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = ?", (database,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Database '{database}' exists!")
        else:
            print(f"⚠️  Database '{database}' does not exist.")
            create = input("   Would you like to create it? (y/n): ").strip().lower()
            if create == 'y':
                conn.autocommit = True
                cursor.execute(f"CREATE DATABASE [{database}]")
                print(f"✅ Database '{database}' created successfully!")
            else:
                print("   Skipping database creation.")
        
        conn.close()
        return True
    except pyodbc.Error as e:
        print(f"❌ Error: {e}")
        return False

def show_django_config():
    """Show required Django configuration"""
    print("\n" + "=" * 60)
    print("DJANGO CONFIGURATION")
    print("=" * 60)
    print("""
Your settings.py is already configured for MSSQL.
Set these environment variables before running Django:

PowerShell:
-----------
$env:DB_ENGINE = "mssql"
$env:DB_NAME = "risk_lms"
$env:DB_USER = "sa"
$env:DB_PASSWORD = "YourPassword"
$env:DB_HOST = "localhost"
$env:DB_PORT = "1433"

Then run migrations:
--------------------
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
""")

def main():
    print("\n" + "=" * 60)
    print("   RISK LMS - MSSQL DATABASE SETUP WIZARD")
    print("=" * 60)
    
    # Check pyodbc
    if not test_pyodbc_installation():
        sys.exit(1)
    
    # List drivers
    driver = list_odbc_drivers()
    if not driver:
        sys.exit(1)
    
    # Get connection details
    print("\n" + "=" * 60)
    print("Enter Database Connection Details")
    print("=" * 60)
    print("(Press Enter to use default values shown in brackets)")
    
    server = input("   SQL Server hostname [localhost]: ").strip() or "localhost"
    port = input("   SQL Server port [1433]: ").strip() or "1433"
    database = input("   Database name [risk_lms]: ").strip() or "risk_lms"
    username = input("   Username [sa]: ").strip() or "sa"
    password = input("   Password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        sys.exit(1)
    
    # Test connection to master
    print("\n   Testing connection to SQL Server...")
    
    import pyodbc
    master_conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server},{port};"
        f"DATABASE=master;"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    
    try:
        conn = pyodbc.connect(master_conn_str, timeout=10)
        conn.close()
        print("✅ Connected to SQL Server successfully!")
    except pyodbc.Error as e:
        print(f"❌ Cannot connect to SQL Server: {e}")
        sys.exit(1)
    
    # Check/create database
    test_database_exists(driver, server, database, username, password, port)
    
    # Test connection to target database
    test_connection(driver, server, database, username, password, port)
    
    # Show Django config
    show_django_config()
    
    # Set environment variables for this session
    print("\n" + "=" * 60)
    print("SETTING ENVIRONMENT VARIABLES")
    print("=" * 60)
    os.environ['DB_ENGINE'] = 'mssql'
    os.environ['DB_NAME'] = database
    os.environ['DB_USER'] = username
    os.environ['DB_PASSWORD'] = password
    os.environ['DB_HOST'] = server
    os.environ['DB_PORT'] = port
    print("✅ Environment variables set for this session!")
    
    # Ask to run migrations
    print("\n" + "=" * 60)
    run_migrations = input("Would you like to run Django migrations now? (y/n): ").strip().lower()
    if run_migrations == 'y':
        print("\nRunning migrations...")
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        
        create_super = input("\nCreate superuser? (y/n): ").strip().lower()
        if create_super == 'y':
            os.system("python manage.py createsuperuser")
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(f"""
To start the server, run:
    python manage.py runserver 0.0.0.0:8000

Access the application at:
    http://localhost:8000/
    
Admin panel:
    http://localhost:8000/admin/
""")

if __name__ == "__main__":
    main()
