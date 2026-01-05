#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def fmt_ts(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log-group", required=True)
    ap.add_argument("--log-stream", required=True)
    ap.add_argument("--region")
    ap.add_argument("--profile")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=10000)
    args = ap.parse_args()

    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    session = boto3.Session(**session_kwargs)

    client_kwargs = {}
    if args.region:
        client_kwargs["region_name"] = args.region
    logs = session.client("logs", **client_kwargs)

    out_fh = open(args.out, "w", encoding="utf-8") if args.out else sys.stdout

    token = None
    total = 0
    try:
        while True:
            kwargs = {
                "logGroupName": args.log_group,
                "logStreamName": args.log_stream,
                "limit": args.limit,
            }
            if token is None:
                kwargs["startFromHead"] = True
            else:
                kwargs["nextToken"] = token

            print(f"[debug] calling get_log_events token={token!r}", file=sys.stderr)
            resp = logs.get_log_events(**kwargs)

            events = resp.get("events", [])
            print(f"[debug] got {len(events)} events", file=sys.stderr)

            for ev in events:
                msg = ev.get("message", "")
                out_fh.write(f"{fmt_ts(ev['timestamp'])}\t{msg}")
                if not msg.endswith("\n"):
                    out_fh.write("\n")
                total += 1

            out_fh.flush()

            next_token = resp.get("nextForwardToken")
            print(f"[debug] nextForwardToken={next_token!r}", file=sys.stderr)

            if next_token == token:
                break
            token = next_token

        print(f"[debug] done; wrote {total} events", file=sys.stderr)

    except (ClientError, BotoCoreError) as e:
        print(f"[error] {e}", file=sys.stderr)
        raise
    finally:
        if args.out:
            out_fh.close()


if __name__ == "__main__":
    main()