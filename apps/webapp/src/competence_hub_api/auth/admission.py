from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class AdmissionPolicy:
    roles: frozenset[str]

    def allows(self, *, active: bool, roles: Iterable[str]) -> bool:
        return active and bool(self.roles.intersection(roles))


INTERNAL_ADMISSION = AdmissionPolicy(frozenset({"admin", "internal"}))
PORTAL_ADMISSION = AdmissionPolicy(
    INTERNAL_ADMISSION.roles | {"coach", "calendar_reviewer"}
)
