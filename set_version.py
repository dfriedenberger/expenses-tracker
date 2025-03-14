import argparse
import re
import sys
import subprocess
from datetime import datetime

CHANGELOG_FILE = "CHANGELOG.md"
INIT_FILE = "app/lib/__init__.py"
MAIN_BRANCH = "main"


def get_version_from_init():
    """Liest die aktuelle Version aus app/__init__.py."""
    with open(INIT_FILE, "r", encoding="UTF-8") as file:
        content = file.read()

    version_match = re.search(r'__version__ = "(\d+)\.(\d+)\.(\d+)"', content)
    date_match = re.search(r'__date__ = "(\d{4}-\d{2}-\d{2})"', content)

    if version_match and date_match:
        return tuple(map(int, version_match.groups())), date_match.group(1)

    print("Fehler: Version oder Datum in __init__.py nicht gefunden!")
    sys.exit(1)


def get_version_from_changelog():
    """Liest die neueste Version aus CHANGELOG.md."""
    with open(CHANGELOG_FILE, "r", encoding="UTF-8") as file:
        content = file.readlines()

    for line in content:
        match = re.match(r"## \[(\d+)\.(\d+)\.(\d+)\]", line)
        if match:
            return tuple(map(int, match.groups()))

    print("Fehler: Keine Version im CHANGELOG gefunden!")
    sys.exit(1)


def bump_version(major: bool, minor: bool, patch: bool, version):
    """Erhöht die Versionsnummer basierend auf der gewählten Option."""
    major_v, minor_v, patch_v = version

    if major:
        major_v += 1
        minor_v = 0
        patch_v = 0
    elif minor:
        minor_v += 1
        patch_v = 0
    elif patch:
        patch_v += 1

    return f"{major_v}.{minor_v}.{patch_v}"


def update_init_version(new_version, new_date):
    """Aktualisiert die Version und das Datum in app/__init__.py."""
    with open(INIT_FILE, "r", encoding="UTF-8") as file:
        content = file.read()

    content = re.sub(r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{new_version}"', content)
    content = re.sub(r'__date__ = "\d{4}-\d{2}-\d{2}"', f'__date__ = "{new_date}"', content)

    with open(INIT_FILE, "w", encoding="UTF-8") as file:
        file.write(content)


def insert_version_into_changelog(new_version, new_date):
    """Fügt die neue Version nach '## [Unreleased]' in CHANGELOG.md ein."""
    with open(CHANGELOG_FILE, "r", encoding="UTF-8") as file:
        content = file.readlines()

    new_version_line = f"\n## [{new_version}] - {new_date}\n"

    for i, line in enumerate(content):
        if re.match(r"## \[Unreleased\]", line):
            insert_pos = i + 1
            break
    else:
        print("Fehler: '## [Unreleased]' nicht gefunden!")
        sys.exit(1)

    content.insert(insert_pos, new_version_line)

    with open(CHANGELOG_FILE, "w", encoding="UTF-8") as file:
        file.writelines(content)


def git_commit_and_tag(new_version):
    """Commitet die Änderungen und erstellt ein Git-Tag."""
    subprocess.run(["git", "add", CHANGELOG_FILE, INIT_FILE], check=True)
    subprocess.run(["git", "commit", "-m", f"Release version {new_version}"], check=True)
    subprocess.run(["git", "push", "origin", MAIN_BRANCH], check=True)
    subprocess.run(["git", "tag", new_version], check=True)
    subprocess.run(["git", "push", "origin", new_version], check=True)


def main():
    parser = argparse.ArgumentParser(description="Erhöhe die Version und aktualisiere CHANGELOG und __init__.py")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Erhöht die Major-Version (X.0.0)")
    group.add_argument("--minor", action="store_true", help="Erhöht die Minor-Version (X.Y.0)")
    group.add_argument("--patch", action="store_true", help="Erhöht die Patch-Version (X.Y.Z)")

    args = parser.parse_args()

    init_version, _ = get_version_from_init()
    changelog_version = get_version_from_changelog()

    if init_version != changelog_version:
        print(f"Fehler: Version in __init__.py ({init_version}) und CHANGELOG ({changelog_version}) stimmen nicht überein!")
        sys.exit(1)

    new_version = bump_version(args.major, args.minor, args.patch, init_version)
    new_date = datetime.today().strftime("%Y-%m-%d")

    update_init_version(new_version, new_date)
    insert_version_into_changelog(new_version, new_date)
    #git_commit_and_tag(new_version)

    print(f"✅ Erfolgreich auf Version {new_version} (Datum: {new_date}) aktualisiert!")


if __name__ == "__main__":
    main()
