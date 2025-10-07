# Contentful Content Model Export/Import

This directory contains configuration files for exporting and importing a single content type between Contentful spaces using the Contentful CLI.

## Configuration

- **Source Space**: `3p2fxa94bzao` (master environment)
- **Destination Space**: `nuloos7fnddp` (dev environment)
- **Content Type**: `afIcon` (AF Icon)

## Prerequisites

- Contentful CLI installed and authenticated
- Access to both source and destination spaces

## Usage

### Option 1: Bash Script (Recommended)

The bash script uses the Contentful Management API directly to copy only the `afIcon` content type:

#### Setup:
1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Contentful Management API token:
   ```bash
   # Get your token from: Contentful Web App > Settings > API keys > Content management tokens
   CONTENTFUL_MANAGEMENT_TOKEN=your_actual_token_here
   ```

#### Run:
```bash
./copy-content-type.sh
```

This script will:
- ✅ Fetch the `afIcon` content type from the source space
- ✅ Create it in the destination space  
- ✅ Publish it automatically
- ✅ Handle errors gracefully

### Alternative: CLI Method (Not Recommended)

The Contentful CLI doesn't support filtering by content type, so it would export ALL content models from your source space. If you really need this approach:

```bash
# Export all content models (no filtering possible)
contentful space export --space-id 3p2fxa94bzao --environment-id master --skip-content --include-drafts --content-file export.json

# Import all content models  
contentful space import --space-id nuloos7fnddp --environment-id dev --content-file export.json
```

**Note**: This exports everything, not just the `afIcon` content type.

## Files

- `copy-content-type.sh` - Bash script to copy single content type via Management API ⭐
- `env.example` - Example environment file for API tokens
- `.env` - Your actual environment file (create from env.example)

## Notes

- Only the content model structure is exported/imported, not the actual content entries
- The export includes draft versions of the content type
- Make sure you have the necessary permissions for both spaces before running the commands

## Troubleshooting

If you encounter authentication issues, run:
```bash
contentful login
```

To verify your spaces and environments:
```bash
contentful space list
```
