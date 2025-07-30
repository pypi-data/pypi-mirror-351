# MS365Sync

A Python library for syncing files between Microsoft 365 SharePoint and local storage.

## Features

- 🔄 **Two-way sync detection**: Automatically detects added, modified, and deleted files
- 📁 **Hierarchical support**: Maintains folder structures during sync
- 🔐 **OAuth2 authentication**: Secure authentication using Microsoft Graph API
- 📊 **Detailed logging**: Comprehensive sync reports and file trees
- 🚀 **CLI and library**: Use as a command-line tool or import as a Python library
- ⚡ **Efficient**: Only downloads changed files to minimize bandwidth usage

## Installation

### From PyPI (when published)

```bash
pip install ms365sync
```

### From source

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
pip install -e .
```

### Development installation

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your project directory with the following variables:

```env
TENANT_ID=your-azure-tenant-id
CLIENT_ID=your-azure-app-client-id
CLIENT_SECRET=your-azure-app-client-secret
```

### Azure App Registration

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set application type to "Web"
5. Under "API permissions", add:
   - `Sites.Read.All` (to read SharePoint sites)
   - `Files.Read.All` (to read files)
   - `Files.ReadWrite.All` (if you need write access)
6. Generate a client secret under "Certificates & secrets"
7. Copy the Application (client) ID, Directory (tenant) ID, and client secret

## Usage

### Command Line Interface

```bash
# Basic sync
ms365sync

# Verbose output
ms365sync --verbose

# Dry run (see what would be synced)
ms365sync --dry-run

# Use custom config file
ms365sync --config /path/to/your/.env
```

### Python Library

```python
from ms365sync import SharePointSync

# Initialize the sync client
syncer = SharePointSync()

# Perform sync and get changes
changes = syncer.sync()

print(f"Added: {len(changes['added'])} files")
print(f"Modified: {len(changes['modified'])} files")
print(f"Deleted: {len(changes['deleted'])} files")
```

### Advanced Usage

```python
from ms365sync import SharePointSync
import os

# Custom configuration
os.environ['TENANT_ID'] = 'your-tenant-id'
os.environ['CLIENT_ID'] = 'your-client-id'
os.environ['CLIENT_SECRET'] = 'your-client-secret'

syncer = SharePointSync()

# Get SharePoint files without syncing
sp_files = syncer.get_sharepoint_files()
print(f"Found {len(sp_files)} files in SharePoint")

# Get local files
local_files = syncer.get_local_files()
print(f"Found {len(local_files)} local files")

# Compare without syncing
added, modified, deleted = syncer.compare_files(sp_files, local_files)
print(f"Would add: {len(added)}, modify: {len(modified)}, delete: {len(deleted)}")
```

## Configuration Options

The library uses the following configuration variables (set in `.env` or environment):

| Variable | Description | Required |
|----------|-------------|----------|
| `TENANT_ID` | Azure Active Directory tenant ID | Yes |
| `CLIENT_ID` | Azure app registration client ID | Yes |
| `CLIENT_SECRET` | Azure app registration client secret | Yes |

The following constants can be modified in the code:

```python
SHAREPOINT_HOST = "your-sharepoint-site.sharepoint.com"
SITE_NAME = "Your Site Name"  # Display name as seen in SharePoint
DOC_LIBRARY = "Your Document Library"  # Display name
LOCAL_ROOT = pathlib.Path("download")  # Local destination folder
```

## File Structure

```
ms365sync/
├── __init__.py          # Package initialization
├── sharepoint_sync.py   # Main sync logic
└── cli.py              # Command-line interface

download/                # Default local sync folder
sync_logs/              # Sync change logs (JSON)
```

## Sync Process

1. **Authentication**: Connects to Microsoft Graph API using OAuth2
2. **Discovery**: Recursively scans SharePoint document library
3. **Comparison**: Compares SharePoint files with local files by size and modification date
4. **Sync**: Downloads new/modified files, deletes files removed from SharePoint
5. **Logging**: Saves detailed change log to `sync_logs/sync_changes_TIMESTAMP.json`

## Error Handling

The library includes comprehensive error handling:

- **Authentication errors**: Clear messages for invalid credentials
- **Network errors**: Retry logic for temporary connection issues
- **File system errors**: Graceful handling of permission issues
- **API errors**: Proper handling of SharePoint/Graph API limitations

## Development

### Setting up development environment

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black ms365sync/
isort ms365sync/
```

### Type checking

```bash
mypy ms365sync/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.1.0
- Initial release
- Basic SharePoint to local sync functionality
- CLI interface
- Comprehensive logging and error handling

## Roadmap

- [ ] Implement dry-run mode
- [ ] Add configuration file support (YAML/JSON)
- [ ] Implement upload functionality (local to SharePoint)
- [ ] Add filtering options (file types, patterns)
- [ ] Add scheduled sync support
- [ ] Implement incremental sync optimization
- [ ] Add progress bars for large syncs
- [ ] Support for multiple SharePoint sites 