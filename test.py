import boto3
logs = boto3.client("logs", region_name="us-gov-west-1")

lg = "/aws/lambda/my-function"
prefix = "2026/01/05/"  # or whatever prefix matches your stream

resp = logs.describe_log_streams(
    logGroupName=lg,
    logStreamNamePrefix=prefix,
    orderBy="LastEventTime",
    descending=True,
    limit=5,
)
for s in resp.get("logStreams", []):
    print(s["logStreamName"], s.get("storedBytes"), s.get("lastEventTimestamp"))