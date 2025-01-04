import sys
from vodka import VodkaManager

def print_usage():
    print("Usage: vodka <command> [args]")
    print("Commands:")
    print("  install <version>   - Install a specific version")
    print("  default <version>   - Set default version")
    print("  list               - List all available versions")
    print("  refresh            - Refresh versions list")

def main():
    vodka = VodkaManager()

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    try:
        if command == "install" and len(sys.argv) == 3:
            version_name = sys.argv[2]
            if vodka.install_version(version_name):
                print(f"Successfully installed {version_name}")
            else:
                print(f"Version {version_name} is already installed")

        elif command == "default" and len(sys.argv) == 3:
            version_name = sys.argv[2]
            if vodka.set_default(version_name):
                print(f"Set {version_name} as default")

        elif command == "list":
            print("Available versions:")
            print("------------------")
            for version in vodka.get_versions():
                status = "installed" if version["installed"] else "not installed"
                default = " (default)" if version["is_default"] else ""
                print(f"{version['name']}: {status}{default}")

        elif command == "refresh":
            if vodka.download_versions():
                print("Successfully downloaded versions list")

        else:
            print_usage()

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
