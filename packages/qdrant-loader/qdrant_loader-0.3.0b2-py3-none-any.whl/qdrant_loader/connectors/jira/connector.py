"""Jira connector implementation."""

import asyncio
import time
from collections.abc import AsyncGenerator
from datetime import datetime
from urllib.parse import urlparse

import requests
import structlog
from requests.auth import HTTPBasicAuth

from qdrant_loader.config.types import SourceType
from qdrant_loader.connectors.base import BaseConnector
from qdrant_loader.connectors.jira.config import JiraDeploymentType, JiraProjectConfig
from qdrant_loader.connectors.jira.models import (
    JiraAttachment,
    JiraComment,
    JiraIssue,
    JiraUser,
)
from qdrant_loader.core.document import Document

logger = structlog.get_logger(__name__)


class JiraConnector(BaseConnector):
    """Jira connector for fetching and processing issues."""

    def __init__(self, config: JiraProjectConfig):
        """Initialize the Jira connector.

        Args:
            config: The Jira configuration.

        Raises:
            ValueError: If required authentication parameters are not set.
        """
        super().__init__(config)
        self.config = config
        self.base_url = str(config.base_url).rstrip("/")

        # Initialize session
        self.session = requests.Session()

        # Set up authentication based on deployment type
        self._setup_authentication()

        self._last_sync: datetime | None = None
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_time = 0.0
        self._initialized = False

    def _setup_authentication(self):
        """Set up authentication based on deployment type."""
        if self.config.deployment_type == JiraDeploymentType.CLOUD:
            # Cloud uses Basic Auth with email:api_token
            if not self.config.token:
                raise ValueError("API token is required for Jira Cloud")
            if not self.config.email:
                raise ValueError("Email is required for Jira Cloud")

            self.session.auth = HTTPBasicAuth(self.config.email, self.config.token)
            logger.info("Configured Jira Cloud authentication with email and API token")

        else:
            # Data Center/Server uses Personal Access Token with Bearer authentication
            if not self.config.token:
                raise ValueError(
                    "Personal Access Token is required for Jira Data Center/Server"
                )

            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.config.token}",
                    "Content-Type": "application/json",
                }
            )
            logger.info(
                "Configured Jira Data Center authentication with Personal Access Token"
            )

    def _auto_detect_deployment_type(self) -> JiraDeploymentType:
        """Auto-detect the Jira deployment type based on the base URL.

        Returns:
            JiraDeploymentType: Detected deployment type
        """
        try:
            parsed_url = urlparse(str(self.base_url))
            hostname = parsed_url.hostname

            if hostname is None:
                # If we can't parse the hostname, default to DATACENTER
                return JiraDeploymentType.DATACENTER

            # Cloud instances use *.atlassian.net domains
            # Use proper hostname checking with endswith to ensure it's a subdomain
            if hostname.endswith(".atlassian.net") or hostname == "atlassian.net":
                return JiraDeploymentType.CLOUD

            # Everything else is likely Data Center/Server
            return JiraDeploymentType.DATACENTER
        except Exception:
            # If URL parsing fails, default to DATACENTER
            return JiraDeploymentType.DATACENTER

    async def __aenter__(self):
        """Async context manager entry."""
        if not self._initialized:
            self._initialized = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._initialized = False

    def _get_api_url(self, endpoint: str) -> str:
        """Construct the full API URL for an endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            str: Full API URL
        """
        return f"{self.base_url}/rest/api/2/{endpoint}"

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an authenticated request to the Jira API.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            dict: Response data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        async with self._rate_limit_lock:
            # Calculate time to wait based on rate limit
            min_interval = 60.0 / self.config.requests_per_minute
            now = time.time()
            time_since_last_request = now - self._last_request_time

            if time_since_last_request < min_interval:
                await asyncio.sleep(min_interval - time_since_last_request)

            self._last_request_time = time.time()

            url = self._get_api_url(endpoint)
            try:
                # For Data Center with PAT, headers are already set
                # For Cloud, use session auth
                if not self.session.headers.get("Authorization"):
                    kwargs["auth"] = self.session.auth

                response = await asyncio.to_thread(
                    self.session.request, method, url, **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to make request to {url}: {e}")
                # Log additional context for debugging
                logger.error(
                    "Request details",
                    method=method,
                    url=url,
                    deployment_type=self.config.deployment_type,
                    has_auth_header=bool(self.session.headers.get("Authorization")),
                    has_session_auth=bool(self.session.auth),
                )
                raise

    def _make_sync_request(self, jql: str, **kwargs):
        """
        Make a synchronous request to the Jira API, converting parameters as needed:
        - Format datetime values in JQL to 'yyyy-MM-dd HH:mm' format
        """
        # Format datetime values in JQL query
        for key, value in kwargs.items():
            if isinstance(value, datetime):
                formatted_date = value.strftime("%Y-%m-%d %H:%M")
                jql = jql.replace(f"{{{key}}}", f"'{formatted_date}'")

        # Use the new _make_request method for consistency
        params = {
            "jql": jql,
            "startAt": kwargs.get("start", 0),
            "maxResults": kwargs.get("limit", self.config.page_size),
            "expand": "changelog",
            "fields": "*all",
        }

        return asyncio.run(self._make_request("GET", "search", params=params))

    async def get_issues(
        self, updated_after: datetime | None = None
    ) -> AsyncGenerator[JiraIssue, None]:
        """
        Get all issues from Jira.

        Args:
            updated_after: Optional datetime to filter issues updated after this time

        Yields:
            JiraIssue objects
        """
        start_at = 0
        page_size = self.config.page_size
        total_issues = 0

        while True:
            jql = f'project = "{self.config.project_key}"'
            if updated_after:
                jql += f" AND updated >= '{updated_after.strftime('%Y-%m-%d %H:%M')}'"

            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": page_size,
                "expand": "changelog",
                "fields": "*all",
            }

            response = await self._make_request("GET", "search", params=params)

            if not response or not response.get("issues"):
                break
            logger.debug(
                f"Make request to Jira API >> Start: {start_at}, Page size: {page_size}, Total issues: {total_issues}"
            )
            issues = response["issues"]
            for issue in issues:
                yield self._parse_issue(issue)

            # Update total count if not set
            if total_issues == 0:
                total_issues = response.get("total", 0)

            # Check if we've processed all issues
            start_at += len(issues)
            if start_at >= total_issues:
                break

    def _parse_issue(self, raw_issue: dict) -> JiraIssue:
        """Parse raw Jira issue data into JiraIssue model.

        Args:
            raw_issue: Raw issue data from Jira API

        Returns:
            Parsed JiraIssue
        """
        fields = raw_issue["fields"]
        parent = fields.get("parent")
        parent_key = parent.get("key") if parent else None

        # Parse reporter with type assertion since it's required
        reporter = self._parse_user(fields["reporter"], required=True)
        assert reporter is not None  # For type checker

        jira_issue = JiraIssue(
            id=raw_issue["id"],
            key=raw_issue["key"],
            summary=fields["summary"],
            description=fields.get("description"),
            issue_type=fields["issuetype"]["name"],
            status=fields["status"]["name"],
            priority=fields.get("priority", {}).get("name"),
            project_key=fields["project"]["key"],
            created=datetime.fromisoformat(fields["created"].replace("Z", "+00:00")),
            updated=datetime.fromisoformat(fields["updated"].replace("Z", "+00:00")),
            reporter=reporter,
            assignee=self._parse_user(fields.get("assignee")),
            labels=fields.get("labels", []),
            attachments=[
                self._parse_attachment(att) for att in fields.get("attachment", [])
            ],
            comments=[
                self._parse_comment(comment)
                for comment in fields.get("comment", {}).get("comments", [])
            ],
            parent_key=parent_key,
            subtasks=[st["key"] for st in fields.get("subtasks", [])],
            linked_issues=[
                link["outwardIssue"]["key"]
                for link in fields.get("issuelinks", [])
                if "outwardIssue" in link
            ],
        )

        return jira_issue

    def _parse_user(
        self, raw_user: dict | None, required: bool = False
    ) -> JiraUser | None:
        """Parse raw Jira user data into JiraUser model.

        Args:
            raw_user: Raw user data from Jira API
            required: Whether this user field is required (e.g., reporter, author)

        Returns:
            Parsed JiraUser or None if raw_user is None and not required

        Raises:
            ValueError: If raw_user is None and required is True
        """
        if not raw_user:
            if required:
                raise ValueError("User data is required but not provided")
            return None

        # Handle different user formats between Cloud and Data Center
        # Cloud uses 'accountId', Data Center uses 'name' or 'key'
        account_id = raw_user.get("accountId")
        if not account_id:
            # Fallback to 'name' or 'key' for Data Center
            account_id = raw_user.get("name") or raw_user.get("key")

        if not account_id:
            if required:
                raise ValueError(
                    "User data missing required identifier (accountId, name, or key)"
                )
            return None

        return JiraUser(
            account_id=account_id,
            display_name=raw_user["displayName"],
            email_address=raw_user.get("emailAddress"),
        )

    def _parse_attachment(self, raw_attachment: dict) -> JiraAttachment:
        """Parse raw Jira attachment data into JiraAttachment model.

        Args:
            raw_attachment: Raw attachment data from Jira API

        Returns:
            Parsed JiraAttachment
        """
        # Parse author with type assertion since it's required
        author = self._parse_user(raw_attachment["author"], required=True)
        assert author is not None  # For type checker

        return JiraAttachment(
            id=raw_attachment["id"],
            filename=raw_attachment["filename"],
            size=raw_attachment["size"],
            mime_type=raw_attachment["mimeType"],
            content_url=raw_attachment["content"],
            created=datetime.fromisoformat(
                raw_attachment["created"].replace("Z", "+00:00")
            ),
            author=author,
        )

    def _parse_comment(self, raw_comment: dict) -> JiraComment:
        """Parse raw Jira comment data into JiraComment model.

        Args:
            raw_comment: Raw comment data from Jira API

        Returns:
            Parsed JiraComment
        """
        # Parse author with type assertion since it's required
        author = self._parse_user(raw_comment["author"], required=True)
        assert author is not None  # For type checker

        return JiraComment(
            id=raw_comment["id"],
            body=raw_comment["body"],
            created=datetime.fromisoformat(
                raw_comment["created"].replace("Z", "+00:00")
            ),
            updated=(
                datetime.fromisoformat(raw_comment["updated"].replace("Z", "+00:00"))
                if "updated" in raw_comment
                else None
            ),
            author=author,
        )

    async def get_documents(self) -> list[Document]:
        """Fetch and process documents from Jira.

        Returns:
            List[Document]: List of processed documents
        """
        documents = []

        # Collect all issues
        issues = []
        async for issue in self.get_issues():
            issues.append(issue)

        # Convert issues to documents
        for issue in issues:
            # Build content including comments
            content_parts = [issue.summary]
            if issue.description:
                content_parts.append(issue.description)

            # Add comments to content
            for comment in issue.comments:
                content_parts.append(
                    f"\nComment by {comment.author.display_name} on {comment.created.strftime('%Y-%m-%d %H:%M')}:"
                )
                content_parts.append(comment.body)

            content = "\n\n".join(content_parts)

            base_url = str(self.config.base_url).rstrip("/")
            document = Document(
                id=issue.id,
                content=content,
                content_type="text",
                source=self.config.source,
                source_type=SourceType.JIRA,
                created_at=issue.created,
                url=f"{base_url}/browse/{issue.key}",
                title=issue.summary,
                updated_at=issue.updated,
                is_deleted=False,
                metadata={
                    "project": self.config.project_key,
                    "issue_type": issue.issue_type,
                    "status": issue.status,
                    "key": issue.key,
                    "priority": issue.priority,
                    "labels": issue.labels,
                    "reporter": issue.reporter.display_name if issue.reporter else None,
                    "assignee": issue.assignee.display_name if issue.assignee else None,
                    "created": issue.created.isoformat(),
                    "updated": issue.updated.isoformat(),
                    "parent_key": issue.parent_key,
                    "subtasks": issue.subtasks,
                    "linked_issues": issue.linked_issues,
                    "comments": [
                        {
                            "id": comment.id,
                            "body": comment.body,
                            "created": comment.created.isoformat(),
                            "updated": (
                                comment.updated.isoformat() if comment.updated else None
                            ),
                            "author": (
                                comment.author.display_name if comment.author else None
                            ),
                        }
                        for comment in issue.comments
                    ],
                    "attachments": (
                        [
                            {
                                "id": att.id,
                                "filename": att.filename,
                                "size": att.size,
                                "mime_type": att.mime_type,
                                "created": att.created.isoformat(),
                                "author": (
                                    att.author.display_name if att.author else None
                                ),
                            }
                            for att in issue.attachments
                        ]
                        if issue.attachments
                        else []
                    ),
                },
            )
            documents.append(document)
            logger.debug(
                "Jira document created",
                document_id=document.id,
                source_type=document.source_type,
                source=document.source,
                title=document.title,
            )

        return documents
