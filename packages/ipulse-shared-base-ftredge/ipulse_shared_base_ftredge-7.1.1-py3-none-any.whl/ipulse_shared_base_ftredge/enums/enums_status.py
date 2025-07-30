# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

from enum import Enum, auto

class AutoStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    def __str__(self) -> str:
        return self.value

class Status(Enum):
    pass

class ProgressStatus(Status):

    # Skipped statuses
    DISABLED = 10
    INTENTIONALLY_SKIPPED = 20

    # Success statuses
    DONE= 200
    DONE_WITH_NOTICES = 205
    DONE_WITH_WARNINGS = 210

    # Pending statuses
    NOT_STARTED = 300
    STARTED=350
    IN_PROGRESS = 360
    IN_PROGRESS_WITH_NOTICES = 363
    IN_PROGRESS_WITH_WARNINGS = 364
    IN_PROGRESS_WITH_ISSUES = 365
    PAUSED = 370
    BLOCKED_BY_UNRESOLVED_DEPENDENCY = 380
    
    UNKNOWN = 400

    FINISHED_WITH_ISSUES= 510
    UNFINISHED = 610
    FAILED = 620

    def __str__(self):
        return self.name
    

    @classmethod
    def pending_statuses(cls):
        return frozenset({
            cls.UNKNOWN,
            cls.NOT_STARTED,
            cls.STARTED,
            cls.IN_PROGRESS,
            cls.IN_PROGRESS_WITH_ISSUES,
            cls.IN_PROGRESS_WITH_WARNINGS,
            cls.IN_PROGRESS_WITH_NOTICES,
            cls.PAUSED,
        })
    
    @classmethod
    def pending_or_blocked_statuses(cls):
        return frozenset.union(
            cls.pending_statuses(),
            {cls.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
        )
    


    @classmethod
    def skipped_statuses(cls):
        return frozenset({
            cls.INTENTIONALLY_SKIPPED,
            cls.DISABLED,
        })

    @classmethod
    def success_statuses(cls):
        return frozenset({
            cls.DONE,
            cls.DONE_WITH_NOTICES,
            cls.DONE_WITH_WARNINGS,
        })

    @classmethod
    def failure_statuses(cls):
        return frozenset({
            cls.FINISHED_WITH_ISSUES,
            cls.UNFINISHED,
            cls.FAILED,
        })
    
    @classmethod
    def issue_statuses(cls):
        return frozenset.union(
            cls.failure_statuses(),
            {cls.IN_PROGRESS_WITH_ISSUES,
            cls.UNKNOWN,
            cls.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
        )

    @classmethod
    def closed_statuses(cls):
        return frozenset.union(
            cls.success_statuses(),
            cls.failure_statuses()
        )

    @classmethod
    def closed_or_skipped_statuses(cls):
        return frozenset.union(
            cls.closed_statuses(),
            cls.skipped_statuses()
        )
    
    @classmethod
    def at_least_started_statuses(cls):
        return frozenset.union(
            frozenset({
                cls.STARTED,
                cls.IN_PROGRESS,
                cls.IN_PROGRESS_WITH_ISSUES,
                cls.IN_PROGRESS_WITH_WARNINGS,
                cls.IN_PROGRESS_WITH_NOTICES,
                cls.PAUSED,
            }),
            cls.closed_statuses()
        )

class ReviewStatus(AutoStrEnum, Status):
    OPEN = auto()
    ACKNOWLEDGED = auto()
    ESCALATED = auto()
    IN_PROGRESS = auto()
    IN_REVIEW = auto()
    RESOLVED = auto()
    IGNORED = auto()
    CANCELLED = auto()
    CLOSED = auto()

class ObjectOverallStatus(AutoStrEnum, Status):
    ACTIVE = auto()
    INACTIVE = auto()
    DELETED = auto()
    PENDING = auto()
    PAUSED = auto()
    ARCHIVED = auto()
    
class TradingStatus(AutoStrEnum, Status):
    TRADED_ON_PUBLIC_EXCHANGE = auto()
    TRADED_OTC = auto()
    TRADED_ON_PUBLIC_SITE_OR_APP = auto()
    NOT_FOR_SALE = auto()
    TRADED_VIA_BROKER = auto()
    UNLISTED = auto()
    PRIVATE = auto()
    DELISTED = auto()
    SUSPENDED = auto()
    LIQUIDATED = auto()
    DELIVERED = auto()
    BANKRUPT = auto()
    MERGED = auto()
    ACQUIRED = auto()
    EXPIRED = auto()
    EXERCISED = auto()
    REDEEMED = auto()
    CALLED = auto()
    UNKNOWN = auto()

class WorkScheduleStatus(AutoStrEnum, Status):
    OPEN = auto()
    CLOSED = auto()
    CANCELLED = auto()
    MAINTENANCE = auto()
    BREAK = auto()
    HOLIDAY = auto()
    UNREACHABLE = auto()
    PERMANENTLY_CLOSED = auto()
    TEMPORARILY_CLOSED = auto()
    UNKNOWN = auto()

class SubscriptionStatus(AutoStrEnum, Status):
    ACTIVE = auto()
    INACTIVE = auto()
    TRIAL = auto()
    PENDING = auto()
    CANCELLED = auto()
    EXPIRED = auto()
    SUSPENDED = auto()
    UNKNOWN = auto()

