"""Archive fetched raw source files to the private aerogrid-raw bucket.

WP-P3-H1 closes Phase 2 limitation L-010: the exact bytes behind a load are
written to a content-addressed object key and linked from
``project_staging.source_manifest.object_key`` before the transaction commits.
"""
from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

S3_ENV_KEYS = (
    "NEON_S3_ENDPOINT",
    "NEON_S3_REGION",
    "NEON_S3_BUCKET",
    "NEON_S3_ACCESS_KEY_ID",
    "NEON_S3_SECRET_ACCESS_KEY",
)
KEY_PREFIX = "raw"
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
_HEX = set("0123456789abcdef")


class RawArchiveConfigError(RuntimeError):
    """Raised when the approved object-storage environment is incomplete."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_file_name(name: str) -> str:
    cleaned = _SAFE_NAME.sub("_", Path(name).name).strip("._")
    return cleaned or "source.bin"


def content_addressed_key(sha256: str, file_name: str) -> str:
    digest = sha256.strip().lower()
    if len(digest) != 64 or any(char not in _HEX for char in digest):
        raise ValueError("sha256 must be a 64-character lowercase hex digest")
    return f"{KEY_PREFIX}/{digest}/{safe_file_name(file_name)}"


@dataclass(frozen=True)
class ArchiveConfig:
    endpoint: str
    region: str
    bucket: str
    access_key_id: str
    secret_access_key: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "ArchiveConfig":
        env = os.environ if environ is None else environ
        missing = [name for name in S3_ENV_KEYS if not str(env.get(name, "")).strip()]
        if missing:
            raise RawArchiveConfigError(
                "Missing required object-storage environment variable(s): "
                + ", ".join(missing)
            )
        endpoint = str(env["NEON_S3_ENDPOINT"]).strip()
        if not endpoint.startswith(("http://", "https://")):
            endpoint = f"https://{endpoint}"
        return cls(
            endpoint=endpoint,
            region=str(env["NEON_S3_REGION"]).strip(),
            bucket=str(env["NEON_S3_BUCKET"]).strip(),
            access_key_id=str(env["NEON_S3_ACCESS_KEY_ID"]).strip(),
            secret_access_key=str(env["NEON_S3_SECRET_ACCESS_KEY"]).strip(),
        )

    def client(self) -> Any:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore

        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            region_name=self.region or None,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=15,
                read_timeout=60,
            ),
        )


@dataclass(frozen=True)
class ArchivedObject:
    object_key: str
    sha256: str
    byte_size: int
    uploaded: bool


class RawArchive:
    def __init__(self, config: ArchiveConfig, *, client: Any | None = None) -> None:
        self.config = config
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = self.config.client()
        return self._client

    def put_file(self, path: Path, *, content_type: str | None = None) -> ArchivedObject:
        path = Path(path)
        digest = sha256_file(path)
        size = path.stat().st_size
        key = content_addressed_key(digest, path.name)
        if self._exists(key, size):
            return ArchivedObject(key, digest, size, uploaded=False)
        extra: dict[str, Any] = {"Metadata": {"sha256": digest}}
        if content_type:
            extra["ContentType"] = content_type
        self.client.upload_file(
            str(path), self.config.bucket, key, ExtraArgs=extra
        )
        return ArchivedObject(key, digest, size, uploaded=True)

    def _exists(self, key: str, size: int) -> bool:
        try:
            head = self.client.head_object(Bucket=self.config.bucket, Key=key)
        except Exception as exc:  # noqa: BLE001 - only a 404 means "absent"
            if _is_not_found(exc):
                return False
            raise
        return int(head.get("ContentLength", -1)) == size

    def fetch_sha256(self, object_key: str) -> str:
        with tempfile.TemporaryDirectory(prefix="raw-archive-") as tmp:
            dest = Path(tmp) / safe_file_name(object_key)
            self.client.download_file(self.config.bucket, object_key, str(dest))
            return sha256_file(dest)


def _is_not_found(exc: BaseException) -> bool:
    response = getattr(exc, "response", None) or {}
    code = str((response.get("Error") or {}).get("Code", ""))
    return code in {"404", "NoSuchKey", "NotFound"}
