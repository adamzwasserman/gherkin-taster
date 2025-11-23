"""
Linear File Upload Service
Handles uploading files to Linear's private cloud storage
"""

import httpx
import base64
from typing import Optional


class LinearFileService:
    """Service for uploading files to Linear"""

    def __init__(self, linear_token: str):
        self.linear_token = linear_token
        self.api_url = "https://api.linear.app/graphql"

    async def upload_file(
        self,
        file_data: str,
        filename: str,
        content_type: str,
    ) -> Optional[str]:
        """
        Upload a file to Linear's cloud storage

        Args:
            file_data: Base64 encoded file data (with or without data URL prefix)
            filename: Name of the file
            content_type: MIME type (e.g., 'video/webm', 'audio/webm')

        Returns:
            Asset URL of the uploaded file, or None if upload failed
        """
        # Remove data URL prefix if present
        if file_data.startswith("data:"):
            file_data = file_data.split(",")[1]

        # Decode base64 to bytes
        file_bytes = base64.b64decode(file_data)
        file_size = len(file_bytes)

        # Step 1: Request upload URL from Linear
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.linear_token}"},
                json={
                    "query": """
                        mutation FileUpload($contentType: String!, $filename: String!, $size: Int!) {
                            fileUpload(contentType: $contentType, filename: $filename, size: $size) {
                                uploadFile {
                                    uploadUrl
                                    assetUrl
                                    headers {
                                        key
                                        value
                                    }
                                }
                            }
                        }
                    """,
                    "variables": {
                        "contentType": content_type,
                        "filename": filename,
                        "size": file_size,
                    },
                },
            )
            result = response.json()

        if not result or "errors" in result:
            print(f"Failed to get upload URL: {result}")
            return None

        upload_data = result["data"]["fileUpload"]["uploadFile"]
        upload_url = upload_data["uploadUrl"]
        asset_url = upload_data["assetUrl"]
        upload_headers = upload_data["headers"]

        # Step 2: Upload file to the pre-signed S3 URL
        headers = {
            "Content-Type": content_type,
            "Cache-Control": "public, max-age=31536000",
        }

        # Add headers from Linear response
        for header in upload_headers:
            headers[header["key"]] = header["value"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            upload_response = await client.put(
                upload_url,
                headers=headers,
                content=file_bytes,
            )

        if upload_response.status_code not in [200, 204]:
            print(f"Failed to upload file: {upload_response.status_code} {upload_response.text}")
            return None

        print(f"Successfully uploaded file: {filename} ({file_size} bytes) -> {asset_url}")
        return asset_url

    async def attach_to_issue(
        self,
        issue_id: str,
        asset_url: str,
        title: str,
    ) -> bool:
        """
        Attach an uploaded file to a Linear issue

        Args:
            issue_id: Linear issue ID (UUID, not identifier)
            asset_url: URL returned from upload_file
            title: Title for the attachment

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.linear_token}"},
                json={
                    "query": """
                        mutation AttachmentCreate($issueId: String!, $url: String!, $title: String!) {
                            attachmentCreate(input: {
                                issueId: $issueId
                                url: $url
                                title: $title
                            }) {
                                success
                                attachment {
                                    id
                                    url
                                }
                            }
                        }
                    """,
                    "variables": {
                        "issueId": issue_id,
                        "url": asset_url,
                        "title": title,
                    },
                },
            )
            result = response.json()

        if not result or "errors" in result:
            print(f"Failed to attach file: {result}")
            return False

        success = result["data"]["attachmentCreate"]["success"]
        if success:
            print(f"Successfully attached file to issue {issue_id}")
        return success
