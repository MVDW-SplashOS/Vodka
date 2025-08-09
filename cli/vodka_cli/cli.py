import sys
import os
import json
from pathlib import Path

from vodka import VodkaManager, WineInstallVersion


def handle_error(e):
    """Handle errors in a user-friendly way."""
    if isinstance(e, FileNotFoundError):
        print(f"Error: File not found - {e.filename}")
    elif isinstance(e, PermissionError):
        print("Error: Permission denied. Try running with sudo?")
    else:
        print(f"Error: {str(e)}")

    # Add suggestion for version not found
    if "Version not found" in str(e):
        print("\nTip: Use 'vodka list' to see available versions")
        print("     Use 'vodka list --filter <text>' to search for specific versions")

    return 1


def print_usage():
    print("Usage: vodka <command> [args]")
    print("\nCommands:")
    print("  install <version>      - Install a specific version")
    print("  default <version>      - Set default version")
    print("  list [options]         - List available versions")
    print("  refresh               - Refresh versions list")
    print("  execute [version] <command> - Execute a command (uses default if version not specified)")
    print("\nComponent Commands:")
    print("  component install <name> - Install a specific component")
    print("  component list        - List available components")
    print("  component refresh     - Refresh components list")
    print("\nList options:")
    print("  --filter <text>       - Filter versions by name")
    print("  --page <number>       - Show specific page")
    print("  --installed           - Show only installed versions")


def paginate_list(items, page_size=10):
    """Split items into pages"""
    for i in range(0, len(items), page_size):
        yield items[i:i + page_size]


def print_version_list(versions_data, filter_str=None, page=1, page_size=10):
    """Print versions with pagination and filtering"""
    try:
        with open(versions_data.versions_file) as f:
            data = json.load(f)

        all_versions = []

        # Collect all versions with their category info
        for category in data['categories']:
            category_id = category['id']
            category_name = category['name']

            if category_id in data['versions']:
                for version in data['versions'][category_id]:
                    version_info = {
                        'category': category_name,
                        'name': version['name'],
                        'title': version['title'],
                        'installed': versions_data.is_installed(version['name']),
                        'default': versions_data.is_default(version['name'])
                    }
                    all_versions.append(version_info)

        # Apply filter if specified
        if filter_str:
            filter_str = filter_str.lower()
            all_versions = [v for v in all_versions if filter_str in v['title'].lower()
                            or filter_str in v['name'].lower()]

        # Sort versions by category and name
        all_versions.sort(key=lambda x: (x['category'], x['name']))

        # Paginate results
        pages = list(paginate_list(all_versions, page_size))
        total_pages = len(pages)

        if not all_versions:
            print("No versions found matching your criteria.")
            return

        if page > total_pages:
            print(f"Page {page} does not exist. Maximum page is {total_pages}")
            return

        current_page = pages[page - 1]
        current_category = None

        # Print header with page information
        print(f"\nShowing page {page} of {total_pages}")
        if filter_str:
            print(f"Filter: {filter_str}")
        print("-" * 50)

        # Print versions
        for version in current_page:
            if current_category != version['category']:
                current_category = version['category']
                print(f"\n{current_category}:")
                print("=" * (len(current_category) + 1))

            installed = "✓" if version['installed'] else " "
            default = "*" if version['default'] else " "
            print(f"[{installed}] [{default}] {
                  version['title']} ({version['name']})")

        print("\nLegend: ✓ = installed, * = default")
        print(f"\nUse 'vodka list --page <num>' to see other pages")
        print(f"Use 'vodka list --filter <text>' to search versions")
        print(f"Use 'vodka list --installed' to show only installed versions")

    except Exception as e:
        print(f"Error loading versions: {str(e)}")


def main():
    try:
        vodka = VodkaManager("/home/mvdw/_test_vodka")

        if len(sys.argv) < 2:
            print_usage()
            return 1

        command = sys.argv[1].lower()

        if command == "install" and len(sys.argv) >= 3:
            version_name = sys.argv[2]
            try:
                if vodka.install_version(version_name):
                    print(f"Successfully installed Wine version {
                        version_name}")
                else:
                    print(f"Version {version_name} is already installed")
            except Exception as e:
                return handle_error(e)

        elif command == "default" and len(sys.argv) == 3:
            version_name = sys.argv[2]
            if vodka.set_default(version_name):
                print(f"Set Wine version {version_name} as default")

        elif command == "list":
            if not vodka.versions_file.exists():
                print(
                    "No Wine versions found. Use 'vodka refresh' to update the version list.")
                return 0

            # Parse list command options
            filter_str = None
            page = 1
            show_installed_only = False

            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--filter" and i + 1 < len(sys.argv):
                    filter_str = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--page" and i + 1 < len(sys.argv):
                    try:
                        page = int(sys.argv[i + 1])
                    except ValueError:
                        print("Invalid page number")
                        return 1
                    i += 2
                elif sys.argv[i] == "--installed":
                    show_installed_only = True
                    i += 1
                else:
                    i += 1

            print_version_list(vodka, filter_str, page)

        elif command == "refresh":
            print("Downloading Wine versions list...")
            if vodka.download_versions():
                print("Successfully updated versions list")

        elif command == "component":
            if len(sys.argv) < 3:
                print_usage()
                return 1

            component_command = sys.argv[2].lower()

            if component_command == "install" and len(sys.argv) >= 4:
                component_name = sys.argv[3]
                prefix_path = None

                # Check for --prefix option
                if len(sys.argv) >= 6 and sys.argv[4] == "--prefix":
                    prefix_path = sys.argv[5]
                else:
                    print("Error: --prefix option is required")
                    print(
                        "Usage: vodka component install <component> --prefix <prefix_path>")
                    return 1

                try:
                    print(f"Installing {
                          component_name} into prefix: {prefix_path}")
                    if vodka.install_component(component_name, prefix_path):
                        print(f"Successfully installed component {
                              component_name}")
                        print(
                            "Note: You may need to restart your Wine prefix for changes to take effect")
                    else:
                        print(f"Component {
                              component_name} installation failed")
                except Exception as e:
                    return handle_error(e)

            elif component_command == "list":
                if not vodka.components_file.exists():
                    print(
                        "No components found. Use 'vodka component refresh' to update the component list.")
                    return 0

                components = vodka.get_components()
                print("\nAvailable Components:")
                print("-" * 50)
                for component in components:
                    installed = "✓" if component['installed'] else " "
                    print(f"[{installed}] {component['name']}")

            elif component_command == "refresh":
                print("Downloading components list...")
                if vodka.download_components():
                    print("Successfully updated components list")

            else:
                print_usage()
                return 1

        elif command == "execute":
            if len(sys.argv) < 3:
                print("Error: Command required")
                print("Usage: vodka execute [version] <command>")
                return 1

            # Check if first argument is a version or part of the command
            if len(sys.argv) >= 4 and vodka.is_installed(sys.argv[2]):
                version_name = sys.argv[2]
                command = sys.argv[3:]
            else:
                # Use default version if exists, otherwise error
                if not vodka.default_link.exists():
                    print("Error: No default Wine version set")
                    print("Use 'vodka default <version>' to set a default version")
                    return 1
                version_name = vodka.default_link.name
                command = sys.argv[2:]

            try:
                stdout, stderr = vodka.execute(version_name, command)
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr, file=sys.stderr)
                return 0
            except Exception as e:
                return handle_error(e)

        else:
            print_usage()
            return 1

        return 0

    except Exception as e:
        return handle_error(e)


if __name__ == "__main__":
    sys.exit(main())
