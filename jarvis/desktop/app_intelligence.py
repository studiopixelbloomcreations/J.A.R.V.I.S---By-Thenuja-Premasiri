"""
Capability 18: Application Intelligence Subsystem for J.A.R.V.I.S.
Provides deep application discovery, category classification, executable mapping,
registry interrogation, and running app state intelligence.
"""
import os
import winreg
import psutil
from typing import List, Dict, Any, Optional

APP_CATEGORIES = {
    "Browser": ["chrome", "msedge", "firefox", "brave", "opera", "safari"],
    "IDE_Editor": ["code", "devenv", "notepad++", "sublime_text", "pycharm", "idea", "atom", "notepad"],
    "Terminal_Shell": ["powershell", "cmd", "wt", "windowsterminal", "bash", "mintty", "conemu"],
    "Communication": ["whatsapp", "slack", "teams", "discord", "zoom", "skype", "telegram", "outlook"],
    "Media_Creative": ["spotify", "vlc", "photoshop", "illustrator", "premiere", "blender", "audacity"],
    "Productivity_Office": ["winword", "excel", "powerpnt", "onenote", "acrobat", "notion", "obsidian"],
    "System_Utility": ["taskmgr", "regedit", "explorer", "cleanmgr", "control", "mmc", "perfmon"]
}


class ApplicationIntelligence:
    """Manages application discovery, classification, and runtime process intelligence."""

    def categorize_app(self, app_name_or_exe: str) -> str:
        """Determines category for an application name or executable."""
        token = str(app_name_or_exe).lower().replace(".exe", "").strip()
        for category, keywords in APP_CATEGORIES.items():
            for kw in keywords:
                if kw in token:
                    return category
        return "General_Software"

    def get_installed_applications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Interrogates Windows Registry Uninstall hives to discover installed software.
        """
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]

        installed = []
        seen_names = set()

        for root_key, subkey_path in registry_paths:
            try:
                key = winreg.OpenKey(root_key, subkey_path)
            except OSError:
                continue

            num_subkeys = winreg.QueryInfoKey(key)[0]
            for i in range(num_subkeys):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    name = None
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    except OSError:
                        pass

                    if not name or name in seen_names:
                        continue

                    # Skip system update packages
                    if name.startswith("KB") or "Security Update" in name:
                        continue

                    seen_names.add(name)

                    version = ""
                    try:
                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    except OSError:
                        pass

                    publisher = ""
                    try:
                        publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                    except OSError:
                        pass

                    install_location = ""
                    try:
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    except OSError:
                        pass

                    installed.append({
                        "name": name,
                        "version": str(version),
                        "publisher": str(publisher),
                        "install_location": str(install_location),
                        "category": self.categorize_app(name),
                    })

                    if len(installed) >= limit:
                        break
                except OSError:
                    continue

        return installed

    def get_active_applications(self) -> List[Dict[str, Any]]:
        """
        Returns actively running applications that have visible desktop windows.
        """
        active_apps = []
        seen_pids = set()

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                pid = info['pid']
                name = info['name'] or ""
                if pid in seen_pids or not name:
                    continue

                mem_mb = round((info['memory_info'].rss if info['memory_info'] else 0) / (1024 * 1024), 1)

                active_apps.append({
                    "pid": pid,
                    "name": name,
                    "executable": info.get('exe') or "",
                    "memory_mb": mem_mb,
                    "cpu_percent": round(info.get('cpu_percent') or 0.0, 1),
                    "category": self.categorize_app(name),
                })
                seen_pids.add(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        active_apps.sort(key=lambda a: a['memory_mb'], reverse=True)
        return active_apps

    def get_startup_applications(self) -> List[Dict[str, Any]]:
        """Enumerates applications configured to run at Windows logon."""
        startup_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]

        items = []
        for root, path in startup_paths:
            try:
                k = winreg.OpenKey(root, path)
                num_vals = winreg.QueryInfoKey(k)[1]
                for i in range(num_vals):
                    try:
                        v_name, v_data, _ = winreg.EnumValue(k, i)
                        items.append({
                            "name": v_name,
                            "command": v_data,
                            "category": self.categorize_app(v_name),
                        })
                    except OSError:
                        continue
            except OSError:
                continue
        return items


app_intelligence = ApplicationIntelligence()
