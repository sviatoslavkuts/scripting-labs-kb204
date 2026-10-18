import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

HASH_ITERATIONS = 100000


class User:
    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ):
        self.username = username
        self.role = role
        self.active = active
        self.__password_hash = b""
        self.__password_salt = b""
        self.email = email

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        pattern = r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Недійсний формат email: {value}")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, HASH_ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_salt:
            return False
        check_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, HASH_ITERATIONS
        )
        return hmac.compare_digest(self.__password_hash, check_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status='{status}')"


class Admin(User):
    def __init__(self, username: str, email: str, active: bool = True):
        super().__init__(username, email, role="admin", active=active)
        self.permissions: set[str] = set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str}, permissions={self.permissions}"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = self.login_time

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            return False
        return (datetime.now(timezone.utc) - self.last_activity) <= timedelta(
            seconds=timeout_sec
        )


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.records: list[AuditRecord] = []

    def add_log(self, username: str, action: str):
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc), username=username, action=action
        )
        self.records.append(record)

    def show_all(self):
        for record in self.records:
            print(
                f"[{record.timestamp.isoformat()}] {record.username}: {record.action}"
            )


class UserAccount:
    SESSION_TIMEOUT_SEC = 900

    def __init__(self, user: User, audit_log: AuditLog = None):
        self.user = user
        self.session: Session | None = None
        self.audit_log = audit_log if audit_log else AuditLog()

    def login(self, username: str, password: str, ip: str):
        if not self.user.active:
            self.audit_log.add_log(username, "login_failure (inactive)")
            return False
        if self.user.username != username:
            self.audit_log.add_log(username, "login_failure (wrong username)")
            return False
        if self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True
        else:
            self.audit_log.add_log(username, "login_failure (wrong password)")
            return False

    def is_authenticated(self) -> bool:
        return bool(self.session and self.session.is_active(self.SESSION_TIMEOUT_SEC))

    def logout(self):
        if self.session:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str):
        if key == "user":
            return self.user
        elif key == "session":
            return self.session
        elif key == "audit_log":
            return self.audit_log
        else:
            raise KeyError(f"Невідомий ключ: {key}")

    def __setitem__(self, key: str, value):
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("Значення має бути об'єктом User")
            self.user = value
        elif key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError("Значення має бути об'єктом Session або None")
            self.session = value
        elif key == "audit_log":
            if not isinstance(value, AuditLog):
                raise TypeError("Значення має бути об'єктом AuditLog")
            self.audit_log = value
        else:
            raise KeyError(f"Не можна змінити ключ: {key}")
