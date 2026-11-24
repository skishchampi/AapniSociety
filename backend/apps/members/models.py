from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.geo.models import Building, Locality, Unit


class ServiceCategory(models.Model):
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "service categories"
        ordering = ["label"]

    def __str__(self):
        return self.label


class ContactVisibility(models.TextChoices):
    PRIVATE = "private", "Private — reveal only on consent"
    COOP = "coop", "Cooperative moderators only"


class WorkerProfile(models.Model):
    """Worker-owned profile. References, rates, and safety notes are added in later
    milestones; alpha.1 holds only identity, categories, languages, and a rate floor."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_profile"
    )
    display_name = models.CharField(max_length=120, blank=True)
    languages = models.JSONField(default=list, blank=True)
    service_categories = models.ManyToManyField(
        ServiceCategory, blank=True, related_name="workers"
    )
    localities_served = models.ManyToManyField(
        Locality, blank=True, related_name="workers"
    )
    availability = models.JSONField(default=dict, blank=True)
    default_rate_floor = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    contact_visibility = models.CharField(
        max_length=10,
        choices=ContactVisibility.choices,
        default=ContactVisibility.PRIVATE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WorkerProfile<{self.display_name or self.user.phone}>"


class HouseholdProfile(models.Model):
    """Household / tenant profile. No public resident directory is ever derived from this."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_profile",
    )
    display_name = models.CharField(max_length=120, blank=True)
    building = models.ForeignKey(
        Building, null=True, blank=True, on_delete=models.SET_NULL, related_name="households"
    )
    unit = models.ForeignKey(
        Unit, null=True, blank=True, on_delete=models.SET_NULL, related_name="households"
    )
    discoverable_to_coop = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HouseholdProfile<{self.display_name or self.user.phone}>"


class MembershipRequest(models.Model):
    """A signed-in user's ask to join the cooperative as worker or household.

    Approval flips `user.primary_role` to `role_sought`. One pending request
    per user, enforced at the database level.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership_requests"
    )
    role_sought = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="membership_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="pending"),
                name="uniq_pending_membership_request",
            )
        ]

    def __str__(self):
        return f"MembershipRequest<{self.user.phone} → {self.role_sought} ({self.status})>"


class ServiceNeed(models.Model):
    """A household's request for a service. Never public; moderators and the
    owning household can read it. Matching and offers arrive in later gates."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        MATCHED = "matched", "Matched"
        CLOSED = "closed", "Closed"

    household = models.ForeignKey(
        HouseholdProfile, on_delete=models.CASCADE, related_name="service_needs"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name="needs"
    )
    title = models.CharField(max_length=120)
    details = models.TextField(blank=True)
    locality = models.ForeignKey(
        Locality, null=True, blank=True, on_delete=models.SET_NULL, related_name="service_needs"
    )
    offered_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    matched_worker = models.ForeignKey(
        WorkerProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="matched_needs",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def below_floor(self) -> bool | None:
        if self.offered_rate is None or self.matched_worker is None:
            return None
        floor = self.matched_worker.default_rate_floor
        if floor is None:
            return None
        return self.offered_rate < floor

    def __str__(self):
        return f"ServiceNeed<{self.title} ({self.status})>"


class IntroductionRequest(models.Model):
    """A household's ask to meet a worker, routed by a moderator.

    Status flow: requested → routed → accepted | declined | withdrawn.
    Contact details stay hidden until the worker reveals them after an
    accept. Every transition writes an append-only IntroductionEvent.
    """

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ROUTED = "routed", "Routed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        WITHDRAWN = "withdrawn", "Withdrawn"

    household = models.ForeignKey(
        HouseholdProfile, on_delete=models.CASCADE, related_name="introductions"
    )
    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="intro_requests"
    )
    category = models.ForeignKey(
        ServiceCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="intros"
    )
    offered_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    routed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="intros_routed",
    )
    routed_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def below_floor(self) -> bool | None:
        if self.offered_rate is None or self.worker.default_rate_floor is None:
            return None
        return self.offered_rate < self.worker.default_rate_floor

    def record_event(self, actor, what: str, detail: str = "") -> "IntroductionEvent":
        return IntroductionEvent.objects.create(
            introduction=self, actor=actor, what=what, detail=detail
        )

    def __str__(self):
        return f"Introduction<{self.id} {self.status}>"


class IntroductionEvent(models.Model):
    """Append-only audit line for one introduction. Never updated or deleted."""

    class What(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ROUTED = "routed", "Routed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        WITHDRAWN = "withdrawn", "Withdrawn"
        CONTACT_REVEALED = "contact_revealed", "Contact revealed"

    introduction = models.ForeignKey(
        IntroductionRequest, on_delete=models.CASCADE, related_name="events"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="intro_events",
    )
    what = models.CharField(max_length=20, choices=What.choices)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"IntroductionEvent<{self.what} on intro {self.introduction_id}>"


class WorkerReference(models.Model):
    """Portable, worker-controlled reference grounded in an accepted introduction.

    Private by default. Never exposed as a public rating or leaderboard.
    """

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private — worker only"
        COOP = "coop", "Cooperative moderators"
        SHARED = "shared", "Shared inside routed introductions"

    introduction = models.OneToOneField(
        IntroductionRequest, on_delete=models.CASCADE, related_name="reference"
    )
    written_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="references_written"
    )
    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="references"
    )
    body = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"WorkerReference<{self.id} worker={self.worker_id} ({self.visibility})>"


class ReferenceRequest(models.Model):
    """A worker's invitation for a household to write a reference."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        WRITTEN = "written", "Written"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="reference_requests"
    )
    household = models.ForeignKey(
        HouseholdProfile, on_delete=models.CASCADE, related_name="reference_requests"
    )
    introduction = models.ForeignKey(
        IntroductionRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reference_requests",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ReferenceRequest<{self.id} worker={self.worker_id} ({self.status})>"


class WorkerBlock(models.Model):
    """A worker's private block against a household.

    Households can never read this table. Blocking stops new introductions
    and prevents routing open introductions from the blocked household.
    """

    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name="blocked_households"
    )
    household = models.ForeignKey(
        HouseholdProfile, on_delete=models.CASCADE, related_name="blocked_by_workers"
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["worker", "household"], name="uniq_worker_household_block"
            )
        ]

    def __str__(self):
        return f"WorkerBlock<worker={self.worker_id} blocked household={self.household_id}>"


class AbuseReport(models.Model):
    """Confidential abuse report filed for cooperative moderation."""

    class Category(models.TextChoices):
        HARASSMENT = "harassment", "Harassment"
        NON_PAYMENT = "non_payment", "Non-payment"
        CASTE_ABUSE = "caste_abuse", "Caste abuse"
        COMMUNAL_ABUSE = "communal_abuse", "Communal abuse"
        COERCION = "coercion", "Coercion"
        STALKING = "stalking", "Stalking"
        UNSAFE_CONDUCT = "unsafe_conduct", "Unsafe conduct"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWING = "reviewing", "Reviewing"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="abuse_reports_filed"
    )
    reported_household = models.ForeignKey(
        HouseholdProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="abuse_reports",
    )
    introduction = models.ForeignKey(
        IntroductionRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="abuse_reports",
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    details = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    resolution_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="abuse_reports_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AbuseReport<{self.id} {self.category} ({self.status})>"


class SafetyNote(models.Model):
    """Worker-authored city safety knowledge.

    Raw notes are never exposed to households, landlords, RWAs, or public search.
    """

    class NoteType(models.TextChoices):
        TRANSIT_RELIABILITY = "transit_reliability", "Transit reliability"
        NIGHT_ROUTE_RISK = "night_route_risk", "Night-route risk"
        HOSTILE_INSTITUTION = "hostile_institution", "Hostile institution"
        POLICE_OR_OFFICIAL_WARNING = (
            "police_or_official_warning",
            "Police-station or official-contact warning",
        )
        NON_PAYMENT_PATTERN = "non_payment_pattern", "Non-payment pattern"
        UNSAFE_BUILDING_OR_HOUSEHOLD = (
            "unsafe_building_or_household",
            "Unsafe building or household pattern",
        )

    class EvidenceLevel(models.TextChoices):
        FIRSTHAND = "firsthand", "Firsthand experience"
        SECONDHAND = "secondhand", "Secondhand report"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="safety_notes"
    )
    locality = models.ForeignKey(
        Locality, null=True, blank=True, on_delete=models.SET_NULL, related_name="safety_notes"
    )
    building = models.ForeignKey(
        Building, null=True, blank=True, on_delete=models.SET_NULL, related_name="safety_notes"
    )
    note_type = models.CharField(max_length=32, choices=NoteType.choices)
    evidence_level = models.CharField(max_length=12, choices=EvidenceLevel.choices)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SafetyNote<{self.id} {self.note_type} ({self.evidence_level})>"


class AdminAuditLog(models.Model):
    """Append-only record of every cooperative moderator/admin action."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_audit_logs",
    )
    action = models.CharField(max_length=40)
    target_type = models.CharField(max_length=40)
    target_id = models.PositiveIntegerField()
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AdminAuditLog<{self.action} {self.target_type}#{self.target_id}>"
