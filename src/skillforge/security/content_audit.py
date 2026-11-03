"""Static Content Auditor and Security Scanner for Agent Skills."""

import re
from typing import Dict, List, Tuple
from skillforge.database.models import TrustLevel


# Security patterns
RULE_OVERRIDE_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"override\s+(all\s+)?rules",
    r"bypass\s+(safety|security|policy|restrictions)",
    r"unrestricted\s+mode",
    r"disable\s+(approval|confirmation|prompts)",
    r"system\s+prompt\s+override",
]

CREDENTIAL_HARVESTING_PATTERNS = [
    r"(read|cat|type|open)\s+([^\n]+\.env)",
    r"(extract|dump|steal|export)\s+(passwords?|tokens?|cookies|keys)",
    r"(\.gemini|\.aws|\.ssh|\.gnupg)/",
    r"browser_profiles?|cookies\.sqlite",
    r"gcloud\s+auth\s+print-access-token",
]

DESTRUCTIVE_COMMAND_PATTERNS = [
    r"rm\s+-rf\s+[/~]",
    r"del\s+/[sfq]\s+[c-z]:\\",
    r"format\s+[c-z]:",
    r"mkfs\.",
    r"drop\s+database",
]

PIPED_SCRIPT_PATTERNS = [
    r"curl[^\n]+\|\s*(ba)?sh",
    r"Invoke-Expression\s*\(New-Object\s+Net\.WebClient\)",
]

SUSPICIOUS_NETWORK_PATTERNS = [
    r"https?://(?:[0-9]{1,3}\.){3}[0-9]{1,3}",  # raw IP addresses
    r"ngrok\.io|serveo\.net|localtunnel",
]


class ContentAuditor:
    def audit_skill_content(
        self,
        content: str,
        name: str,
        description: str,
        missing_files: List[str]
    ) -> Tuple[TrustLevel, float, List[str]]:
        """Audit skill content for security risks and calculate quality score.
        
        Returns:
            (trust_level, quality_score, security_flags)
        """
        flags: List[str] = []
        is_quarantined = False

        # 1. Rule override audit
        for pat in RULE_OVERRIDE_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                flags.append(f"Prompt injection / rule override pattern detected: {pat}")
                is_quarantined = True

        # 2. Credential harvesting audit
        for pat in CREDENTIAL_HARVESTING_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                flags.append(f"Credential access pattern detected: {pat}")
                is_quarantined = True

        # 3. Destructive command audit
        for pat in DESTRUCTIVE_COMMAND_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                flags.append(f"Destructive shell command pattern detected: {pat}")
                is_quarantined = True

        # 4. Suspicious network patterns
        for pat in SUSPICIOUS_NETWORK_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                flags.append(f"Suspicious raw IP / tunneling pattern: {pat}")

        # 5. Piped remote script patterns (informational warning, not quarantined)
        for pat in PIPED_SCRIPT_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                flags.append(f"Piped remote script download pattern detected: {pat}")

        # Quality scoring
        quality_score = 1.0

        # Check description truncation
        desc_clean = description.strip()
        if (
            desc_clean.endswith("...") or
            desc_clean.endswith(" and") or
            desc_clean.endswith(" with") or
            desc_clean.endswith(" or") or
            desc_clean.endswith(",")
        ):
            flags.append("Truncated or incomplete description detected")
            quality_score -= 0.25

        if len(desc_clean) < 20:
            flags.append("Very short description (< 20 chars)")
            quality_score -= 0.15

        # Check phantom missing files
        if missing_files:
            flags.append(f"Referenced files not found on disk: {len(missing_files)} file(s)")
            quality_score -= min(0.3, len(missing_files) * 0.1)

        # Check generic boilerplate
        if "this is a skill that helps you" in desc_clean.lower() or "template skill" in desc_clean.lower():
            quality_score -= 0.1

        quality_score = max(0.1, min(1.0, round(quality_score, 2)))

        # Determine trust level
        if is_quarantined:
            trust_level = TrustLevel.QUARANTINED
        elif flags:
            trust_level = TrustLevel.UNVERIFIED
        else:
            trust_level = TrustLevel.REVIEWED

        return trust_level, quality_score, flags
