import re
import os

def get_current_version(file_path="pyproject.toml"):
    with open(file_path, "r") as f:
        content = f.read()
    version_match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
    if not version_match:
        raise ValueError("Version string not found in pyproject.toml")
    return version_match.group(1)

def increment_version(file_path="pyproject.toml"):
    with open(file_path, "r") as f:
        content = f.read()

    version_match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
    if not version_match:
        raise ValueError("Version string not found in pyproject.toml")

    old_version = version_match.group(1)
    version_parts = list(map(int, old_version.split('.')))
    version_parts[-1] += 1  # Increment the last part (revision)
    new_version = ".".join(map(str, version_parts))

    new_content = re.sub(r'version = "\d+\.\d+\.\d+"', f'version = "{new_version}"', content)

    with open(file_path, "w") as f:
        f.write(new_content)
    return new_version

def revert_version(original_version, file_path="pyproject.toml"):
    with open(file_path, "r") as f:
        content = f.read()
    new_content = re.sub(r'version = "\d+\.\d+\.\d+"', f'version = "{original_version}"', content)
    with open(file_path, "w") as f:
        f.write(new_content)
    print(f"Reverted version to {original_version}")

if __name__ == "__main__":
    # This part is for testing or direct use, not for the orchestrator
    # The orchestrator will call these functions directly.
    pass
