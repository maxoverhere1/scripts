#!/bin/bash

# Contentful Content Type Copy Script
# Copies a single content type from one space to another using the Management API

set -e  # Exit on any error

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    echo "Error: .env file not found. Please create it with your API tokens."
    echo "See .env.example for the required format."
    exit 1
fi

# Configuration
SOURCE_SPACE_ID="3p2fxa94bzao"
SOURCE_ENVIRONMENT="master"
DEST_SPACE_ID="nuloos7fnddp"
DEST_ENVIRONMENT="dev"
CONTENT_TYPE_ID="tabCard"

# Validate required environment variables
if [ -z "$CONTENTFUL_MANAGEMENT_TOKEN" ]; then
    echo "Error: CONTENTFUL_MANAGEMENT_TOKEN not set in .env file"
    exit 1
fi

echo "🚀 Starting content type copy process..."
echo "📥 Source: Space $SOURCE_SPACE_ID, Environment $SOURCE_ENVIRONMENT"
echo "📤 Destination: Space $DEST_SPACE_ID, Environment $DEST_ENVIRONMENT"
echo "📋 Content Type: $CONTENT_TYPE_ID"
echo ""

# Step 1: Fetch the content type from source space
echo "1️⃣ Fetching content type from source space..."
TEMP_FILE=$(mktemp)

curl -s \
  -H "Authorization: Bearer $CONTENTFUL_MANAGEMENT_TOKEN" \
  -H "Content-Type: application/vnd.contentful.management.v1+json" \
  "https://api.contentful.com/spaces/$SOURCE_SPACE_ID/environments/$SOURCE_ENVIRONMENT/content_types/$CONTENT_TYPE_ID" \
  > "$TEMP_FILE"

# Check if the request was successful
if ! jq -e '.sys.id' "$TEMP_FILE" > /dev/null 2>&1; then
    echo "❌ Error: Failed to fetch content type. Response:"
    cat "$TEMP_FILE"
    rm "$TEMP_FILE"
    exit 1
fi

echo "✅ Successfully fetched content type: $(jq -r '.name' "$TEMP_FILE")"

# Step 2: Clean the JSON for import (remove sys fields that shouldn't be copied)
echo "2️⃣ Preparing content type for import..."
CLEAN_FILE=$(mktemp)


jq 'del(.sys.createdAt, .sys.updatedAt, .sys.publishedAt, .sys.firstPublishedAt, .sys.createdBy, .sys.updatedBy, .sys.publishedBy, .sys.publishedVersion, .sys.publishedCounter, .sys.version, .sys.space, .sys.environment, .sys.urn)' "$TEMP_FILE" > "$CLEAN_FILE"

# Step 3: Create the content type in destination space
echo "3️⃣ Creating content type in destination space..."
RESPONSE_FILE=$(mktemp)

curl -s \
  -X PUT \
  -H "Authorization: Bearer $CONTENTFUL_MANAGEMENT_TOKEN" \
  -H "Content-Type: application/vnd.contentful.management.v1+json" \
  -d @"$CLEAN_FILE" \
  "https://api.contentful.com/spaces/$DEST_SPACE_ID/environments/$DEST_ENVIRONMENT/content_types/$CONTENT_TYPE_ID" \
  > "$RESPONSE_FILE"

# Check if creation was successful (check for error type first)
if jq -e '.sys.type == "Error"' "$RESPONSE_FILE" > /dev/null 2>&1; then
    echo "❌ Error: Failed to create content type. API Response:"
    jq '.' "$RESPONSE_FILE"
    
    # Check for specific error types
    ERROR_ID=$(jq -r '.sys.id // "Unknown"' "$RESPONSE_FILE")
    ERROR_MSG=$(jq -r '.message // "No message"' "$RESPONSE_FILE")
    
    echo ""
    echo "Error Details:"
    echo "  Type: $ERROR_ID"
    echo "  Message: $ERROR_MSG"
    
    if [[ "$ERROR_ID" == "ValidationFailed" ]]; then
        echo ""
        echo "💡 This usually means there's a validation error in the content type definition."
        echo "   Check the field definitions and constraints."
    elif [[ "$ERROR_MSG" == *"already exists"* ]]; then
        echo ""
        echo "💡 The content type already exists in the destination space."
        echo "   If you want to update it, you'll need to use a PUT request instead."
    fi
    
    rm "$TEMP_FILE" "$CLEAN_FILE" "$RESPONSE_FILE"
    exit 1
elif jq -e '.sys.id' "$RESPONSE_FILE" > /dev/null 2>&1; then
    echo "✅ Successfully created content type in destination space!"
    
    # Step 4: Publish the content type
    echo "4️⃣ Publishing content type..."
    VERSION=$(jq -r '.sys.version' "$RESPONSE_FILE")
    PUBLISH_RESPONSE=$(mktemp)
    
    curl -s \
      -X PUT \
      -H "Authorization: Bearer $CONTENTFUL_MANAGEMENT_TOKEN" \
      -H "Content-Type: application/vnd.contentful.management.v1+json" \
      -H "X-Contentful-Version: $VERSION" \
      "https://api.contentful.com/spaces/$DEST_SPACE_ID/environments/$DEST_ENVIRONMENT/content_types/$CONTENT_TYPE_ID/published" \
      > "$PUBLISH_RESPONSE"
    
    # Check if publishing was successful
    if jq -e '.sys.type == "Error"' "$PUBLISH_RESPONSE" > /dev/null 2>&1; then
        echo "⚠️  Warning: Failed to publish content type. Response:"
        jq '.' "$PUBLISH_RESPONSE"
        echo ""
        echo "✅ Content type created but not published. You can publish it manually in the web app."
    else
        echo "✅ Content type published successfully!"
    fi
    
    rm "$PUBLISH_RESPONSE"
    echo ""
    echo "🎉 Content type '$CONTENT_TYPE_ID' has been successfully copied!"
    echo "   You can now view it in the Contentful web app for space $DEST_SPACE_ID"
    
else
    echo "❌ Error: Unexpected response format. Raw response:"
    cat "$RESPONSE_FILE"
    rm "$TEMP_FILE" "$CLEAN_FILE" "$RESPONSE_FILE"
    exit 1
fi

# Cleanup
rm "$TEMP_FILE" "$CLEAN_FILE" "$RESPONSE_FILE"

echo ""
echo "🏁 Script completed!"
