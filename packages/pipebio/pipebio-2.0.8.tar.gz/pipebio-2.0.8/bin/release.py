#!/usr/bin/env python3
import argparse
import subprocess
import sys
import re


def run(cmd, dry_run=False, capture=False):
    print(f"🔧 {cmd}")
    if dry_run:
        print("🧪 (dry run)")
        return ""
    result = subprocess.run(
        cmd, shell=True, check=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True
    )
    return result.stdout.strip() if capture else ""


def ensure_clean_git():
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout.strip():
        print("❌ Working directory not clean. Please commit or stash changes.")
        sys.exit(1)


def get_exact_tag():
    try:
        return subprocess.check_output(["git", "describe", "--tags", "--exact-match"], text=True).strip()
    except subprocess.CalledProcessError:
        return None


def confirm(prompt):
    try:
        response = input(f"{prompt} (y/N): ")
        return response.strip().lower() == 'y'
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)

def get_current_branch():
    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()

def has_changes_since_last_tag() -> bool:
    try:
        latest_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
        commits = subprocess.check_output(["git", "rev-list", f"{latest_tag}..HEAD", "--count"], text=True).strip()
        return int(commits) > 0
    except subprocess.CalledProcessError:
        # No tags exist — so definitely changes
        return True

def ensure_bump2version_installed():
    try:
        subprocess.run(
            ["bump2version", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL  # suppress "command not found" or warnings
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 bump2version not found. Installing it with pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "bump2version"],
                check=True
            )
            print("✅ bump2version installed.")
        except subprocess.CalledProcessError:
            print("❌ Failed to install bump2version. Please install it manually.")
            sys.exit(1)

def main():
    ensure_bump2version_installed()
    parser = argparse.ArgumentParser(
        description="Bump version, tag, and push to testpypi or pypi release branches.")
    parser.add_argument(
        "part",
        nargs="?",
        default="patch",
        choices=["patch", "minor", "major"],
        help=(
            "Which part of the version to bump (default: patch):\n"
            "  patch → 1.0.0 → 1.0.1 (bugfixes, safe changes)\n"
            "  minor → 1.0.0 → 1.1.0 (new features, backward-compatible)\n"
            "  major → 1.0.0 → 2.0.0 (breaking changes)"
        )
    )
    parser.add_argument("--dry-run", action="store_true", help="Show actions without executing")

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    ensure_clean_git()

    current_branch = get_current_branch()
    if current_branch not in ("testpypi", "pypi"):
        print(f"❌ Current branch is '{current_branch}', but releases are only allowed from 'testpypi' or 'pypi'.")
        sys.exit(1)
    #
    # if not has_changes_since_last_tag():
    #     print("⚠️  No changes since the last tag. Skipping release.")
    #     sys.exit(0)

    print(f"📦 Bumping version ({args.part})...")
    BUMP_CFG = "./.bump2version.cfg"  # or whatever path is correct
    run(f"bump2version {args.part}  --config-file {BUMP_CFG} {'--dry-run --verbose' if args.dry_run else ''}")

    tag = get_exact_tag()
    if not tag and not args.dry_run:
        print("❌ No Git tag found on current commit. Did bump2version create it?")
        sys.exit(1)

    if not args.dry_run and not re.match(r"^v\d+\.\d+\.\d+$", tag):
        print(f"❌ Tag '{tag}' does not match semantic versioning (vX.Y.Z).")
        sys.exit(1)

    print(f"✅ Prepared release: {tag} → {current_branch}")

    if current_branch == "pypi" and not args.dry_run:
        if not confirm("⚠️ Are you sure you want to release to PRODUCTION PyPI?"):
            print("Aborted.")
            sys.exit(0)

    if args.dry_run:
        print(f"🧪 DRY RUN: Would push tag {tag} to branch {current_branch}")
    else:
        run(f"git push origin {current_branch}")
        run(f"git push origin {tag}")
        print(f"🚀 Pushed tag {tag} to {current_branch}")


if __name__ == "__main__":
    main()
