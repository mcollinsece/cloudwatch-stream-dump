import boto3
logs = boto3.client("logs", region_name="us-gov-west-1")

lg = "ccd-sort-sqs-writeback"
prefix = "sqs-writeback-"  # or whatever prefix matches your stream

# List streams with prefix (no orderBy to avoid API error)
streams = []
kwargs = {"logGroupName": lg, "logStreamNamePrefix": prefix, "limit": 50}

while True:
    resp = logs.describe_log_streams(**kwargs)
    streams.extend(resp.get("logStreams", []))
    token = resp.get("nextToken")
    if not token:
        break
    kwargs["nextToken"] = token

# Sort locally by lastEventTimestamp (newest first)
streams.sort(key=lambda s: s.get("lastEventTimestamp", 0), reverse=True)

# Show top 5
for s in streams[:5]:
    print(s["logStreamName"], s.get("storedBytes"), s.get("lastEventTimestamp"))
