import json
from collections.abc import Sequence
from typing import Any

import boto3

from app.core.config import settings


class SqsService:
    def __init__(self) -> None:
        session_kwargs: dict[str, Any] = {}
        if settings.aws_profile:
            session_kwargs["profile_name"] = settings.aws_profile

        session = boto3.session.Session(**session_kwargs)
        client_kwargs: dict[str, Any] = {
            "region_name": settings.aws_region,
        }
        if settings.aws_sqs_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_sqs_endpoint_url
        self._client = session.client("sqs", **client_kwargs)

    def send_json_message(
        self,
        *,
        queue_url: str,
        payload: dict[str, Any],
        message_group_id: str | None = None,
        message_deduplication_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "QueueUrl": queue_url,
            "MessageBody": json.dumps(payload),
        }
        if message_group_id:
            params["MessageGroupId"] = message_group_id
        if message_deduplication_id:
            params["MessageDeduplicationId"] = message_deduplication_id
        return self._client.send_message(**params)

    def receive_messages(
        self,
        *,
        queue_url: str,
        max_number: int = 1,
        wait_time_seconds: int = 10,
        visibility_timeout: int = 30,
    ) -> Sequence[dict[str, Any]]:
        response = self._client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
        )
        return response.get("Messages", [])

    def delete_message(self, *, queue_url: str, receipt_handle: str) -> None:
        self._client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
