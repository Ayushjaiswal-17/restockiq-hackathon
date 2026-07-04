def approve_po(po_draft, auto_approve_under_qty=50):
    """
    Simple human-in-loop gate: auto-approve small orders,
    flag large ones for manager review.
    """
    qty = po_draft.get("recommended_qty", 0)
    if isinstance(qty, str):
        try:
            qty = float(qty)
        except ValueError:
            qty = 0

    if qty <= auto_approve_under_qty:
        po_draft["status"] = "AUTO-APPROVED"
    else:
        po_draft["status"] = "PENDING MANAGER REVIEW"
    return po_draft