import argparse
import sys
import time
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, simpledialog
except ImportError:
    tk = None

from scanner import ProjectScanner
from document_generator import DocumentGenerator
from framework_profiles import ALL_PROFILES, FrameworkProfile
from framework_detector import detect_framework_details
from logger_setup import setup_logging


def select_folder_gui() -> Path:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select Project Root Folder")
    root.destroy()
    if not folder:
        raise SystemExit("No folder selected. Exiting.")
    return Path(folder)


def select_folder_cli() -> Path:
    path_str = input("Enter the project root path: ").strip()
    if not path_str:
        raise SystemExit("No path entered. Exiting.")
    path = Path(path_str)
    if not path.is_dir():
        raise SystemExit(f"Directory not found: {path}")
    return path


def get_project_root() -> Path:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.is_dir():
            return path
        print(f"Invalid path: {path}")
        print("Falling back to folder picker...")

    if tk is not None:
        try:
            return select_folder_gui()
        except Exception:
            pass

    return select_folder_cli()


def select_framework_gui(profiles: dict[str, FrameworkProfile]) -> FrameworkProfile:
    root = tk.Tk()
    root.title("Select Framework")
    root.attributes("-topmost", True)

    result = [None]

    label = tk.Label(root, text="Select the project framework:", font=("Consolas", 12))
    label.pack(padx=20, pady=(15, 10))

    listbox = tk.Listbox(root, font=("Consolas", 11), width=30, height=len(profiles))
    names = list(profiles.keys())
    for i, name in enumerate(names):
        listbox.insert(tk.END, f"{name} ({profiles[name].language})")
    listbox.pack(padx=20, pady=5)

    def on_select():
        sel = listbox.curselection()
        if sel:
            result[0] = profiles[names[sel[0]]]
            root.destroy()

    btn = tk.Button(root, text="OK", command=on_select, font=("Consolas", 11), width=10)
    btn.pack(pady=15)

    listbox.bind("<Double-Button-1>", lambda e: on_select())

    root.mainloop()

    if result[0] is None:
        raise SystemExit("No framework selected. Exiting.")
    return result[0]


def select_framework_cli(profiles: dict[str, FrameworkProfile]) -> FrameworkProfile:
    print("\nAvailable frameworks:")
    names = list(profiles.keys())
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name} ({profiles[name].language})")

    while True:
        choice = input(f"\nSelect framework [1-{len(names)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(names):
                return profiles[names[idx]]
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def get_framework(pick: str | None) -> FrameworkProfile:
    if pick:
        pick_lower = pick.lower()
        for name, profile in ALL_PROFILES.items():
            if pick_lower == name.lower() or pick_lower in name.lower():
                return profile
        print(f"Unknown framework: {pick}")
        print(f"Available: {', '.join(ALL_PROFILES.keys())}")
        raise SystemExit(1)

    if tk is not None:
        try:
            return select_framework_gui(ALL_PROFILES)
        except SystemExit:
            raise
        except Exception:
            pass

    return select_framework_cli(ALL_PROFILES)


def get_system_name() -> str:
    if tk is not None:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            name = simpledialog.askstring(
                "System Name",
                "Enter the system name:",
                initialvalue="",
                parent=root,
            )
            root.destroy()
            if name and name.strip():
                return name.strip()
        except Exception:
            pass

    name = input("Enter the system name (or press Enter for default): ").strip()
    return name if name else "Source Code Documentation"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Source Code Documentation Generator for IPOPHL Copyright Registration"
    )
    parser.add_argument("path", nargs="?", help="Project root path")
    parser.add_argument("--framework", "-f", help="Framework name (Laravel, Flask, Django, etc.)")
    parser.add_argument("--name", "-n", help="System name for the document title")
    parser.add_argument("--output", "-o", help="Output .docx filename")
    args = parser.parse_args()

    logger = setup_logging()
    start_time = time.time()

    print("\n" + "=" * 60)
    print("  Source Code Documentation Generator")
    print("  For IPOPHL Software Copyright Registration")
    print("=" * 60 + "\n")

    if args.path:
        project_root = Path(args.path)
        if not project_root.is_dir():
            print(f"Invalid path: {project_root}")
            print("Falling back to folder picker...")
            project_root = get_project_root()
    else:
        print("Selecting project folder...")
        project_root = get_project_root()
    print(f"Project: {project_root}\n")

    print("Detecting framework...")
    profile = None
    if args.framework:
        profile = get_framework(args.framework)
        print(f"  Framework: {profile.name} (from CLI)")
    else:
        detection = detect_framework_details(project_root)
        if detection:
            profile = detection.profile
            evidence = ", ".join(detection.evidence)
            print(f"  Auto-detected: {profile.name} ({detection.confidence:.0%} confidence)")
            print(f"  Evidence: {evidence}")
        else:
            print("  Could not auto-detect. Please select:")
            if tk is not None:
                profile = select_framework_gui(ALL_PROFILES)
            else:
                profile = select_framework_cli(ALL_PROFILES)
            print(f"  Selected: {profile.name}")

    system_name = args.name if args.name else ""
    if not system_name:
        system_name = get_system_name()
    if not system_name:
        system_name = project_root.name

    print(f"\nScanning...")
    scanner = ProjectScanner(project_root, profile)
    scan_result = scanner.scan()
    print(f"  Found {scan_result.total_files} files in {scan_result.total_folders} folders")
    print(f"  Skipped {scan_result.skipped_files} files")
    for reason, count in sorted(scan_result.skipped_reasons.items()):
        print(f"    - {reason}: {count}")

    if scan_result.errors:
        print(f"  {len(scan_result.errors)} errors encountered (see log)")

    print("\nProcessing...")
    output_name = args.output if args.output else f"{system_name} - Source Code Documentation.docx"
    output_path = project_root / output_name

    generator = DocumentGenerator()
    generator.generate(scan_result, output_path, profile, system_name)

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  Generation Complete!")
    print("=" * 60)
    print(f"  Document Location: {output_path}")
    print(f"  Framework:         {profile.name}")
    print(f"  Files Included:    {scan_result.total_files}")
    print(f"  Files Skipped:     {scan_result.skipped_files}")
    print(f"  Secrets Redacted:  {generator.total_secrets_redacted}")
    print(f"  Generation Time:   {elapsed:.1f} seconds")
    print("=" * 60)

    logger.info(f"Generation complete in {elapsed:.1f}s")
    logger.info(f"Framework: {profile.name}")
    logger.info(f"Files included: {scan_result.total_files}")
    logger.info(f"Files skipped: {scan_result.skipped_files}")
    logger.info(f"Secrets redacted: {generator.total_secrets_redacted}")
    logger.info(f"Output: {output_path}")


if __name__ == "__main__":
    main()
