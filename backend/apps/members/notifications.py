"""Notification hooks for introduction transitions.

Alpha.3 wires the call sites only; delivery (SMS/push) is a later
milestone. Every transition funnels through `notify_introduction_event`,
so a real channel can attach here without touching view code.
"""

import logging

logger = logging.getLogger(__name__)


def notify_introduction_event(introduction, what: str) -> None:
    logger.info(
        "introduction event intro=%s what=%s", introduction.id, what
    )
