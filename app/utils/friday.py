# python
from typing import Tuple, Any, List

import config
import requests


def _fmt(value: Any) -> str:
    return "" if value is None else str(value)


def _campaign_to_text(item: dict) -> str:
    lines = [
        f"Campaign: {_fmt(item.get('name'))}",
        f"Description: {_fmt(item.get('description'))}",
        f"Brand: {_fmt(item.get('brand_name'))}",
        f"Location: {_fmt(item.get('location'))}",
        f"Start date: {_fmt(item.get('start_date'))}",
        f"End date: {_fmt(item.get('end_date'))}",
        f"Kilometers per month: {_fmt(item.get('kilometers_per_month'))}",
        f"Pay per month: {_fmt(item.get('pay_per_month'))}",
        f"Max drivers: {_fmt(item.get('max_drivers'))}",
    ]
    return "\n".join(lines).strip()


def parse_all_info_from_response(response_json) -> list[Tuple[str, str]]:
    data = response_json.get("data", {})
    items = data.get("campaigns", [])

    result: list[Tuple[str, str]] = []
    for idx, item in enumerate(items, start=1):
        if isinstance(item, dict):
            name = item.get("name") or f"campaign-{idx}"
            content = _campaign_to_text(item)
        else:
            name = f"item-{idx}"
            content = str(item)
        result.append((name, content))
    return result


def get_ai_context() -> list[Tuple[str, str]]:
    url = f"{config.FRIDAY_API_URL}/api/ai-context"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return parse_all_info_from_response(response.json())
    except Exception as e:
        # Log the error if logging is set up, or print for now
        print(f"Error fetching AI context: {e}")
        return []