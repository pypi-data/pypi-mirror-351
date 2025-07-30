"""
Command Line Interface for Beem SMS SDK
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .client import BeemSMSClient, SMSEncoding
from .exceptions import SMSError


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from file"""
    if config_path:
        config_file = Path(config_path)
    else:
        possible_paths = [
            Path.home() / ".beem_sms.json",
            Path.cwd() / "beem_sms.json",
            Path.cwd() / ".beem_sms.json",
        ]
        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break

    if config_file and config_file.exists():
        with open(config_file, "r") as f:
            return json.load(f)

    return {}


def send_command(args):
    """Handle send SMS command"""
    config = load_config(args.config)

    api_key = args.api_key or config.get("api_key")
    secret_key = args.secret_key or config.get("secret_key")

    if not api_key or not secret_key:
        print("Error: API key and secret key are required")
        sys.exit(1)

    client = BeemSMSClient(api_key, secret_key)

    encoding = SMSEncoding.UNICODE if args.unicode else SMSEncoding.PLAIN_TEXT

    try:
        if args.file:
            with open(args.file, "r") as f:
                recipients = [line.strip() for line in f if line.strip()]
        else:
            recipients = args.recipients

        if args.bulk:
            results = client.send_bulk_sms(
                source_addr=args.sender,
                recipients=recipients,
                message=args.message,
                encoding=encoding,
                batch_size=args.batch_size,
            )

            successful = sum(1 for r in results if r.success)
            print(f"Sent {successful}/{len(results)} batches successfully")

            if args.verbose:
                for i, result in enumerate(results):
                    status = "✓" if result.success else "✗"
                    print(f"Batch {i+1}: {status} {result.message}")
        else:
            response = client.send_sms(
                source_addr=args.sender,
                dest_addr=recipients,
                message=args.message,
                encoding=encoding,
            )

            if response.success:
                print(f"✓ SMS sent successfully! " f"Request ID: {response.request_id}")
            else:
                print(f"✗ Failed to send SMS: {response.message}")
                sys.exit(1)

    except SMSError as e:
        print(f"Error: {e}")
        sys.exit(1)


def validate_command(args):
    """Handle phone number validation command"""
    from .validators import PhoneNumberValidator

    if args.file:
        with open(args.file, "r") as f:
            numbers = [line.strip() for line in f if line.strip()]
    else:
        numbers = args.numbers

    for number in numbers:
        is_valid = PhoneNumberValidator.validate(number)
        cleaned = PhoneNumberValidator.clean(number) if is_valid else "Invalid"
        status = "✓" if is_valid else "✗"
        print(f"{status} {number} -> {cleaned}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Beem SMS Python SDK Command Line Interface"
    )
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    send_parser = subparsers.add_parser("send", help="Send SMS")
    send_parser.add_argument("--api-key", help="Beem API key")
    send_parser.add_argument("--secret-key", help="Beem secret key")
    send_parser.add_argument("--sender", "-s", required=True, help="Sender ID")
    send_parser.add_argument("--message", "-m", required=True, help="Message text")
    send_parser.add_argument(
        "--recipients", "-r", nargs="+", help="Recipient phone numbers"
    )
    send_parser.add_argument(
        "--file",
        "-f",
        help="File containing recipient phone numbers (one per line)",
    )
    send_parser.add_argument(
        "--unicode", "-u", action="store_true", help="Use Unicode encoding"
    )
    send_parser.add_argument(
        "--bulk", "-b", action="store_true", help="Send as bulk SMS"
    )
    send_parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for bulk SMS (default: 100)",
    )
    send_parser.set_defaults(func=send_command)

    validate_parser = subparsers.add_parser("validate", help="Validate phone numbers")
    validate_parser.add_argument(
        "--numbers", "-n", nargs="+", help="Phone numbers to validate"
    )
    validate_parser.add_argument(
        "--file",
        "-f",
        help="File containing phone numbers to validate (one per line)",
    )
    validate_parser.set_defaults(func=validate_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
