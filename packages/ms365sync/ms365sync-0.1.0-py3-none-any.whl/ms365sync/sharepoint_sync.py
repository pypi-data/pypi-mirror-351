import json
import os
import pathlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import msal
import requests
from dotenv import load_dotenv

from .utils import print_file_tree

load_dotenv()

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
SCOPE = ["https://graph.microsoft.com/.default"]


class SharePointSync:
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        sharepoint_host: Optional[str] = None,
        site_name: Optional[str] = None,
        doc_library: Optional[str] = None,
        local_root: Optional[pathlib.Path] = None,
        sync_logs_dir: Optional[pathlib.Path] = None,
    ):
        """
        Initialize SharePoint sync client.

        Args:
            tenant_id: Azure tenant ID (defaults to TENANT_ID env var)
            client_id: Azure client ID (defaults to CLIENT_ID env var)
            client_secret: Azure client secret (defaults to CLIENT_SECRET
                env var)
            sharepoint_host: SharePoint hostname (defaults to hardcoded
                value)
            site_name: SharePoint site display name (defaults to hardcoded
                value)
            doc_library: Document library display name (defaults to
                hardcoded value)
            local_root: Local directory path (defaults to "download")
            sync_logs_dir: Directory for sync logs (defaults to "sync_logs")
        """
        # Configuration with fallbacks to environment variables or defaults
        self.tenant_id = tenant_id or os.environ.get("TENANT_ID")
        self.client_id = client_id or os.environ.get("CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("CLIENT_SECRET")

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required authentication parameters. "
                "Provide tenant_id, client_id, and client_secret, "
                "or set TENANT_ID, CLIENT_ID, and CLIENT_SECRET "
                "environment variables."
            )

        self.sharepoint_host = sharepoint_host or "rbapartnersdifc.sharepoint.com"
        self.site_name = site_name or "PhiChatTestSite"
        self.doc_library = doc_library or "Restricted Test PDFs"
        self.local_root = local_root or pathlib.Path("download")
        self.sync_logs_dir = sync_logs_dir or pathlib.Path("sync_logs")

        self.setup_auth()
        self.setup_site()

    def setup_auth(self) -> None:
        """Initialize authentication"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )

        token = app.acquire_token_for_client(scopes=SCOPE)
        if "access_token" not in token:
            error_desc = token.get('error_description', 'Unknown error')
            raise ValueError(f"Authentication failed: {error_desc}")

        self.headers = {"Authorization": f"Bearer {token['access_token']}"}

    def setup_site(self) -> None:
        """Get site and drive IDs"""
        try:
            site_url = (
                f"{GRAPH_ROOT}/sites/{self.sharepoint_host}:/sites/{self.site_name}"
            )
            site = requests.get(site_url, headers=self.headers)
            site.raise_for_status()
            self.site_id = site.json()["id"]

            drives_url = f"{GRAPH_ROOT}/sites/{self.site_id}/drives"
            drives = requests.get(drives_url, headers=self.headers)
            drives.raise_for_status()
            drives_data = drives.json()["value"]

            self.drive_id = next(
                (d["id"] for d in drives_data if d["name"] == self.doc_library), None
            )

            if not self.drive_id:
                available_drives = [d["name"] for d in drives_data]
                raise ValueError(
                    f"Document library '{self.doc_library}' not found. "
                    f"Available drives: {available_drives}"
                )

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to SharePoint: {e}")

    def get_sharepoint_files(self, folder_path: str = "") -> Dict[str, dict]:
        """Recursively get all files from SharePoint"""
        files: Dict[str, dict] = {}

        # Get items in current folder
        url = f"{GRAPH_ROOT}/drives/{self.drive_id}/root"
        if folder_path:
            url += f":/{folder_path}:"
        url += "/children"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            items = response.json().get("value", [])

            for item in items:
                if "folder" in item:
                    # Recursively process subfolders
                    subfolder_path = (
                        f"{folder_path}/{item['name']}" if folder_path else item["name"]
                    )
                    files.update(self.get_sharepoint_files(subfolder_path))
                elif "file" in item:
                    # Store file metadata
                    relative_path = (
                        f"{folder_path}/{item['name']}" if folder_path else item["name"]
                    )
                    files[relative_path] = {
                        "id": item["id"],
                        "name": item["name"],
                        "size": item["size"],
                        "last_modified": item["lastModifiedDateTime"],
                        "download_url": item.get("@microsoft.graph.downloadUrl"),
                        "relative_path": relative_path,
                    }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SharePoint files: {e}")

        return files

    def get_local_files(self) -> Dict[str, dict]:
        """Get all local files with their metadata"""
        files: Dict[str, dict] = {}

        if not self.local_root.exists():
            self.local_root.mkdir(parents=True, exist_ok=True)
            return files

        for file_path in self.local_root.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.local_root)).replace(
                    os.sep, "/"
                )
                stat = file_path.stat()
                files[relative_path] = {
                    "size": stat.st_size,
                    "last_modified": (
                        datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
                    ),
                    "local_path": file_path,
                }

        return files

    def download_file(self, sp_file: dict) -> bool:
        """Download a file from SharePoint"""
        try:
            local_path = self.local_root / sp_file["relative_path"]
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            response = requests.get(sp_file["download_url"])
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            print(f"Downloaded: {sp_file['relative_path']}")
            return True

        except Exception as e:
            print(f"Error downloading {sp_file['relative_path']}: {e}")
            return False

    def compare_files(
        self, sp_files: Dict[str, dict], local_files: Dict[str, dict]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Compare SharePoint and local files to detect changes"""
        added = []
        modified = []
        deleted = []

        # Find added and modified files
        for rel_path, sp_file in sp_files.items():
            if rel_path not in local_files:
                added.append(rel_path)
            else:
                local_file = local_files[rel_path]
                # Compare by size and last modified date
                sp_modified = datetime.fromisoformat(
                    sp_file["last_modified"].replace("Z", "+00:00")
                )
                local_modified = datetime.fromisoformat(
                    local_file["last_modified"].replace("Z", "+00:00")
                )

                if (
                    sp_file["size"] != local_file["size"]
                    or sp_modified > local_modified
                ):
                    modified.append(rel_path)

        # Find deleted files
        for rel_path in local_files:
            if rel_path not in sp_files:
                deleted.append(rel_path)

        return added, modified, deleted

    def sync(self) -> Dict[str, Union[List[str], int]]:
        """Main sync function - returns changes for RAG database updates"""
        print("Starting SharePoint sync...")

        # Get file lists
        print("Fetching SharePoint files...")
        sp_files = self.get_sharepoint_files()
        print(f"Found {len(sp_files)} files in SharePoint")

        print("Scanning local files...")
        local_files = self.get_local_files()
        print(f"Found {len(local_files)} local files")

        # Print tree structures for debugging
        print_file_tree(sp_files, "SHAREPOINT FILE TREE")
        print_file_tree(local_files, "LOCAL FILE TREE")

        # Compare and detect changes
        added, modified, deleted = self.compare_files(sp_files, local_files)

        print("\nChanges detected:")
        print(f"  Added: {len(added)}")
        print(f"  Modified: {len(modified)}")
        print(f"  Deleted: {len(deleted)}")

        # Download new and modified files
        for rel_path in added + modified:
            self.download_file(sp_files[rel_path])

        # Delete local files that no longer exist in SharePoint
        for rel_path in deleted:
            local_path = self.local_root / rel_path
            if local_path.exists():
                local_path.unlink()
                print(f"Deleted: {rel_path}")

                # Remove empty directories
                parent = local_path.parent
                while parent != self.local_root and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent

        print("\nSync completed successfully!")

        # Create sync_logs directory outside download folder
        sync_logs_dir = self.sync_logs_dir
        sync_logs_dir.mkdir(exist_ok=True)

        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        changes_file = sync_logs_dir / f"sync_changes_{timestamp}.json"

        # Save changes to JSON file for external processing
        with open(changes_file, "w") as f:
            json.dump(
                {
                    "added": added,
                    "modified": modified,
                    "deleted": deleted,
                    "total_files": len(sp_files),
                },
                f,
                indent=2,
            )
        print(f"\nChanges saved to: {changes_file}")

        # Return changes for RAG database updates
        return {
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "total_files": len(sp_files),
        }


def main() -> Optional[Dict[str, Union[List[str], int]]]:
    """Main function to run the sync"""
    try:
        syncer = SharePointSync()
        changes = syncer.sync()

        # Print summary for RAG database updates
        print("\n=== CHANGES FOR RAG DATABASE ===")
        if changes["added"]:
            print(f"ADD TO RAG: {changes['added']}")
        if changes["modified"]:
            print(f"UPDATE IN RAG: {changes['modified']}")
        if changes["deleted"]:
            print(f"REMOVE FROM RAG: {changes['deleted']}")

        return changes

    except Exception as e:
        print(f"Sync failed: {e}")
        return None


if __name__ == "__main__":
    main()
