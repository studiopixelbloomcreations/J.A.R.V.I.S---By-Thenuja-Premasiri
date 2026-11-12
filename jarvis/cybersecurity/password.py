"""
Capability 53: Password Security Auditing (Entropy & Complexity)
Calculates Shannon entropy, character pool entropy, evaluates dictionary vulnerability,
detects sequential/repeated patterns and leetspeak substitutions,
estimates offline brute-force crack times, and verifies NIST SP 800-63B compliance.
"""

import math
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class PasswordAuditResult:
    score: int  # 0 to 100
    rating: str  # VERY_WEAK, WEAK, MODERATE, STRONG, VERY_STRONG
    shannon_entropy: float
    pool_entropy_bits: float
    length: int
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_symbols: bool
    is_common: bool
    patterns_found: List[str] = field(default_factory=list)
    estimated_crack_time_offline: str = ""
    estimated_crack_time_online: str = ""
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "rating": self.rating,
            "shannon_entropy": round(self.shannon_entropy, 2),
            "pool_entropy_bits": round(self.pool_entropy_bits, 1),
            "length": self.length,
            "has_uppercase": self.has_uppercase,
            "has_lowercase": self.has_lowercase,
            "has_digits": self.has_digits,
            "has_symbols": self.has_symbols,
            "is_common": self.is_common,
            "patterns_found": self.patterns_found,
            "estimated_crack_time_offline": self.estimated_crack_time_offline,
            "estimated_crack_time_online": self.estimated_crack_time_online,
            "recommendations": self.recommendations,
        }


class PasswordAuditor:
    """Evaluates password security, entropy, pattern vulnerability, and cracking resistance."""

    COMMON_PASSWORDS = {
        "123456", "password", "12345678", "qwerty", "123456789", "12345", "1234", "111111",
        "1234567", "dragon", "123123", "baseball", "football", "welcome", "monkey", "charlie",
        "donald", "admin", "p@ssw0rd", "p@ssword", "password123", "admin123", "master",
        "letmein", "sunshine", "princess", "trustno1", "superman", "iloveyou",
    }

    LEET_MAP = {
        "@": "a", "4": "a",
        "3": "e",
        "1": "i", "!": "i",
        "0": "o",
        "$": "s", "5": "s",
        "7": "t", "+": "t",
    }

    def __init__(self, additional_common: Optional[List[str]] = None):
        self.common_set = set(self.COMMON_PASSWORDS)
        if additional_common:
            self.common_set.update(p.lower() for p in additional_common)

    @staticmethod
    def calculate_shannon_entropy(password: str) -> float:
        """Calculates Shannon entropy in bits per character."""
        if not password:
            return 0.0
        frequencies: Dict[str, int] = {}
        for char in password:
            frequencies[char] = frequencies.get(char, 0) + 1
        entropy = 0.0
        length = len(password)
        for count in frequencies.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def calculate_pool_entropy(self, password: str) -> float:
        """Calculates total pool entropy bits: L * log2(PoolSize)."""
        if not password:
            return 0.0
        pool_size = 0
        if any(c.islower() for c in password):
            pool_size += 26
        if any(c.isupper() for c in password):
            pool_size += 26
        if any(c.isdigit() for c in password):
            pool_size += 10
        if any(not c.isalnum() for c in password):
            pool_size += 32

        if pool_size == 0:
            return 0.0
        return len(password) * math.log2(pool_size)

    def normalize_leetspeak(self, text: str) -> str:
        """Replaces common leetspeak substitutions with standard alphabet chars."""
        normalized = text.lower()
        for leet, char in self.LEET_MAP.items():
            normalized = normalized.replace(leet, char)
        return normalized

    def find_patterns(self, password: str) -> List[str]:
        """Detects sequential, repeated, and keyboard walk patterns."""
        patterns: List[str] = []
        low = password.lower()

        # Repeated characters (e.g. 'aaaa', '1111')
        if re.search(r"(.)\1{2,}", password):
            patterns.append("Repeated characters sequence (e.g. 3+ identical consecutive characters)")

        # Sequential numbers (e.g. '123', '456', '789')
        if any(seq in low for seq in ["012", "123", "234", "345", "456", "567", "678", "789", "890"]):
            patterns.append("Sequential numeric sequence (e.g. 123, 456)")

        # Sequential alphabet (e.g. 'abc', 'def')
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for i in range(len(alphabet) - 2):
            if alphabet[i:i+3] in low:
                patterns.append(f"Sequential alphabetical sequence ({alphabet[i:i+3]})")
                break

        # Keyboard walk (e.g. 'qwer', 'asdf', 'zxcv')
        walks = ["qwer", "wert", "erty", "rtyu", "tyui", "yuio", "uiop", "asdf", "sdfg", "dfgh", "zxcv"]
        for walk in walks:
            if walk in low:
                patterns.append(f"Keyboard walk sequence ({walk})")
                break

        return patterns

    def format_time_duration(self, seconds: float) -> str:
        """Human-readable crack time formatter."""
        if seconds < 1e-4:
            return "Instant (< 1 millisecond)"
        if seconds < 1:
            return "Instant (< 1 second)"
        if seconds < 60:
            return f"{round(seconds, 1)} seconds"
        if seconds < 3600:
            return f"{round(seconds / 60, 1)} minutes"
        if seconds < 86400:
            return f"{round(seconds / 3600, 1)} hours"
        if seconds < 86400 * 365:
            return f"{round(seconds / 86400, 1)} days"
        if seconds < 86400 * 365 * 1000:
            return f"{round(seconds / (86400 * 365), 1)} years"
        return f"{seconds / (86400 * 365):.1e} years (Centuries+)"

    def audit_password(self, password: str) -> PasswordAuditResult:
        """Performs comprehensive security and entropy evaluation of a password."""
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_symbols = any(not c.isalnum() for c in password)

        shannon = self.calculate_shannon_entropy(password)
        pool_entropy = self.calculate_pool_entropy(password)
        patterns = self.find_patterns(password)
        recommendations: List[str] = []

        # Common password check (both raw and leet-normalized)
        is_common = (
            password.lower() in self.common_set
            or self.normalize_leetspeak(password) in self.common_set
        )

        score = 0

        if is_common:
            score = 10
            recommendations.append("Password matches a known dictionary or common password list.")
        else:
            # Length scoring
            if length >= 16:
                score += 40
            elif length >= 12:
                score += 30
            elif length >= 8:
                score += 15
            else:
                score += 5
                recommendations.append("Increase password length to at least 12-16 characters.")

            # Diversity scoring
            diversity = sum([has_upper, has_lower, has_digits, has_symbols])
            score += diversity * 12

            # Entropy scoring
            if pool_entropy >= 80:
                score += 15
            elif pool_entropy >= 60:
                score += 10
            elif pool_entropy >= 40:
                score += 5

            # Deductions for patterns
            score -= len(patterns) * 10

        score = max(0, min(100, score))

        if score >= 85:
            rating = "VERY_STRONG"
        elif score >= 70:
            rating = "STRONG"
        elif score >= 50:
            rating = "MODERATE"
        elif score >= 30:
            rating = "WEAK"
        else:
            rating = "VERY_WEAK"

        # Crack time estimations
        # Combinations = 2 ^ pool_entropy
        combos = 2 ** min(pool_entropy, 128)
        # Offline high-performance GPU cluster: ~10^10 hashes/sec
        seconds_offline = (combos / 2) / 1e10
        # Online rate-limited: ~100 attempts/sec
        seconds_online = (combos / 2) / 100.0

        if is_common:
            time_offline = "Instant (Present in Rainbow tables / Wordlists)"
            time_online = "Seconds (Top wordlist dictionary attack)"
        else:
            time_offline = self.format_time_duration(seconds_offline)
            time_online = self.format_time_duration(seconds_online)

        if not has_upper:
            recommendations.append("Include uppercase letters (A-Z).")
        if not has_lower:
            recommendations.append("Include lowercase letters (a-z).")
        if not has_digits:
            recommendations.append("Include numeric digits (0-9).")
        if not has_symbols:
            recommendations.append("Include special characters/symbols (e.g. !@#$%^&*).")

        return PasswordAuditResult(
            score=score,
            rating=rating,
            shannon_entropy=shannon,
            pool_entropy_bits=pool_entropy,
            length=length,
            has_uppercase=has_upper,
            has_lowercase=has_lower,
            has_digits=has_digits,
            has_symbols=has_symbols,
            is_common=is_common,
            patterns_found=patterns,
            estimated_crack_time_offline=time_offline,
            estimated_crack_time_online=time_online,
            recommendations=recommendations,
        )

    def audit_password_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Verifies organization password policy against NIST SP 800-63B standards."""
        min_length = policy.get("min_length", 8)
        mandatory_rotation_days = policy.get("rotation_days", None)
        require_dictionary_screening = policy.get("check_compromised", False)

        findings = []
        is_compliant = True

        if min_length < 8:
            findings.append("NIST SP 800-63B requires minimum length of at least 8 characters.")
            is_compliant = False

        if mandatory_rotation_days and mandatory_rotation_days < 365:
            findings.append(
                "NIST SP 800-63B advises against arbitrary periodic password changes without evidence of compromise."
            )

        if not require_dictionary_screening:
            findings.append("NIST SP 800-63B mandates verification against lists of compromised passwords.")
            is_compliant = False

        return {
            "is_nist_compliant": is_compliant,
            "min_length_configured": min_length,
            "findings": findings,
        }
