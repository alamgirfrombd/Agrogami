import os

# -----------------------------------------------------
# AgrogamiPH — Auto Project Structure Creator
# Creates required folders & files if missing
# -----------------------------------------------------

PROJECT_STRUCTURE = {
    "folders": [
        "app",
        "app/layout",
        "app/static",
        "pages",
        "pages/inventory_management",
        "pages/sales_management",
        "pages/user_management",
        "uploads",
        "uploads/profile_pics",
        ".streamlit",
        "dev_tools"
    ],

    "files": {
        "requirements.txt": "",
        "db_connect.py": "",
        "login.py": "",
        "app/__init__.py": "",
        "app/layout/header.py": "",
        "app/layout/sidebar.py": "",
        "app/layout/footer.py": "",
        "app/static/style.css": "",
        ".streamlit/config.toml": "",
        "pages/home.py": "",
        "dev_tools/run.py": "",
        "dev_tools/show_structure.py": ""
    }
}


def create_folders():
    print("\n📁 Creating required folders (if missing)...")
    for folder in PROJECT_STRUCTURE["folders"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"  ➕ Created folder: {folder}")
        else:
            print(f"  ✔ Folder exists: {folder}")


def create_files():
    print("\n📄 Creating required files (if missing)...")
    for file_path, default_content in PROJECT_STRUCTURE["files"].items():
        if not os.path.exists(file_path):

            # Ensure parent folder exists
            folder = os.path.dirname(file_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)

            # Create the file
            with open(file_path, "w", encoding="utf-8") as f:
                if default_content:
                    f.write(default_content)

            print(f"  ➕ Created file: {file_path}")
        else:
            print(f"  ✔ File exists: {file_path}")


def main():
    print("\n🚀 AgrogamiPH Auto Project Setup Started...\n")
    create_folders()
    create_files()
    print("\n🎉 Setup completed successfully! Project structure is ready.\n")


if __name__ == "__main__":
    main()
