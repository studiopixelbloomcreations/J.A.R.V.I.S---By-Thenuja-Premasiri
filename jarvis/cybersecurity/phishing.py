"""
Capability 54: Phishing Detection (Heuristic URL & Domain Analysis)
Analyzes URLs and domains for typo-squatting, homoglyph punycode attacks,
subdomain brand deception, high-risk TLDs, IP hostnames, and credential harvesting paths.
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class PhishingIndicator:
    rule_id: str
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    evidence: str


@dataclass
class PhishingAssessment:
    url: str
    domain: str
    verdict: str  # CLEAN, SUSPICIOUS, PHISHING
    risk_score: int  # 0 to 100
    brand_targeted: Optional[str] = None
    indicators: List[PhishingIndicator] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "domain": self.domain,
            "verdict": self.verdict,
            "risk_score": self.risk_score,
            "brand_targeted": self.brand_targeted,
            "indicators": [
                {
                    "rule_id": i.rule_id,
                    "name": i.name,
                    "severity": i.severity,
                    "description": i.description,
                    "evidence": i.evidence,
                }
                for i in self.indicators
            ],
        }


class PhishingDetector:
    """Heuristic URL and domain analysis engine for detecting phishing attacks."""

    POPULAR_BRANDS = [
        "google", "microsoft", "paypal", "apple", "amazon",
        "facebook", "netflix", "chase", "wellsfargo", "bankofamerica",
        "dropbox", "github", "linkedin", "twitter", "instagram",
    ]

    SUSPICIOUS_TLDS = {
        ".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq",
        ".buzz", ".club", ".work", ".click", ".live", ".fit",
        ".rest", ".monster", ".icu",
    }

    HARVESTING_KEYWORDS = [
        "login", "signin", "verify", "verification", "account",
        "banking", "secure", "security", "wallet", "credential",
        "update", "suspended", "confirm", "auth", "validate",
    ]

    def __init__(self, additional_brands: Optional[List[str]] = None):
        self.brands = list(self.POPULAR_BRANDS)
        if additional_brands:
            self.brands.extend([b.lower() for b in additional_brands])

    @staticmethod
    def is_ip_address(host: str) -> bool:
        """Checks if hostname is an IPv4 or IPv6 address."""
        ipv4_pat = r"^(\d{1,3}\.){3}\d{1,3}$"
        return bool(re.match(ipv4_pat, host)) or ":" in host

    def detect_typosquatting(self, domain_label: str) -> Optional[str]:
        """Detects leetspeak/character substitution typo-squatting against target brands."""
        clean = domain_label.lower()
        substitutions = {
            "0": "o", "1": "l", "l": "i", "i": "l", "5": "s", "vv": "w",
        }
        for brand in self.brands:
            if clean == brand:
                continue
            # Direct leet normalization
            test_str = clean
            for s, r in substitutions.items():
                test_str = test_str.replace(s, r)
            if test_str == brand:
                return brand

            # Single character substitution / edit distance
            if len(clean) == len(brand):
                diffs = sum(1 for c1, c2 in zip(clean, brand) if c1 != c2)
                if diffs == 1:
                    return brand
        return None

    def analyze_url(self, url: str) -> PhishingAssessment:
        """Evaluates a URL across multiple phishing indicators and computes risk score."""
        indicators: List[PhishingIndicator] = []
        brand_targeted = None
        risk_score = 0

        # Handle schemes
        parsed = urllib.parse.urlparse(url if "://" in url else "http://" + url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()

        # 1. IP address in hostname
        if self.is_ip_address(host):
            indicators.append(
                PhishingIndicator(
                    rule_id="PHISH-IP-HOST",
                    name="IP Address Used as Hostname",
                    severity="HIGH",
                    description="The URL uses a raw IP address instead of a registered domain name.",
                    evidence=host,
                )
            )
            risk_score += 35

        # 2. Punycode / Homoglyph attack
        if "xn--" in host:
            indicators.append(
                PhishingIndicator(
                    rule_id="PHISH-PUNYCODE",
                    name="Punycode Homoglyph Detected",
                    severity="HIGH",
                    description="Domain contains internationalized (IDN/Punycode) characters commonly used for lookalike spoofing.",
                    evidence=host,
                )
            )
            risk_score += 40

        # 3. HTTP Basic Auth deception (@ symbol in authority)
        if "@" in parsed.netloc:
            indicators.append(
                PhishingIndicator(
                    rule_id="PHISH-AT-SYMBOL",
                    name="Embedded Userinfo '@' in URL",
                    severity="CRITICAL",
                    description="The URL uses the '@' character to obscure the true target destination.",
                    evidence=parsed.netloc,
                )
            )
            risk_score += 50

        # 4. Suspicious TLD
        for tld in self.SUSPICIOUS_TLDS:
            if host.endswith(tld):
                indicators.append(
                    PhishingIndicator(
                        rule_id="PHISH-SUSPICIOUS-TLD",
                        name="High-Risk Top-Level Domain (TLD)",
                        severity="MEDIUM",
                        description=f"Domain registered under high-risk or commonly abused TLD: {tld}",
                        evidence=tld,
                    )
                )
                risk_score += 20
                break

        # 5. Excessive subdomains
        host_parts = [p for p in host.split(".") if p]
        if len(host_parts) >= 4 and not self.is_ip_address(host):
            indicators.append(
                PhishingIndicator(
                    rule_id="PHISH-DEEP-SUBDOMAIN",
                    name="Excessive Subdomain Depth",
                    severity="MEDIUM",
                    description=f"Domain has {len(host_parts)} labels, often used to conceal true domain identity.",
                    evidence=host,
                )
            )
            risk_score += 15

        # 6. Brand hijacking in subdomain
        # e.g., paypal.com.attacker.com
        if len(host_parts) > 2:
            subdomains = ".".join(host_parts[:-2])
            for brand in self.brands:
                if brand in subdomains:
                    brand_targeted = brand
                    indicators.append(
                        PhishingIndicator(
                            rule_id="PHISH-BRAND-SUBDOMAIN",
                            name=f"Brand Deception in Subdomain ({brand})",
                            severity="CRITICAL",
                            description=f"Legitimate brand name '{brand}' appears in the subdomain while the apex domain is '{'.'.join(host_parts[-2:])}'.",
                            evidence=subdomains,
                        )
                    )
                    risk_score += 50
                    break

        # 7. Typo-squatting on apex domain label
        if len(host_parts) >= 2:
            apex_label = host_parts[-2]
            typo_brand = self.detect_typosquatting(apex_label)
            if typo_brand:
                brand_targeted = typo_brand
                indicators.append(
                    PhishingIndicator(
                        rule_id="PHISH-TYPOSQUAT",
                        name=f"Typo-Squatting / Lookalike Domain ({typo_brand})",
                        severity="CRITICAL",
                        description=f"Apex domain '{apex_label}' is a deceptive lookalike of '{typo_brand}'.",
                        evidence=apex_label,
                    )
                )
                risk_score += 55

        # 8. Credential harvesting keywords in path or query
        url_full_text = f"{path}?{parsed.query}".lower()
        matched_keywords = [kw for kw in self.HARVESTING_KEYWORDS if kw in url_full_text]
        if len(matched_keywords) >= 2:
            indicators.append(
                PhishingIndicator(
                    rule_id="PHISH-KEYWORDS",
                    name="Credential Harvesting Keywords in Path",
                    severity="MEDIUM",
                    description=f"URL contains sensitive security/login terminology: {matched_keywords}",
                    evidence=", ".join(matched_keywords),
                )
            )
            risk_score += 25
        elif len(matched_keywords) == 1:
            risk_score += 10

        risk_score = min(100, risk_score)

        if risk_score >= 60:
            verdict = "PHISHING"
        elif risk_score >= 30:
            verdict = "SUSPICIOUS"
        else:
            verdict = "CLEAN"

        return PhishingAssessment(
            url=url,
            domain=host,
            verdict=verdict,
            risk_score=risk_score,
            brand_targeted=brand_targeted,
            indicators=indicators,
        )
