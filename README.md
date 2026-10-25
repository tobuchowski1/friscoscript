# friscoscript

Bot that keeps checking the Frisco.pl grocery store for an earlier delivery slot than the one you've booked, and switches your booking when it finds one.

## Background

In 2020 pandemic times online grocery stores were swarmed with orders.
Polish store frisco.pl had so many sudden customers that available time slots in Warsaw were all taken for weeks ahead of ordering time.
This created an issue as we didn't want either to leave home or to plan our orders weeks ahead.

## How it works

Every 15 seconds the script:

1. Refreshes the access token (at most once every 5 minutes).
2. Reads the delivery slot currently reserved in your cart.
3. Fetches the first open delivery window from the calendar.
4. If that window is on an earlier day than your reservation (and not before `earliest_date`), reserves it.

Errors are logged with a stack trace and the loop continues.

## Requirements

- Python 3
- An active frisco.pl account with a delivery slot already reserved in your cart

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

> **You need to paste a valid refresh token before every run.**
> Refresh tokens rotate: each refresh invalidates the previous token, so the value in the script goes stale after a run.

1. Log in at [frisco.pl](https://www.frisco.pl) in your browser.
2. Open DevTools → Network and find a request to `commerce.frisco.pl/connect/token`.
3. Copy these values into the top of `friscoscript.py`:
   - `refresh_token`: from the request body
   - `user_id`: from the `/api/users/<user_id>/...` request URLs
   - `visitor_id`: from the `X-Frisco-Visitorid` request header
4. Optionally set `earliest_date` to the earliest day you'd accept a delivery.

The latest refresh token is written to `token.txt` while the script runs. Paste it from there into `friscoscript.py` if you restart soon after stopping.

## Running

```bash
source .venv/bin/activate
python friscoscript.py
```

Stop it with `Ctrl+C`.
