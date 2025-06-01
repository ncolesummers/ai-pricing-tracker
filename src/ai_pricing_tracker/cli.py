"""Command-line interface for AI Pricing Tracker"""

import argparse
import json
import sys

from .manager import PricingManager
from .exceptions import PricingNotFoundError


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AI Pricing Tracker - Get current AI API pricing")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List models command
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument("--provider", help="Filter by provider (e.g., anthropic, openai)")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Get pricing command
    get_parser = subparsers.add_parser("get", help="Get pricing for a model")
    get_parser.add_argument("provider", help="Provider name")
    get_parser.add_argument("model", help="Model name")

    # Calculate cost command
    calc_parser = subparsers.add_parser("calc", help="Calculate API call cost")
    calc_parser.add_argument("provider", help="Provider name")
    calc_parser.add_argument("model", help="Model name")
    calc_parser.add_argument("input_tokens", type=int, help="Input token count")
    calc_parser.add_argument("output_tokens", type=int, help="Output token count")

    # Update command
    subparsers.add_parser("update", help="Force update pricing data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = PricingManager()

    try:
        if args.command == "list":
            models = manager.list_models(args.provider)

            if args.json:
                output = {
                    k: {
                        "input": v.input_price,
                        "output": v.output_price,
                        "currency": v.currency,
                    }
                    for k, v in models.items()
                }
                print(json.dumps(output, indent=2))
            else:
                print(f"Available models (Last updated: {manager.get_last_updated()}):\n")
                for key, pricing in sorted(models.items()):
                    print(f"{key}:")
                    print(f"  Input:  ${pricing.input_price:>7.2f} per 1M tokens")
                    print(f"  Output: ${pricing.output_price:>7.2f} per 1M tokens")
                    print()

        elif args.command == "get":
            input_price, output_price = manager.get_model_pricing(args.provider, args.model)
            print(f"{args.provider}/{args.model}:")
            print(f"  Input:  ${input_price:.2f} per 1M tokens")
            print(f"  Output: ${output_price:.2f} per 1M tokens")

        elif args.command == "calc":
            cost = manager.calculate_cost(
                args.provider,
                args.model,
                args.input_tokens,
                args.output_tokens,
            )
            print(f"Cost calculation for {args.provider}/{args.model}:")
            print(f"  Input tokens:  {args.input_tokens:,}")
            print(f"  Output tokens: {args.output_tokens:,}")
            print(f"  Total cost:    ${cost:.6f}")

        elif args.command == "update":
            print("Updating pricing data...")
            manager.load_pricing(force_update=True)
            print(f"Updated successfully. Last updated: {manager.get_last_updated()}")

        return 0

    except PricingNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
