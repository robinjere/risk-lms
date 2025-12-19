"""
Test LDAP authentication - matching the PHP implementation exactly
"""
import ldap3
from ldap3 import Server, Connection, ALL, SIMPLE

# LDAP Configuration - from PHP code
LDAP_HOST = '192.168.10.50'
LDAP_PORT = 389
LDAP_DOMAIN = 'kcbltz.crdbbankplc.com'

def test_ldap_bind(username, password):
    """
    Test LDAP bind exactly like PHP:
    ldap_bind($ldap_connection, "$un@$ldap_domain", $pw)
    """
    print(f"\n{'='*60}")
    print(f"Testing LDAP authentication for: {username}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Connect to LDAP server (ldap_connect)
        print(f"\n1. Connecting to {LDAP_HOST}:{LDAP_PORT}...")
        server = Server(
            LDAP_HOST,
            port=LDAP_PORT,
            use_ssl=False,
            get_info=ALL,
            connect_timeout=10
        )
        print(f"   Server object created: {server}")
        
        # Step 2: Prepare bind credentials (same as PHP: "$un@$ldap_domain")
        bind_dn = f"{username}@{LDAP_DOMAIN}"
        print(f"\n2. Bind DN: {bind_dn}")
        
        # Step 3: Create connection and attempt bind
        print(f"\n3. Attempting LDAP bind...")
        conn = Connection(
            server,
            user=bind_dn,
            password=password,
            authentication=SIMPLE,
            auto_bind=False,
            raise_exceptions=False,
            read_only=True
        )
        
        # Attempt bind
        bind_result = conn.bind()
        
        print(f"\n4. Bind Result: {bind_result}")
        print(f"   Connection result: {conn.result}")
        
        if bind_result:
            print(f"\n✅ SUCCESS! User {username} authenticated successfully!")
            
            # Try to search for user details
            print(f"\n5. Searching for user details...")
            search_base = 'DC=kcbltz,DC=crdbbankplc,DC=com'
            search_filter = f'(sAMAccountName={username})'
            
            conn.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=['displayName', 'mail', 'department', 'title', 'givenName', 'sn']
            )
            
            if conn.entries:
                entry = conn.entries[0]
                print(f"   Found user: {entry}")
                print(f"   Display Name: {entry.displayName if hasattr(entry, 'displayName') else 'N/A'}")
                print(f"   Email: {entry.mail if hasattr(entry, 'mail') else 'N/A'}")
                print(f"   Department: {entry.department if hasattr(entry, 'department') else 'N/A'}")
            else:
                print(f"   No user details found in search")
            
            conn.unbind()
            return True
        else:
            print(f"\n❌ FAILED! Bind unsuccessful")
            print(f"   Error: {conn.last_error}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        return False


if __name__ == '__main__':
    # Test with a username - you'll need to enter the password
    import getpass
    
    print("\nLDAP Authentication Test")
    print("Domain: KCBLTZ.CRDBBANKPLC.COM")
    print("Server: 192.168.10.50:389")
    print("-" * 40)
    
    username = input("Enter domain username (e.g., JMuro): ").strip()
    password = getpass.getpass("Enter domain password: ")
    
    if username and password:
        test_ldap_bind(username, password)
    else:
        print("Username and password required!")
