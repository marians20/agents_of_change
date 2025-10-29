"""
API Usage Tracker for monitoring Alpha Vantage API calls.
Helps track daily usage against the 25 requests/day free tier limit.
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APIUsageTracker:
    """Tracks API usage to monitor against rate limits."""

    def __init__(self, storage_path: str = ".api_usage.json"):
        """
        Initialize the usage tracker.

        Args:
            storage_path: Path to store usage data
        """
        self.storage_path = Path(storage_path)
        self._usage_data = self._load_usage()

    def _load_usage(self) -> Dict:
        """Load usage data from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load usage data: {e}")
        return {}

    def _save_usage(self) -> None:
        """Save usage data to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self._usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save usage data: {e}")

    def _get_today_key(self) -> str:
        """Get the storage key for today's date."""
        return date.today().isoformat()

    def record_api_call(self, endpoint: str = "unknown") -> None:
        """
        Record an API call.

        Args:
            endpoint: Name of the API endpoint called
        """
        today = self._get_today_key()

        if today not in self._usage_data:
            self._usage_data[today] = {
                "count": 0,
                "endpoints": {},
                "first_call": datetime.now().isoformat(),
                "last_call": None
            }

        self._usage_data[today]["count"] += 1
        self._usage_data[today]["last_call"] = datetime.now().isoformat()

        # Track per-endpoint usage
        if endpoint not in self._usage_data[today]["endpoints"]:
            self._usage_data[today]["endpoints"][endpoint] = 0
        self._usage_data[today]["endpoints"][endpoint] += 1

        self._save_usage()

        # Log warning if approaching limit
        count = self._usage_data[today]["count"]
        if count >= 25:
            logger.error(f"⚠️ Daily API limit REACHED: {count}/25 calls today!")
        elif count >= 20:
            logger.warning(f"⚠️ Approaching daily API limit: {count}/25 calls today")
        elif count >= 15:
            logger.info(f"ℹ️ API usage: {count}/25 calls today")

    def get_today_usage(self) -> Dict:
        """
        Get today's usage statistics.

        Returns:
            Dictionary with usage stats
        """
        today = self._get_today_key()

        if today not in self._usage_data:
            return {
                "date": today,
                "count": 0,
                "limit": 25,
                "remaining": 25,
                "percentage": 0.0,
                "endpoints": {}
            }

        count = self._usage_data[today]["count"]
        return {
            "date": today,
            "count": count,
            "limit": 25,
            "remaining": max(0, 25 - count),
            "percentage": (count / 25) * 100,
            "endpoints": self._usage_data[today]["endpoints"],
            "first_call": self._usage_data[today].get("first_call"),
            "last_call": self._usage_data[today].get("last_call")
        }

    def can_make_request(self) -> bool:
        """
        Check if we can make another API request.

        Returns:
            True if under the limit, False otherwise
        """
        usage = self.get_today_usage()
        return usage["remaining"] > 0

    def get_usage_summary(self) -> str:
        """
        Get a formatted usage summary.

        Returns:
            Human-readable usage summary
        """
        usage = self.get_today_usage()

        summary = f"""
📊 Alpha Vantage API Usage Summary
═══════════════════════════════════
Date: {usage['date']}
Used: {usage['count']}/25 requests ({usage['percentage']:.1f}%)
Remaining: {usage['remaining']} requests

Endpoint Breakdown:
"""
        for endpoint, count in usage.get("endpoints", {}).items():
            summary += f"  • {endpoint}: {count} calls\n"

        if usage['first_call']:
            summary += f"\nFirst call: {usage['first_call']}"
        if usage['last_call']:
            summary += f"\nLast call:  {usage['last_call']}"

        return summary


# Create a singleton instance
api_usage_tracker = APIUsageTracker()
