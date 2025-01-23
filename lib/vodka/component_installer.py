import os
import glob
import shutil
import time
from pathlib import Path


class ComponentInstaller:
    def __init__(self, prefix_path):
        self.prefix_path = Path(prefix_path)
        self.drive_c = self.prefix_path / "drive_c"
        self.system32_path = self.drive_c / "windows/system32"
        self.system64_path = self.drive_c / "windows/system64"
        self.user_reg_path = self.prefix_path / "user.reg"
        self.system_reg_path = self.prefix_path / "system.reg"

    def install_component(self, component_path, installation_info):
        """Install a component according to its installation instructions"""
        try:
            if installation_info["type"] == "dll_override":
                # Ensure prefix structure exists
                self._ensure_prefix_structure()

                # Install DLLs
                self._install_dlls(component_path, installation_info["files"])

                # Set DLL overrides
                self._set_dll_overrides(installation_info["overrides"])

                # Set environment variables if specified
                if "environment" in installation_info:
                    self._set_environment_vars(
                        installation_info["environment"])

                return True
            return False
        except Exception as e:
            print(f"Installation error: {str(e)}")
            return False

    def _ensure_prefix_structure(self):
        """Ensure all necessary directories exist"""
        self.system32_path.mkdir(parents=True, exist_ok=True)
        self.system64_path.mkdir(parents=True, exist_ok=True)

    def _install_dlls(self, component_path, files_info):
        """Install DLLs to appropriate directories"""
        component_path = Path(component_path)

        # Install 32-bit DLLs
        if "x32" in files_info:
            self._install_arch_dlls(
                component_path, files_info["x32"], self.system32_path)

        # Install 64-bit DLLs
        if "x64" in files_info:
            self._install_arch_dlls(
                component_path, files_info["x64"], self.system64_path)

    def _install_arch_dlls(self, component_path, arch_info, target_path):
        """Install DLLs for a specific architecture"""
        source_pattern = component_path / arch_info["source"]

        # Remove existing DLLs first
        if "dlls" in arch_info:
            for dll in arch_info["dlls"]:
                target_dll = target_path / dll
                if target_dll.exists():
                    target_dll.unlink()

        # Copy new DLLs
        for dll_path in glob.glob(str(source_pattern)):
            dll_name = os.path.basename(dll_path)
            target_dll = target_path / dll_name
            print(f"Installing {dll_name} to {target_dll}")
            shutil.copy2(dll_path, target_dll)
            # Ensure DLL is executable
            os.chmod(target_dll, 0o755)

    def _set_dll_overrides(self, overrides):
        """Set DLL overrides in the registry"""
        if not self.user_reg_path.exists():
            # Create basic registry structure if it doesn't exist
            self._create_basic_registry()

        with open(self.user_reg_path, 'r', encoding='utf-8') as f:
            registry_content = f.readlines()

        dll_section = "[Software\\\\Wine\\\\DllOverrides]"
        section_index = -1

        # Find or create DllOverrides section
        for i, line in enumerate(registry_content):
            if dll_section in line:
                section_index = i
                break

        if section_index == -1:
            current_time = int(time.time())
            registry_content.extend([
                "\n",
                f"{dll_section}\n",
                f"#time={current_time:x}\n"
            ])
            section_index = len(registry_content) - 3

        # Remove existing overrides
        i = section_index + 1
        while i < len(registry_content):
            if i >= len(registry_content) or registry_content[i].startswith("["):
                break
            if any(override.split('=')[0].strip('"') in registry_content[i] for override in overrides):
                registry_content.pop(i)
            else:
                i += 1

        # Add new overrides
        new_content = []
        for override in overrides:
            dll_name, value = override.split('=')
            new_content.append(f'"{dll_name}"="{value}"\n')

        registry_content[section_index + 2:section_index + 2] = new_content

        with open(self.user_reg_path, 'w', encoding='utf-8') as f:
            f.writelines(registry_content)

    def _set_environment_vars(self, environment):
        """Set environment variables in the registry"""
        if not self.system_reg_path.exists():
            return

        with open(self.system_reg_path, 'r', encoding='utf-8') as f:
            registry_content = f.readlines()

        env_section = "[System\\\\CurrentControlSet\\\\Control\\\\Session Manager\\\\Environment]"
        section_index = -1

        for i, line in enumerate(registry_content):
            if env_section in line:
                section_index = i
                break

        if section_index == -1:
            current_time = int(time.time())
            registry_content.extend([
                "\n",
                f"{env_section}\n",
                f"#time={current_time:x}\n"
            ])
            section_index = len(registry_content) - 3

        # Add environment variables
        for name, value in environment.items():
            registry_content.insert(section_index + 2, f'"{name}"="{value}"\n')

        with open(self.system_reg_path, 'w', encoding='utf-8') as f:
            f.writelines(registry_content)

    def _create_basic_registry(self):
        """Create basic registry structure if it doesn't exist"""
        current_time = int(time.time())
        basic_registry = f"""WINE REGISTRY Version 2
;; All keys relative to \\\\User

[Software\\\\Wine\\\\DllOverrides]
#time={current_time:x}
"""
        with open(self.user_reg_path, 'w', encoding='utf-8') as f:
            f.write(basic_registry)
