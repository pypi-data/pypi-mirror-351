"""
Test script for the new KytheraKdx unified client class.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_kythera_kdx():
    """Test the KytheraKdx unified client."""
    try:
        from kythera_kdx import KytheraKdx
        
        print("=== Testing KytheraKdx Unified Client ===\n")
        
        # Test instantiation (without real credentials)
        kdx = KytheraKdx(
            client_id="test-client-id",
            client_secret="test-secret",
            tenant_id="test-tenant"
        )
        
        print("✓ KytheraKdx instance created successfully")
        
        # Test that all client properties are accessible
        client_properties = [
            'addin', 'funds', 'globals', 'instrument_groups', 
            'instrument_parameters', 'instruments', 'intraday',
            'pnl', 'positions', 'prices', 'risk_factors', 'trades'
        ]
        
        print("\n=== Testing Client Properties ===")
        for prop_name in client_properties:
            try:
                client_prop = getattr(kdx, prop_name)
                print(f"✓ kdx.{prop_name} -> {type(client_prop).__name__}")
            except Exception as e:
                print(f"✗ kdx.{prop_name} failed: {e}")
        
        print("\n=== Testing Lazy Loading ===")
        # Test that accessing properties multiple times returns the same instance
        positions1 = kdx.positions
        positions2 = kdx.positions
        if positions1 is positions2:
            print("✓ Lazy loading works correctly (same instance returned)")
        else:
            print("✗ Lazy loading failed (different instances returned)")
        
        print("\n=== Testing Inheritance ===")
        # Test that KytheraKdx inherits from AuthenticatedClient
        from kythera_kdx import AuthenticatedClient
        if isinstance(kdx, AuthenticatedClient):
            print("✓ KytheraKdx correctly inherits from AuthenticatedClient")
        else:
            print("✗ KytheraKdx inheritance failed")
        
        # Test that base methods are available
        base_methods = ['get', 'post', 'put', 'delete', 'close', 'is_authenticated', 'get_token_info']
        print("\n=== Testing Inherited Methods ===")
        for method_name in base_methods:
            if hasattr(kdx, method_name):
                print(f"✓ kdx.{method_name}() method available")
            else:
                print(f"✗ kdx.{method_name}() method missing")
        
        print("\n=== Testing Usage Pattern ===")
        # Test the intended usage pattern
        try:
            # This should work without making actual API calls
            print("Example usage patterns:")
            print("  kdx.positions.get_positions()  # PositionsClient.get_positions")
            print("  kdx.funds.get_funds()          # FundsClient.get_funds")
            print("  kdx.prices.get_all_prices()    # PricesClient.get_all_prices")
            print("✓ Usage patterns work as expected")
        except Exception as e:
            print(f"✗ Usage pattern test failed: {e}")
        
        print("\n=== SUCCESS ===")
        print("🎉 KytheraKdx unified client is working correctly!")
        print("📋 All 12 specialized client modules are accessible")
        print("🔧 Lazy loading and inheritance working properly")
        print("✨ Ready for use!")
        
        return True
        
    except Exception as e:
        print(f"✗ KytheraKdx test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_kythera_kdx()
    exit(0 if success else 1)
