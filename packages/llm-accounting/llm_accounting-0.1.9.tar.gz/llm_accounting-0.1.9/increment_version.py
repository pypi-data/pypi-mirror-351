import toml
import re

def increment_version(file_path="pyproject.toml"):
    with open(file_path, "r") as f:
        content = f.read()

    # Use regex to find and replace the version string
    # This is more robust than parsing TOML if only the version needs to be updated
    # and avoids issues with TOML library's write behavior
    def replace_version(match):
        version_parts = list(map(int, match.group(1).split('.')))
        version_parts[-1] += 1  # Increment the last part (revision)
        new_version = ".".join(map(str, version_parts))
        print(f"Incremented version from {match.group(1)} to {new_version}")
        return f'version = "{new_version}"'

    new_content = re.sub(r'version = "(\d+\.\d+\.\d+)"', replace_version, content)

    with open(file_path, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    increment_version()
