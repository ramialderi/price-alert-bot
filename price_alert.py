#!/usr/bin/env python3
"""
price_alert.py
----------------
A small, self-contained Telegram price-alert bot for a single crypto asset.

It checks a coin's current price (via the free CoinGecko API — no key
needed), compares it against a target you set, and sends a Telegram
message if the condition is met (price went above / below the target).

Meant to run on a schedule (e.g. via GitHub Actions, see
.github/workflows/price-alert.yml) rather than as a long-running
process — each run is a single check-and-maybe-alert.

Usage:
    python price_alert.py --coin bitcoin --target 100000 --direction above

Requires two environment variables (set as GitHub Actions secrets, or
export locally for testing):
    TELEGRAM_BOT_TOKEN  - from @BotFather
    TELEGRAM_CHAT_ID    - the chat/user/channel to notify
"""

import argparse
import os
import sys

import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def fetch_price(coin: str, currency: str = "usd") -> float:
    """Return the current price of `coin` in `currency` from CoinGecko."""
    resp = requests.get(
        COINGECKO_URL,
        params={"ids": coin, "vs_currencies": currency},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if coin not in data or currency not in data[coin]:
        raise ValueError(
            f"No price data for coin='{coin}' currency='{currency}'. "
            f"Check the CoinGecko coin id (e.g. 'bitcoin', not 'BTC')."
        )
    return float(data[coin][currency])


def check_condition(price: float, target: float, direction: str) -> bool:
    """Pure logic, kept separate from I/O so it's easy to test."""
    if direction == "above":
        return price >= target
    if direction == "below":
        return price <= target
    raise ValueError(f"Unknown direction: {direction!r} (expected 'above' or 'below')")


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API.format(token=token)
    resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)
    resp.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Telegram crypto price alert (single check).")
    parser.add_argument("--coin", required=True, help="CoinGecko coin id, e.g. 'bitcoin', 'ethereum'")
    parser.add_argument("--target", required=True, type=float, help="Target price to compare against")
    parser.add_argument("--direction", required=True, choices=["above", "below"],
                         help="Alert when price goes 'above' or 'below' the target")
    parser.add_argument("--currency", default="usd", help="Quote currency (default: usd)")
    parser.add_argument("--dry-run", action="store_true",
                         help="Print what would be sent instead of calling Telegram")
    args = parser.parse_args()

    price = fetch_price(args.coin, args.currency)
    triggered = check_condition(price, args.target, args.direction)

    print(f"{args.coin}: current={price} {args.currency.upper()} "
          f"| target={args.target} ({args.direction}) | triggered={triggered}")

    if not triggered:
        return

    message = (
        f"🔔 تنبيه سعر\n"
        f"{args.coin.upper()} وصل {price:,.2f} {args.currency.upper()}\n"
        f"(الشرط: {args.direction} {args.target:,.2f})"
    )

    if args.dry_run:
        print("--dry-run set, not sending. Message would be:")
        print(message)
        return

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID not set.", file=sys.stderr)
        sys.exit(1)

    send_telegram_message(token, chat_id, message)
    print("Alert sent.")


if __name__ == "__main__":
    main()
