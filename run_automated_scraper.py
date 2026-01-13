#!/usr/bin/env python3
"""
Automated News Scraper Runner
Easy way to run the automated scraper service

Usage:
    python run_automated_scraper.py              # Run one test cycle
    python run_automated_scraper.py --continuous # Run continuous mode (08:00, 12:00, 16:00 WIB)
    python run_automated_scraper.py --help       # Show help
"""
import sys
import argparse
from services.automated_scraper import AutomatedScraperService

# Stock list - customize as needed
STOCK_LIST = [
    'BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII',
    'UNVR', 'GOTO', 'ACES', 'ICBP', 'EMTK', 'SUPA'
]


def main():
    parser = argparse.ArgumentParser(
        description='Automated News Scraper for Indonesian Stocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run one test cycle:
  python run_automated_scraper.py

  # Run continuous mode (scrapes at 08:00, 12:00, 16:00 WIB daily):
  python run_automated_scraper.py --continuous

  # Run continuous with custom schedule:
  python run_automated_scraper.py --continuous --times 09:00 13:00 17:00

  # Run test cycle for specific stocks only:
  python run_automated_scraper.py --stocks BBCA BBRI TLKM
        '''
    )

    parser.add_argument(
        '--continuous', '-c',
        action='store_true',
        help='Run in continuous mode with scheduled scraping'
    )

    parser.add_argument(
        '--times', '-t',
        nargs='+',
        default=['08:00', '12:00', '16:00'],
        help='Scrape times in HH:MM format WIB (default: 08:00 12:00 16:00)'
    )

    parser.add_argument(
        '--stocks', '-s',
        nargs='+',
        default=STOCK_LIST,
        help='List of stock codes to monitor (default: all)'
    )

    args = parser.parse_args()

    # Initialize service
    print(f"📊 Monitoring {len(args.stocks)} stocks: {', '.join(args.stocks)}")
    service = AutomatedScraperService(args.stocks)

    if args.continuous:
        # Run continuous mode
        print(f"🤖 Starting continuous mode...")
        print(f"📅 Schedule: {', '.join(args.times)} WIB daily")
        print(f"⚠️  Press Ctrl+C to stop\n")
        service.run_continuous(scrape_times=args.times)
    else:
        # Run one test cycle
        print("🧪 Running test cycle...\n")
        result = service.run_scraping_cycle()

        print(f"\n✅ Test cycle completed!")
        print(f"📊 Results:")
        print(f"  - Success: {result['success_count']}/{len(args.stocks)} stocks")
        print(f"  - Articles: {result['total_articles']}")
        print(f"  - Sources: {result['total_sources']}")

        if result['failed_stocks']:
            print(f"  - Failed: {', '.join(result['failed_stocks'])}")

        print(f"\n💡 Tip: Use --continuous flag to run scheduled scraping")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
