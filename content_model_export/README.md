# Contentful Content Model Export/Import

This directory contains configuration files for exporting and importing a single content type between Contentful spaces 
using the Contentful client by a bash script.

## Configuration

- **Source Space**: e.g.`3p2fxa94bzao` (affinity space)
- **Destination Space**: `nuloos7fnddp` (global space)
- **Content Type**: `afIcon` (AF Icon)

## Usage

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

3. Edit `copy-content-type.sh` to set the environment and content type you want to upload

#### Run:
```
bash copy-content-type.sh
```

This script will:
- ✅ Fetch the `afIcon` content type from the source space
- ✅ Create it in the destination space  
- ✅ Publish it automatically
