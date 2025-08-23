#!/usr/bin/env python
import argparse
import os


def create_api_files(app_name, folder_name, endpoint_name):
    """
    Create a new API endpoint structure with required empty files.

    Args:
        app_name: Name of the app (e.g., 'book', 'users')
        folder_name: Name of the folder inside app's api_endpoints (e.g., 'book')
        endpoint_name: Name of the API endpoint (e.g., 'CategoryList')
    """
    # Define the base path for the new endpoint
    base_path = os.path.join(
        "apps", app_name, "api_endpoints", folder_name, endpoint_name
    )

    # Create directories if they don't exist
    os.makedirs(base_path, exist_ok=True)

    # Create empty __init__.py files in all parent directories
    parent_dirs = [
        os.path.join("apps", app_name, "api_endpoints"),
        os.path.join("apps", app_name, "api_endpoints", folder_name),
    ]

    for directory in parent_dirs:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(init_file):
            open(init_file, "a").close()

    # Define files to create
    files = ["doc.md", "serializers.py", "views.py", "tests.py"]

    # Create each file (empty)
    for file in files:
        file_path = os.path.join(base_path, file)

        # Check if file already exists
        if os.path.exists(file_path):
            print(f"File {file_path} already exists, skipping.")
            continue

        # Create empty file
        open(file_path, "a").close()

    # Create __init__.py with import statement
    init_file_path = os.path.join(base_path, "__init__.py")
    if os.path.exists(init_file_path):
        print(f"File {init_file_path} already exists, skipping.")
    else:
        with open(init_file_path, "w") as f:
            f.write("from .views import *  # noqa\n")

    print(
        f"Successfully created API endpoint: {app_name}/{folder_name}/{endpoint_name}"
    )
    print(f"Location: {base_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new API endpoint with required files."
    )
    parser.add_argument("app_name", help="Name of the app (e.g., book, users)")
    parser.add_argument(
        "folder_name", help="Name of the folder inside app's api_endpoints (e.g., book)"
    )
    parser.add_argument(
        "endpoint_name", help="Name of the API endpoint (e.g., CategoryList)"
    )

    args = parser.parse_args()

    create_api_files(args.app_name, args.folder_name, args.endpoint_name)
