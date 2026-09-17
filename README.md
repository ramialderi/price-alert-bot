# Telegram Price Alert Bot

A small, self-contained bot that checks a crypto coin's price (via the
free [CoinGecko](https://www.coingecko.com/en/api) API — no key needed)
and sends a Telegram message when it crosses a target you set. Runs on
a schedule via GitHub Actions — no server to manage.

This is meant as a minimal, working example: the same pattern (fetch →
compare → alert, on a schedule) generalizes to almost any monitoring
task — portfolio balances, on-chain events, exchange listings, website
uptime, etc.

## How it works

1. `price_alert.py` fetches the current price of one coin.
2. Compares it against `--target` using `--direction` (`above` or `below`).
3. If the condition is met, sends a Telegram message. If not, it just
   logs the check and exits — no message, no noise.

Each run is a single check. `.github/workflows/price-alert.yml` runs it
every 15 minutes automatically, or on demand.

## Setup

### 1. Create a Telegram bot and get your chat ID

1. Open Telegram, message **[@BotFather](https://t.me/BotFather)**, and
   send `/newbot`. Follow the prompts — you'll get a **bot token**
   (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyz`).
2. Start a chat with your new bot (search its username, hit Start), or
   add it to a group/channel you want alerts in.
3. Get your **chat ID**: message your bot anything, then visit
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
   and look for `"chat":{"id": ...}` in the response. For a group, this
   will be a negative number.

### 2. Add repository secrets

Settings → Secrets and variables → Actions → New repository secret:

| Secret name          | Value                          |
|-----------------------|--------------------------------|
| `TELEGRAM_BOT_TOKEN`  | The token from BotFather       |
| `TELEGRAM_CHAT_ID`    | The chat ID from step above    |

### 3. Run it

- **Manually**: Actions tab → Price Alert → Run workflow → set `coin`,
  `target`, `direction`, `currency`.
- **Automatically**: runs every 15 minutes once the workflow is on the
  default branch (edit the `cron:` line to change the interval).

### Local testing (no Telegram needed)

```bash
pip install -r requirements.txt
python price_alert.py --coin bitcoin --target 100000 --direction above --dry-run
```

`--dry-run` prints what would be sent instead of calling Telegram —
useful for checking your logic before wiring up real alerts.

## Extending this

This is intentionally minimal (single coin, no de-duplication of
repeated alerts while a condition stays true). Natural next steps for
a real client project:

- Multiple coins/targets in one run (loop over a config list)
- Only alert once per crossing (store last-alerted state, e.g. in a
  committed file or a tiny external key-value store)
- Different data sources (a specific exchange's API, on-chain data,
  a website's price page)
- Different alert channels (Discord webhook, email, SMS)

## License

MIT
