"""
Command-line interface for MS365Sync.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .sharepoint_sync import SharePointSync


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync files between Microsoft 365 SharePoint and local storage"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to .env configuration file (default: .env in current directory)",
    )

    parser.add_argument(
        "--local-root",
        type=Path,
        help="Local directory for downloaded files (default: download)",
    )

    parser.add_argument(
        "--sync-logs-dir",
        type=Path,
        help="Directory for sync log files (default: sync_logs)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without actually downloading/deleting files",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="ms365sync {}".format(__import__("ms365sync").__version__),
    )

    parsed_args = parser.parse_args(args)

    try:
        # Set up environment if config file is specified
        if parsed_args.config:
            config_path = Path(parsed_args.config)
            if not config_path.exists():
                print(
                    f"Error: Configuration file {config_path} not found",
                    file=sys.stderr,
                )
                return 1

        # Initialize and run sync
        if parsed_args.verbose:
            print("Initializing SharePoint sync...")

        syncer = SharePointSync(
            local_root=parsed_args.local_root,
            sync_logs_dir=parsed_args.sync_logs_dir,
        )

        if parsed_args.dry_run:
            print("DRY RUN MODE: No files will be actually modified")
            # TODO: Implement dry-run functionality
            print("Dry-run mode not yet implemented")
            return 0

        changes = syncer.sync()

        if changes:
            print("\nSync completed successfully!")
            print("Total files synced: {}".format(changes.get("total_files", 0)))
            if changes.get("added"):
                added = changes["added"]
                if isinstance(added, list):
                    print(f"Files added: {len(added)}")
            if changes.get("modified"):
                modified = changes["modified"]
                if isinstance(modified, list):
                    print(f"Files modified: {len(modified)}")
            if changes.get("deleted"):
                deleted = changes["deleted"]
                if isinstance(deleted, list):
                    print(f"Files deleted: {len(deleted)}")
        else:
            print("Sync failed")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\nSync interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
