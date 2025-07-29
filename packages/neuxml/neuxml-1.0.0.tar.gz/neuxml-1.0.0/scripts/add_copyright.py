# Copyright 2025 Center for Digital Humanities, Princeton University
# SPDX-License-Identifier: Apache-2.0

import argparse
import sys
import re
from pathlib import Path

# variables for adding copyright notice programmatically
COPYRIGHT_YEAR = "2025"
COPYRIGHT_HOLDER = "Center for Digital Humanities, Princeton University"
COPYRIGHT_STATEMENT = f"Copyright {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}"
SPDX_ID = "SPDX-License-Identifier: Apache-2.0"
SUPPORTED_TYPES = [".py", ".yaml", ".yml", ".toml"]

# regex to check if ANY copyright is present
COPYRIGHT_RE = re.compile(r"^\s*#\s*[Cc]opyright", re.MULTILINE)

# regex for existing emory copyright, keeping track of indentation
EUL_RE = re.compile(r"^(\s*#\s*)Copyright [\d,]+ Emory University", re.MULTILINE)


def main(arg_list=None):
    """Add or check for copyright statements"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check files for copyright notice",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames (may use glob pattern) to check or modify",
    )
    args = parser.parse_args(arg_list)

    check = args.check
    needs_copyright = []

    for filename in args.filenames:
        path = Path(filename)
        if (
            not path.is_file()  # skip non-files
            or ".github" in path.parts  # skip github workflows
            or path.name in ["lextab.py", "parsetab.py"]  # skip generated PLY files
            or "schema_data" in path.parts  # skip schema_data/* (xml from elsewhere)
            # skip test fixtures
            or any("fixtures" in part for part in path.parts if "test" in path.parts)
        ):
            continue

        try:
            contents = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # skip unreadable/binary files
            continue

        if not COPYRIGHT_RE.search(contents):
            # missing copyright: add to pre-commit check failures
            needs_copyright.append(filename)
            if not check and path.suffix in SUPPORTED_TYPES:
                # automatically add CDH copyright with SPDX identifier
                new_contents = f"# {COPYRIGHT_STATEMENT}\n# {SPDX_ID}\n\n{contents}"
                path.write_text(new_contents)
        elif not check and EUL_RE.search(contents):
            # has EUL copyright: add CDH copyright directly above
            new_contents = EUL_RE.sub(
                lambda m: f"{m.group(1)}{COPYRIGHT_STATEMENT}\n{m.group(0)}",
                contents,
            )
            path.write_text(new_contents)

    if check:
        # use exit code to tell pre-commit success or failure
        if needs_copyright:
            print("The following files are missing a copyright notice:")
            for f in needs_copyright:
                print(f" - {f}")
            sys.exit(1)
        print("All modified files have copyright notices.")
        sys.exit(0)


if __name__ == "__main__":
    main()
