
def ksh(amount_cents: int) -> str:
    # Format cents to KSh with thousands separators, no decimals (MPesa works in shillings)
    shillings = int(amount_cents // 100)
    return f"KSh {shillings:,}"
