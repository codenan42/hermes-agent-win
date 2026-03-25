#!/usr/bin/env python3
"""
Windows Import Verification Script

Attempts to import all core modules of Hermes Agent to ensure no
platform-specific code (e.g. os.setsid, socket.AF_UNIX) is executed
at the top level, which would cause crashes on Windows.
"""

import os
import sys
import platform
import logging

# Set up logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("verify_windows")

def verify_imports():
    """Attempt to import core modules and report results."""
    modules_to_test = [
        "hermes_constants",
        "hermes_state",
        "hermes_cli.config",
        "hermes_cli.env_loader",
        "agent.model_metadata",
        "agent.auxiliary_client",
        "tools.file_operations",
        "tools.environments.local",
        "tools.environments.persistent_shell",
        "tools.process_registry",
        "tools.code_execution_tool",
        "gateway.platforms.whatsapp",
        "run_agent",
    ]

    failed = []

    # Ensure project root is in sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"Testing imports on {platform.system()} {platform.release()}...")
    print("-" * 50)

    for module_name in modules_to_test:
        try:
            print(f"Importing {module_name:30}...", end=" ", flush=True)
            __import__(module_name)
            print("OK")
        except Exception as e:
            print("FAILED")
            logger.error("Failed to import %s: %s", module_name, e)
            failed.append((module_name, str(e)))

    print("-" * 50)
    if not failed:
        print("[OK] All core modules imported successfully!")
        return True
    else:
        print(f"[FAIL] {len(failed)} modules failed to import.")
        for mod, err in failed:
            print(f"  - {mod}: {err}")
        return False

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
