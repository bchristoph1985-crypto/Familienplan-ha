"""Konstanten für Familienplan."""

DOMAIN = "familienplan"
STORAGE_VERSION = 1
SIGNAL_UPDATED = f"{DOMAIN}_updated"

ATTR_CHORE_ID = "chore_id"
ATTR_MEMBER = "member"
ATTR_NAME = "name"
ATTR_ASSIGNEES = "assignees"
ATTR_POINTS = "points"
ATTR_RECURRENCE = "recurrence"
ATTR_DUE = "due"
ATTR_ROTATION = "rotation"
ATTR_REQUIRES_APPROVAL = "requires_approval"

SERVICE_CREATE_CHORE = "create_chore"
SERVICE_DELETE_CHORE = "delete_chore"
SERVICE_CLAIM_CHORE = "claim_chore"
SERVICE_UNDO_CLAIM = "undo_claim"
SERVICE_APPROVE_CHORE = "approve_chore"
SERVICE_REJECT_CHORE = "reject_chore"
