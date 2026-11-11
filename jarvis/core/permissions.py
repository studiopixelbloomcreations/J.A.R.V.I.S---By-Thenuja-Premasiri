"""
Central Security and Permission Broker for J.A.R.V.I.S.
Enforces 4-tier risk classification, confirmation gates, audit logging, and global stop controls.
"""
import time
import uuid

# 4 Risk Tiers defined in PRD Section 8
RISK_READ_ONLY = "read_only"
RISK_REVERSIBLE = "reversible"
RISK_CONSEQUENTIAL = "consequential"
RISK_RESTRICTED = "restricted"


class PermissionBroker:
    def __init__(self):
        self.pending_approvals = {}
        self.audit_log = []
        self.automation_paused = False
        self.emergency_stop_triggered = False

    def check_permission(self, skill_id, risk_level, description, params=None):
        """
        Evaluates risk level and current safety state.
        Returns (allowed: bool, needs_approval: bool, approval_id: str or None, reason: str).
        """
        if self.emergency_stop_triggered or self.automation_paused:
            return False, False, None, "Automation is currently stopped or paused by user command."

        if risk_level == RISK_RESTRICTED:
            self.log_action(skill_id, "BLOCKED", f"Attempted restricted operation: {description}", params)
            return False, False, None, "Operation is restricted by security policy for system integrity."

        if risk_level == RISK_CONSEQUENTIAL:
            app_id = str(uuid.uuid4())[:8]
            self.pending_approvals[app_id] = {
                "id": app_id,
                "skill_id": skill_id,
                "risk_level": risk_level,
                "description": description,
                "params": params or {},
                "timestamp": int(time.time()),
                "status": "pending"
            }
            self.log_action(skill_id, "PENDING_APPROVAL", description, params)
            return False, True, app_id, f"Consequential action requires user confirmation: {description}"

        # Read-only and reversible are auto-allowed within granted permissions
        self.log_action(skill_id, "ALLOWED", description, params)
        return True, False, None, "Action permitted."

    def resolve_approval(self, approval_id, approved=True):
        """Approves or rejects a pending consequential operation."""
        req = self.pending_approvals.get(approval_id)
        if not req:
            return {"status": "error", "message": f"Approval request '{approval_id}' not found."}

        req["status"] = "approved" if approved else "rejected"
        req["resolved_at"] = int(time.time())
        self.log_action(
            req["skill_id"],
            "APPROVED" if approved else "REJECTED",
            f"User {'approved' if approved else 'rejected'} action: {req['description']}",
            req["params"]
        )
        return {"status": "success", "approval_id": approval_id, "approved": approved, "request": req}

    def trigger_emergency_stop(self):
        """Halts all automation immediately."""
        self.emergency_stop_triggered = True
        self.pending_approvals.clear()
        self.log_action("system", "EMERGENCY_STOP", "Global emergency stop engaged by user command.")
        return {"status": "success", "message": "Global emergency stop engaged. All active automation halted."}

    def reset_emergency_stop(self):
        self.emergency_stop_triggered = False
        self.log_action("system", "STOP_RESET", "Global stop reset. Systems restored.")
        return {"status": "success", "message": "Emergency stop cleared."}

    def toggle_pause(self, paused=None):
        self.automation_paused = not self.automation_paused if paused is None else bool(paused)
        status_text = "PAUSED" if self.automation_paused else "RESUMED"
        self.log_action("system", status_text, f"Automation {status_text.lower()} by user.")
        return {"status": "success", "paused": self.automation_paused}

    def log_action(self, skill_id, status, description, params=None):
        entry = {
            "id": len(self.audit_log) + 1,
            "skill_id": skill_id,
            "status": status,
            "description": description,
            "timestamp": int(time.time()),
            "params": params or {}
        }
        self.audit_log.append(entry)
        if len(self.audit_log) > 500:
            self.audit_log = self.audit_log[-500:]

    def get_audit_log(self, limit=50):
        return list(reversed(self.audit_log[-limit:]))

    def get_pending_approvals(self):
        return [req for req in self.pending_approvals.values() if req["status"] == "pending"]


# Global singleton broker
broker = PermissionBroker()
