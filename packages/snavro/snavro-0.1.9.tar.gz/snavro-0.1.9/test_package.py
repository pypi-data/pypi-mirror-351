#!/usr/bin/env python3
"""
Simple test script to verify the snavro package works correctly.
"""

import sys

# Add the current directory to the path so we can import snavro
sys.path.insert(0, ".")

try:
    import snavro
    from snavro import FileReader, get_supported_files

    print("✅ Successfully imported snavro package")
    print(f"   Version: {snavro.__version__}")
    print(f"   Available functions: {snavro.__all__}")

    # Test FileReader class
    reader = FileReader()
    print("\n✅ Successfully created FileReader instance")

    # Test file detection
    test_files = [
        "test.parquet",
        "test.parquet.snappy",
        "test.avro",
        "test.csv",  # unsupported
    ]

    print("\n📁 Testing file format detection:")
    for file in test_files:
        is_supported = reader.is_supported_file(file)
        status = "✅ Supported" if is_supported else "❌ Not supported"
        print(f"   {file}: {status}")

    # Test getting supported files in current directory
    supported_files = get_supported_files()
    print(f"\n📂 Found {len(supported_files)} supported files in current directory:")
    for file in supported_files[:3]:  # Show first 3
        print(f"   - {file}")
    if len(supported_files) > 3:
        print(f"   ... and {len(supported_files) - 3} more")

    print("\n🎉 All tests passed! The package is working correctly.")

    if supported_files:
        print(f"\n💡 Try running: python -m snavro.cli {supported_files[0]}")
        print("   Or just: python -m snavro.cli")

except ImportError as e:
    print(f"❌ Failed to import snavro: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error testing package: {e}")
    sys.exit(1)
