#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone

import boto3


def iso_ts(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds")


def list_streams(logs, log_group: str, prefix: str | None = None, limit: int = 50):
    streams = []
    kwargs = {"logGroupName": log_group, "limit": limit}
    if prefix:
        kwargs["logStreamNamePrefix"] = prefix

    while True:
        resp = logs.describe_log_streams(**kwargs)
        streams.extend(resp.get("logStreams", []))
        token = resp.get("nextToken")
        if not token:
            break
        kwargs["nextToken"] = token

    # Sort newest-first by lastEventTimestamp (works even when using prefix)
    streams.sort(key=lambda s: s.get("lastEventTimestamp", 0), reverse=True)
    return streams


def download_stream(logs, log_group: str, log_stream: str, out_fh, limit: int = 10000):
    token = None
    total = 0

    while True:
        kwargs = {
            "logGroupName": log_group,
            "logStreamName": log_stream,
            "limit": limit,
        }
        if token is None:
            kwargs["startFromHead"] = True
        else:
            kwargs["nextToken"] = token

        resp = logs.get_log_events(**kwargs)
        events = resp.get("events", [])

        for ev in events:
            msg = ev.get("message", "")
            out_fh.write(f"{iso_ts(ev['timestamp'])}\t{msg}")
            if not msg.endswith("\n"):
                out_fh.write("\n")
            total += 1

        out_fh.flush()

        next_token = resp.get("nextForwardToken")
        if next_token == token:
            break
        token = next_token

    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="us-gov-west-1")
    ap.add_argument("--log-group", required=True)
    ap.add_argument("--log-stream", help="Exact log stream name. If omitted, picks newest matching --prefix.")
    ap.add_argument("--prefix", help="Optional stream name prefix (used only if --log-stream not provided).")
    ap.add_argument("--profile", help="AWS profile (optional)")
    ap.add_argument("--out", default="-", help="Output file path or '-' for stdout")
    ap.add_argument("--limit", type=int, default=10000, help="Max events per API call")
    args = ap.parse_args()

    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    session = boto3.Session(**session_kwargs)
    logs = session.client("logs", region_name=args.region)

    stream = args.log_stream
    if not stream:
        streams = list_streams(logs, args.log_group, prefix=args.prefix)
        if not streams:
            raise SystemExit("No log streams found (check region/log group/prefix).")
        stream = streams[0]["logStreamName"]
        print(f"[info] selected newest stream: {stream}", file=sys.stderr)

    out_fh = sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")
    try:
        n = download_stream(logs, args.log_group, stream, out_fh, limit=args.limit)
        print(f"[info] wrote {n} events", file=sys.stderr)
    finally:
        if out_fh is not sys.stdout:
            out_fh.close()


if __name__ == "__main__":
    main()
