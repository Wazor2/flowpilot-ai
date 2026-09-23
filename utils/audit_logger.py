from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from backend.database import SessionLocal
from backend.models import AuditEvent


class AuditLogger:
    """Persist workflow audit events in PostgreSQL; never fall back to a JSON file."""

    def log_event(
        self,
        agent_name: str,
        action: str,
        details: dict[str, Any],
        *,
        workflow_id: Optional[str] = None,
        tool: Optional[str] = None,
        status: Optional[str] = None,
        approval_state: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        db = SessionLocal()
        try:
            db.add(AuditEvent(
                id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                event_type=action,
                actor=agent_name,
                tool=tool,
                status=status,
                input_summary=json.dumps(details, default=str)[:2000],
                result_summary=None,
                approval_state=approval_state,
                reason=reason,
                summary=json.dumps(details, default=str)[:2000],
                metadata_json=details,
            ))
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_logs(self, workflow_id: Optional[str] = None) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            query = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc())
            if workflow_id:
                query = query.filter(AuditEvent.workflow_id == workflow_id)
            return [
                {
                    "id": event.id,
                    "workflow_id": event.workflow_id,
                    "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                    "event_type": event.event_type,
                    "actor": event.actor,
                    "tool": event.tool,
                    "status": event.status,
                    "input_summary": event.input_summary,
                    "result_summary": event.result_summary,
                    "approval_state": event.approval_state,
                    "reason": event.reason,
                }
                for event in query.all()
            ]
        finally:
            db.close()
