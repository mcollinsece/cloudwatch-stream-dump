# CloudWatch Stream Dump

A Python utility to download all log events from a single AWS CloudWatch Logs stream.

## Description

This tool retrieves and dumps all log events from a specified CloudWatch Logs stream. It handles pagination automatically and can output to stdout or a file. Timestamps are formatted as ISO 8601 by default.

## Requirements

- Python 3.x
- boto3 (AWS SDK for Python)
- AWS credentials configured (via `~/.aws/credentials`, environment variables, or IAM role)

## Installation

1. Install boto3:
   ```bash
   pip install boto3
   ```

2. Ensure the script is executable (optional):
   ```bash
   chmod +x stream_dump.py
   ```

## Usage

### Basic Usage

```bash
python stream_dump.py --log-group /aws/lambda/my-function --log-stream 2024/01/01/[$LATEST]abc123
```

### Output to File

```bash
python stream_dump.py --log-group /aws/lambda/my-function --log-stream 2024/01/01/[$LATEST]abc123 --out logs.txt
```

### Using AWS Profile

```bash
python stream_dump.py --log-group /aws/lambda/my-function --log-stream 2024/01/01/[$LATEST]abc123 --profile my-profile
```

### Specify AWS Region

```bash
python stream_dump.py --log-group /aws/lambda/my-function --log-stream 2024/01/01/[$LATEST]abc123 --region us-east-1
```

### Without Timestamps

```bash
python stream_dump.py --log-group /aws/lambda/my-function --log-stream 2024/01/01/[$LATEST]abc123 --no-timestamps
```

## Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--log-group` | Yes | Log group name (e.g., `/aws/lambda/my-function`) |
| `--log-stream` | Yes | Log stream name |
| `--region` | No | AWS region (defaults to your AWS config) |
| `--profile` | No | AWS profile to use |
| `--out` | No | Output file path (defaults to stdout) |
| `--no-timestamps` | No | Do not prepend ISO timestamps to log messages |
| `--limit` | No | Max events per API call (default: 10000) |

## Output Format

By default, each log event is output with an ISO 8601 timestamp followed by a tab character and the log message:

```
2024-01-01T12:34:56.789+00:00	[INFO] Application started
2024-01-01T12:34:57.123+00:00	[ERROR] Something went wrong
```

With `--no-timestamps`, only the log messages are output:

```
[INFO] Application started
[ERROR] Something went wrong
```

## Examples

### Dump Lambda Function Logs

```bash
python stream_dump.py \
  --log-group /aws/lambda/my-function \
  --log-stream 2024/01/15/[$LATEST]a1b2c3d4e5f6 \
  --out lambda-logs.txt
```

### Pipe to Another Tool

```bash
python stream_dump.py \
  --log-group /aws/lambda/my-function \
  --log-stream 2024/01/15/[$LATEST]a1b2c3d4e5f6 \
  --no-timestamps | grep ERROR
```

### Use with Different AWS Account

```bash
python stream_dump.py \
  --log-group /aws/lambda/my-function \
  --log-stream 2024/01/15/[$LATEST]a1b2c3d4e5f6 \
  --profile production \
  --region us-west-2
```

## Notes

- The tool automatically handles pagination to retrieve all events from the stream
- CloudWatch log messages typically end with a newline, but the tool ensures all lines are properly terminated
- Timestamps are converted from CloudWatch's epoch milliseconds format to ISO 8601
- The default limit of 10,000 events per API call balances performance and API rate limits

## License

This is a utility script for personal/project use.
