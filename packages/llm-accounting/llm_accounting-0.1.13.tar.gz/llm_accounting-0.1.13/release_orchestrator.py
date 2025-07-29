import subprocess
import sys
import os
from version_manager import get_current_version, increment_version, revert_version

def run_command(command, shell=True, check=True):
    """Helper to run shell commands."""
    print(f"Executing: {command}")
    try:
        result = subprocess.run(command, shell=shell, check=check, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}", file=sys.stderr)
        print(f"Stdout: {e.stdout}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        raise

def main():
    original_version = None
    try:
        # 1. Get original version
        original_version = get_current_version()
        print(f"Current version: {original_version}")

        # 2. Increment version in pyproject.toml
        new_version = increment_version()
        print(f"Incremented version to: {new_version}")

        # 3. Clean up previous build artifacts
        print("Cleaning up build artifacts...")
        run_command("rmdir /s /q dist", check=False) # check=False because rmdir might fail if dir doesn't exist

        # 4. Build the package
        print("Building package...")
        run_command("python -m build")

        # 5. Upload to PyPI
        print("Uploading to PyPI...")
        # Assuming PYPI_TOKEN is set as an environment variable
        pypi_token = os.environ.get("PYPI_TOKEN")
        if not pypi_token:
            print("PYPI_TOKEN environment variable not set. Skipping PyPI upload.", file=sys.stderr)
            # Decide whether to exit or continue without upload
            sys.exit(1) # Exit if token is missing for upload

        run_command(f'twine upload --username __token__ --password "{pypi_token}" dist/*')

        # 6. Create GitHub Release
        print("Creating GitHub Release...")
        run_command(f'gh release create {new_version} --title "Release {new_version}" --notes "Automated release for version {new_version}"')

        print("Release process completed successfully!")

    except Exception as e:
        print(f"An error occurred during the release process: {e}", file=sys.stderr)
        if original_version:
            print("Attempting to revert version...", file=sys.stderr)
            try:
                revert_version(original_version)
                print("Version reverted successfully.", file=sys.stderr)
            except Exception as revert_e:
                print(f"Failed to revert version: {revert_e}", file=sys.stderr)
        sys.exit(1) # Exit with error code

if __name__ == "__main__":
    # Ensure virtual environment is activated before running this script
    # This script assumes it's run within an activated venv or that python -m build etc. are globally available
    # For build.bat, we'll activate the venv there.
    main()
