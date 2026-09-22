"""Install missing files only, without following learner-controlled symlinks."""
from pathlib import Path
import os
import shutil
import json

source = Path("/opt/java-course/materials")
work = Path.home() / "work"
work.mkdir(exist_ok=True)
for origin in sorted(source.rglob("*")):
    if not origin.is_file():
        continue
    relative = origin.relative_to(source)
    parent = work
    safe = True
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            safe = False
            break
        parent.mkdir(exist_ok=True)
    if not safe:
        continue
    target = parent / relative.name
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        continue
    with os.fdopen(fd, "wb") as dest, origin.open("rb") as src:
        shutil.copyfileobj(src, dest)

settings = work / ".ide/User"
if not (work / ".ide").is_symlink() and not settings.is_symlink():
    settings.mkdir(parents=True, exist_ok=True)
    defaults = settings / "settings.json"
    if not defaults.exists():
        defaults.write_text('''{
  "workbench.startupEditor": "none",
  "workbench.colorTheme": "Default Light Modern",
  "editor.fontSize": 16,
  "editor.minimap.enabled": false,
  "files.autoSave": "off",
  "java.jdt.ls.java.home": "/opt/java/openjdk",
  "java.jdt.ls.vmargs": "-Xms128m -Xmx1024m",
  "java.transport": "stdio",
  "java.configuration.runtimes": [{"name":"JavaSE-21","path":"/opt/java/openjdk","default":true}],
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false
}
''', encoding="utf-8")

# Remote machine-scoped settings are not reliably read from browser user settings.
machine = work / ".ide/Machine"
if not (work / ".ide").is_symlink() and not machine.is_symlink():
    machine.mkdir(parents=True, exist_ok=True)
    machine_defaults = machine / "settings.json"
    if not machine_defaults.exists():
        machine_defaults.write_text(json.dumps({
            "java.jdt.ls.java.home": "/opt/java/openjdk",
            "java.jdt.ls.vmargs": "-Xms128m -Xmx1024m",
            "java.transport": "stdio",
            "java.configuration.maven.userSettings": "/opt/java-course/maven-settings.xml",
            "redhat.telemetry.enabled": False,
        }, indent=2) + "\n", encoding="utf-8")
    elif not machine_defaults.is_symlink():
        # Add only the newly required default; preserve explicit learner settings.
        try:
            existing = json.loads(machine_defaults.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            existing = None
        if isinstance(existing, dict) and "java.configuration.maven.userSettings" not in existing:
            existing["java.configuration.maven.userSettings"] = "/opt/java-course/maven-settings.xml"
            machine_defaults.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
