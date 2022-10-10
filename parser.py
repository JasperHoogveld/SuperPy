# Imports
import argparse
from commands import buy_csv_writer
from commands import sell_csv_writer
from commands import buy_csv
from commands import sell_csv
from commands import get_profit
from commands import get_revenue
from commands import display_inventory
from commands import advance_date
from commands import reset_date

def parser():
    # Add a parser for commandline input
    parser = argparse.ArgumentParser(prog="Inventory Manager",
                                    description="Program to manage and report Store Inventory. \
                                    Use -h together with buy, sell, report or adv_date for more options")
    subparsers = parser.add_subparsers(dest='command')

    # Create a Buy Sub-parser
    buy_parser = subparsers.add_parser('buy', help='Add a bought product')
    buy_parser.add_argument("-prod", required=True, help="Enter a product to buy or sell", type=str)
    buy_parser.add_argument("-amount", required=True, help="Amount of items", type=int)
    buy_parser.add_argument("-price", required=True, help="Price per item", type=float)
    buy_parser.add_argument("-exp", required=True, help="Expiration date")

    # Create a Sell Sub-parser
    sell_parser = subparsers.add_parser('sell', help='Add a sold product')
    sell_parser.add_argument("-prod", required=True, help="Enter a product to buy or sell", type=str)
    sell_parser.add_argument("-amount", required=True, help="Amount of items", type=int)
    sell_parser.add_argument("-price", required=True, help="Price per item", type=float)

    # Create a Report Sub-parser
    report_parser = subparsers.add_parser('report', help='Report Inventory or Revenue/Profit over a time period')
    report_parser.add_argument('mode', choices=['inventory', 'revenue', 'profit'])
    report_parser.add_argument('-period', help="Enter a period for 'report revenue' or 'report profit'", type=str)

    # Create an Advance Date Sub-parser
    date_parser = subparsers.add_parser('adv_date',
                    help="Type a number of days you want to test in the future or reset back to today")
    date_parser.add_argument('mode', choices=['time_delta', 'reset'])
    date_parser.add_argument('-num_days', help="Use with 'adv_date time_delta' to advance time", type=int)

    # Create an Argument parser with if loops to check the input
    args = parser.parse_args()

    if args.command == 'buy':
        buy_csv_writer(buy_csv, args.prod, args.amount, args.price, args.exp)

    if args.command == 'sell':
        sell_csv_writer(sell_csv, args.prod, args.amount, args.price)

    if args.command == 'report':
        if args.mode == 'profit':
            get_profit(args.period)
        elif args.mode == 'revenue':
            get_revenue(args.period)
        elif args.mode == 'inventory':
            display_inventory()

    if args.command == 'adv_date':
        if args.mode == 'time_delta':
            advance_date(args.num_days)
        elif args.mode == 'reset':
            reset_date()
