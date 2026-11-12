"""
Brand Intelligence, Social Media Management, and Creative Asset Management for J.A.R.V.I.S.
Covers Capabilities:
  - 87. Brand Intelligence (Brand guidelines, color consistency, tone of voice)
  - 88. Social Media Management (Post scheduling, hashtag strategy, copy drafts)
  - 89. Creative Asset Management (Asset cataloging, tags, resolution metadata)
"""

import os
import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, date, timedelta


class BrandIntelligence:
    """Capability 87: Brand Intelligence"""

    @staticmethod
    def create_brand_guidelines(
        brand_name: str,
        tagline: str,
        primary_palette: Dict[str, str],
        secondary_palette: Dict[str, str],
        typography_specs: Dict[str, str],
        tone_pillars: List[str]
    ) -> Dict[str, Any]:
        """
        Creates a structured brand identity specification and style guide.
        """
        return {
            "brand_identity": {
                "name": brand_name,
                "tagline": tagline,
                "created_at": date.today().isoformat()
            },
            "color_system": {
                "primary": primary_palette,
                "secondary": secondary_palette,
                "usage_rule": "60% dominant neutral, 30% brand secondary, 10% high-contrast primary accent"
            },
            "typography": {
                "headings": typography_specs.get("heading", "Inter, sans-serif"),
                "body": typography_specs.get("body", "Roboto, sans-serif"),
                "monospace": typography_specs.get("mono", "Fira Code, monospace")
            },
            "voice_and_tone": {
                "pillars": tone_pillars,
                "dos": [
                    "Use active, assertive verbs",
                    "Keep explanations crisp and data-backed",
                    "Maintain technological elegance and precision"
                ],
                "donts": [
                    "Avoid hyperbole and clickbait phrasing",
                    "Never use colloquial slangs or overly informal grammar",
                    "Do not clutter communications with unnecessary buzzwords"
                ]
            },
            "logo_clearspace_rule": "Maintain minimum 1.5x of the icon mark height as clear exclusion zone."
        }

    @staticmethod
    def audit_color_consistency(
        candidate_hex: str,
        brand_palette: Dict[str, str],
        max_delta_tolerance: float = 25.0
    ) -> Dict[str, Any]:
        """
        Audits color match against official brand swatches using Euclidean RGB distance.
        """
        def parse_hex(h: str) -> Tuple[int, int, int]:
            s = h.strip().lstrip("#")
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))

        cand_rgb = parse_hex(candidate_hex)

        matches = []
        for name, hex_val in brand_palette.items():
            b_rgb = parse_hex(hex_val)
            dist = math.sqrt(
                (cand_rgb[0] - b_rgb[0]) ** 2 +
                (cand_rgb[1] - b_rgb[1]) ** 2 +
                (cand_rgb[2] - b_rgb[2]) ** 2
            )
            matches.append({
                "swatch_name": name,
                "target_hex": hex_val.upper(),
                "euclidean_distance": round(dist, 2),
                "is_match": dist <= max_delta_tolerance
            })

        closest = min(matches, key=lambda x: x["euclidean_distance"])

        return {
            "candidate_color": candidate_hex.upper(),
            "closest_brand_swatch": closest["swatch_name"],
            "distance_to_closest": closest["euclidean_distance"],
            "is_on_brand": closest["is_match"],
            "evaluations": matches
        }

    @staticmethod
    def evaluate_tone_of_voice(copy_text: str, brand_pillars: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluates draft copy against brand voice standards:
        computes reading level, sentence length, formality, and pillar alignment.
        """
        pillars = brand_pillars or ["intelligent", "precise", "visionary", "concise"]
        words = copy_text.strip().split()
        total_words = len(words)
        sentences = [s for s in copy_text.split(".") if s.strip()]
        total_sentences = max(1, len(sentences))
        avg_sentence_len = total_words / total_sentences

        # Count matched tone vocabulary
        matched_pillars = [p for p in pillars if p.lower() in copy_text.lower()]

        # Simple formality check
        informal_markers = ["gonna", "wanna", "lol", "hey guys", "totally", "omg", "kinda"]
        detected_informal = [m for m in informal_markers if m in copy_text.lower()]

        formality_score = max(0.0, 100.0 - (len(detected_informal) * 25.0) - (15.0 if avg_sentence_len < 5 else 0))

        return {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "average_sentence_length": round(avg_sentence_len, 1),
            "formality_score_100": round(formality_score, 1),
            "detected_informal_markers": detected_informal,
            "aligned_pillars": matched_pillars,
            "recommendation": "Passes tone criteria" if formality_score >= 80 and not detected_informal else "Refine tone: remove conversational slang and strengthen authoritative structure."
        }


class SocialMediaManager:
    """Capability 88: Social Media Management"""

    PLATFORM_CONSTRAINTS = {
        "twitter": {"max_chars": 280, "max_hashtags": 2, "optimal_time": "12:00 PM"},
        "linkedin": {"max_chars": 3000, "max_hashtags": 5, "optimal_time": "08:30 AM"},
        "instagram": {"max_chars": 2200, "max_hashtags": 10, "optimal_time": "06:00 PM"},
        "youtube": {"max_chars": 5000, "max_hashtags": 3, "optimal_time": "03:00 PM"}
    }

    @classmethod
    def generate_post_schedule(
        cls,
        campaign_name: str,
        start_date: Optional[str] = None,
        duration_days: int = 7,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Builds a multi-platform content calendar with publication time slots.
        """
        active_platforms = platforms or ["linkedin", "twitter", "instagram"]
        s_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.today()

        schedule = []
        for d in range(duration_days):
            current_date = s_date + timedelta(days=d)
            for plat in active_platforms:
                cfg = cls.PLATFORM_CONSTRAINTS.get(plat.lower(), {"optimal_time": "10:00 AM"})
                schedule.append({
                    "date": current_date.isoformat(),
                    "day_of_week": current_date.strftime("%A"),
                    "platform": plat.capitalize(),
                    "recommended_publish_time": cfg["optimal_time"],
                    "content_pillar": "Thought Leadership" if d % 2 == 0 else "Product Architecture / Demo",
                    "media_format": "Carousel Slide" if plat == "linkedin" else ("Short Video / Clip" if plat == "instagram" else "Thread")
                })

        return {
            "campaign": campaign_name,
            "start_date": s_date.isoformat(),
            "duration_days": duration_days,
            "total_posts_planned": len(schedule),
            "calendar": schedule
        }

    @staticmethod
    def develop_hashtag_strategy(niche: str, campaign_focus: str) -> Dict[str, Any]:
        """
        Generates a tiered hashtag strategy: Broad, Community, and Brand-specific.
        """
        niche_clean = "".join(part.strip() for part in niche.split())
        focus_clean = "".join(part.strip() for part in campaign_focus.split())

        return {
            "tier_1_broad_reach": [f"#{niche_clean}", "#Technology", "#Innovation", "#ArtificialIntelligence"],
            "tier_2_community_targeted": [f"#{niche_clean}Community", f"#{focus_clean}Engineering", "#DevTools", "#DeepTech"],
            "tier_3_branded_campaign": [f"#{niche_clean}2026", f"#{focus_clean}Launch", "#JARVISSystem"],
            "platform_best_practices": {
                "twitter": "1 to 2 hashtags maximum embedded naturally in text",
                "linkedin": "3 to 5 hashtags placed at the bottom of the post",
                "instagram": "5 to 10 highly relevant niche tags",
                "youtube": "3 primary tags for top-level search metadata"
            }
        }

    @classmethod
    def draft_social_copy(
        cls,
        topic: str,
        platform: str = "linkedin",
        key_takeaway: str = "Autonomous execution accelerates productivity 10x.",
        call_to_action: str = "Read the technical whitepaper below."
    ) -> Dict[str, Any]:
        """
        Drafts customized platform-compliant post copy with hook, body, and CTA.
        """
        plat = platform.lower()
        limits = cls.PLATFORM_CONSTRAINTS.get(plat, {"max_chars": 1000})

        if plat == "twitter":
            copy = (
                f"Breakthrough in {topic}:\n\n"
                f"{key_takeaway}\n\n"
                f"Explore details: {call_to_action} #AI #Automation"
            )
        elif plat == "linkedin":
            copy = (
                f"We are fundamentally rethinking how we interact with {topic}.\n\n"
                f"Key Architectural Insight:\n"
                f"• {key_takeaway}\n\n"
                f"By eliminating cognitive friction, autonomous agents bridge the gap between intent and real execution.\n\n"
                f"👉 {call_to_action}\n\n"
                f"#ArtificialIntelligence #Engineering #AutonomousSystems #Innovation"
            )
        else:
            copy = (
                f"Inside {topic} ⚡\n\n"
                f"{key_takeaway}\n\n"
                f"Full breakdown in bio. 🚀\n\n"
                f"#CreativeAI #Workflow"
            )

        char_count = len(copy)

        return {
            "platform": platform,
            "character_count": char_count,
            "within_limit": char_count <= limits["max_chars"],
            "max_allowed_characters": limits["max_chars"],
            "post_copy": copy
        }


class CreativeAssetManager:
    """Capability 89: Creative Asset Management"""

    def __init__(self):
        self.catalog: Dict[str, Dict[str, Any]] = {}

    def catalog_asset(
        self,
        asset_id: str,
        file_name: str,
        media_type: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration_sec: Optional[float] = None,
        file_size_bytes: int = 1024,
        tags: Optional[List[str]] = None,
        color_space: str = "sRGB"
    ) -> Dict[str, Any]:
        """
        Ingests and indexes a media asset with resolution, aspect ratio, and metadata.
        """
        aspect_ratio = None
        if width and height and height > 0:
            aspect_ratio = f"{round(width / height, 2)}:1"

        sha256_mock = hashlib.sha256(f"{asset_id}_{file_name}_{file_size_bytes}".encode("utf-8")).hexdigest()

        entry = {
            "asset_id": asset_id,
            "file_name": file_name,
            "media_type": media_type.lower(),
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "duration_sec": duration_sec,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "color_space": color_space,
            "tags": tags or [],
            "checksum_sha256": sha256_mock,
            "ingested_at": datetime.now().isoformat()
        }

        self.catalog[asset_id] = entry
        return entry

    def search_catalog(
        self,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        media_type: Optional[str] = None,
        min_width: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches cataloged creative assets with multi-criteria filters.
        """
        results = []
        for asset in self.catalog.values():
            if query and (query.lower() not in asset["file_name"].lower() and query.lower() not in asset["asset_id"].lower()):
                continue
            if tag and tag.lower() not in [t.lower() for t in asset["tags"]]:
                continue
            if media_type and asset["media_type"] != media_type.lower():
                continue
            if min_width and (asset["width"] is None or asset["width"] < min_width):
                continue
            results.append(asset)
        return results

    @staticmethod
    def validate_delivery_specs(
        asset_metadata: Dict[str, Any],
        required_width: int,
        required_height: int,
        required_aspect_ratio: Optional[float] = None,
        max_size_mb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validates whether an asset conforms to broadcast or delivery specifications.
        """
        actual_w = asset_metadata.get("width")
        actual_h = asset_metadata.get("height")
        size_mb = asset_metadata.get("file_size_mb", 0.0)

        checks = []
        is_valid = True

        if actual_w != required_width or actual_h != required_height:
            is_valid = False
            checks.append(f"Resolution mismatch: got {actual_w}x{actual_h}, expected {required_width}x{required_height}")
        else:
            checks.append("Resolution matches requirement")

        if required_aspect_ratio and actual_w and actual_h:
            actual_ratio = actual_w / actual_h
            if abs(actual_ratio - required_aspect_ratio) > 0.02:
                is_valid = False
                checks.append(f"Aspect ratio deviation: got {round(actual_ratio, 2)}, expected {round(required_aspect_ratio, 2)}")
            else:
                checks.append("Aspect ratio conforms to spec")

        if max_size_mb and size_mb > max_size_mb:
            is_valid = False
            checks.append(f"File size exceeds ceiling: got {size_mb} MB, max allowed {max_size_mb} MB")

        return {
            "asset_id": asset_metadata.get("asset_id"),
            "conforms_to_specs": is_valid,
            "validation_log": checks
        }
