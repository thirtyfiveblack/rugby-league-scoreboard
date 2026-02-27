#!/usr/bin/env python3
"""
Simple syntax checker for the basketball plugin.
Tests that the plugin can be imported without errors.
"""

import sys
import os

# Set emulator mode before any imports
os.environ['EMULATOR'] = 'true'

# Add LEDMatrix to path
sys.path.insert(0, '/home/chuck/Github/LEDMatrix')

try:
    # Try to import the plugin
    from manager import BasketballPluginManager
    print("✓ Plugin imported successfully")
    print(f"✓ Class name: {BasketballPluginManager.__name__}")
    print(f"✓ Base classes: {BasketballPluginManager.__bases__}")
    print("\nPlugin structure is valid!")
    sys.exit(0)
    
except SyntaxError as e:
    print(f"✗ Syntax error: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
