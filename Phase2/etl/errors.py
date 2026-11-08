from __future__ import annotations


class RowRejected(ValueError):
    def __init__(
        self,
        reason_code: str,
        detail: str = "",
        source_record_id: str | None = None,
    ) -> None:
        super().__init__(f"{reason_code}: {detail}" if detail else reason_code)
        self.reason_code = reason_code
        self.detail = detail
        self.source_record_id = source_record_id
