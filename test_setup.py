#!/usr/bin/env python3
"""
Test Setup Script - Customer Support AI Assistant

Purpose:
- Verify environment setup
- Check imports
- Check Ollama connection
- Validate project directories
- Quick sanity check before running app.py

Run:
    python test_setup.py
"""

import sys
import os
import requests
from termcolor import colored


# --------------------------------------------------
# TEST 1: IMPORT CHECK
# --------------------------------------------------

def test_imports():
    print(colored("\n[1] Testing module imports...", "cyan"))
    try:
        import config
        import utils
        import agent
        import tools
        import memory_manager
        import escalation_manager
        import vector_store
        import document_processor

        print(colored("✓ All modules imported successfully", "green"))
        return True
    except ImportError as e:
        print(colored(f"✗ Import error: {e}", "red"))
        return False


# --------------------------------------------------
# TEST 2: OLLAMA CONNECTION
# --------------------------------------------------

def test_ollama():
    print(colored("\n[2] Testing Ollama connection...", "cyan"))
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(colored("✓ Ollama is running", "green"))

            if models:
                print("Available models:")
                for m in models:
                    print(f"  - {m['name']}")
            else:
                print(colored("⚠ Ollama running but no models found", "yellow"))
                print("Run: ollama pull llama3")

            return True
        else:
            print(colored("✗ Ollama returned unexpected status", "red"))
            return False
    except requests.exceptions.RequestException:
        print(colored("✗ Cannot connect to Ollama (http://localhost:11434)", "red"))
        print("Fix: Run → ollama serve")
        return False


# --------------------------------------------------
# TEST 3: DIRECTORY CHECK
# --------------------------------------------------

def test_directories():
    print(colored("\n[3] Checking required directories...", "cyan"))

    required_dirs = [
        "pdfFiles",
        "vectorDB",
        "memoryDB",
    ]

    all_ok = True
    for d in required_dirs:
        if os.path.exists(d):
            print(colored(f"✓ {d} exists", "green"))
        else:
            print(colored(f"⚠ {d} missing (will be created automatically)", "yellow"))
            try:
                os.makedirs(d)
                print(colored(f"✓ {d} created", "green"))
            except Exception as e:
                print(colored(f"✗ Failed to create {d}: {e}", "red"))
                all_ok = False

    return all_ok


# --------------------------------------------------
# MAIN RUNNER
# --------------------------------------------------

def main():
    print(colored("\n============================================", "magenta", attrs=["bold"]))
    print(colored(" CUSTOMER SUPPORT AI - SETUP TEST ", "magenta", attrs=["bold"]))
    print(colored("============================================", "magenta", attrs=["bold"]))

    all_passed = True

    if not test_imports():
        all_passed = False

    if not test_ollama():
        all_passed = False

    if not test_directories():
        all_passed = False

    print(colored("\n--------------------------------------------", "magenta"))

    if all_passed:
        print(colored("✓ ALL TESTS PASSED", "green", attrs=["bold"]))
        print(colored("You can now run: streamlit run app.py 🚀", "cyan"))
    else:
        print(colored("✗ SOME TESTS FAILED", "red", attrs=["bold"]))
        print("Fix the errors above before running the app.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        from termcolor import colored
    except ImportError:
        print("Installing termcolor...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "termcolor"])
        from termcolor import colored

    main()
