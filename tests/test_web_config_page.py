#!/usr/bin/env python3
"""
Test the web config management pages
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_page_import():
    """Test importing the config management page"""
    print("🧪 Testing config management page import")
    print("=" * 50)

    try:
        from web.pages.config_management import render_config_management
        print("✅ Config management page imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import config management page: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
        return False

def test_config_manager_import():
    """Test importing the config manager"""
    print("\n🧪 Testing config manager import")
    print("=" * 50)

    try:
        from tradingagents.config.config_manager import config_manager, token_tracker
        print("✅ Config manager imported successfully")

        # Test basic functions
        models = config_manager.load_models()
        print(f"📋 Loaded {len(models)} model configurations")

        pricing = config_manager.load_pricing()
        print(f"💰 Loaded {len(pricing)} pricing configurations")

        settings = config_manager.load_settings()
        print(f"⚙️ Loaded {len(settings)} system settings")

        return True
    except Exception as e:
        print(f"❌ Failed to import config manager: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
        return False

def test_streamlit_components():
    """Test Streamlit components"""
    print("\n🧪 Testing Streamlit components")
    print("=" * 50)

    try:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go

        print("✅ Streamlit imported successfully")
        print("✅ Pandas imported successfully")
        print("✅ Plotly imported successfully")

        return True
    except Exception as e:
        print(f"❌ Failed to import Streamlit components: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 Web config management page tests")
    print("=" * 60)

    tests = [
        ("Streamlit components", test_streamlit_components),
        ("Config manager", test_config_manager_import),
        ("Config page", test_config_page_import),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")

    print(f"\n📊 Test results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! The config management page looks usable")
        print("\n💡 How to use:")
        print("1. Start the web app: python -m streamlit run web/app.py")
        print("2. Select '⚙️ Config Management' in the sidebar")
        print("3. Configure API keys, model parameters and pricing")
        print("4. Review usage statistics and cost analysis")
        return True
    else:
        print("❌ Some tests failed, please check configuration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
