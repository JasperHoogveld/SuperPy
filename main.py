# Imports
from asyncio.proactor_events import _ProactorBasePipeTransport
from genericpath import exists
import sys
import argparse
import csv
from datetime import date, datetime
from typing import Optional
import os.path
import shutil
from pathlib import Path

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.

today = datetime.now()
stoday = today.strftime("%Y-%m-%d")
smonth = today.strftime("%Y-%m")


def main():
    parser = argparse.ArgumentParser(prog="Inventory Manager",
                                    description="Program to edit/check store Inventory",
                                    epilog="I hope this is clear enough")
    subparsers = parser.add_subparsers(dest='command')

    buy_parser = subparsers.add_parser('buy', help='Add a bought product')
    buy_parser.add_argument("-prod", help="enter a product to buy or sell", type=str, nargs='?')
    buy_parser.add_argument("-amount", help="used with buy|sell options", type=int, nargs='?')
    buy_parser.add_argument("-price", help="used with buy|sell options", type=int, nargs='?')
    buy_parser.add_argument("-exp", help="used with buy|sell options", nargs='?')

    sell_parser = subparsers.add_parser('sell', help='Add a sold product')
    sell_parser.add_argument("-prod", help="enter a product to buy or sell", type=str, nargs='?')
    sell_parser.add_argument("-amount", help="used with buy|sell options", type=int, nargs='?')
    sell_parser.add_argument("-price", help="used with buy|sell options", type=int, nargs='?')

    report_parser = subparsers.add_parser('report', help='Produce a report')
    report_parser.add_argument("-inventory", help="show inventory (used with report option)", nargs='?')
    report_parser.add_argument("-revenue", help="report revenue (used with report option)", nargs='?')
    report_parser.add_argument("-profit", help="report profit (used with report option)", nargs='?')

    args = parser.parse_args()

    if args.command == 'buy':
        buy_csv_writer(buy_csv, args.prod, stoday, args.amount, args.price, args.exp)

    if args.command == 'sell':
        sell_csv_writer(sell_csv, args.prod, stoday, args.amount, args.price)

    if args.command == 'report':
        if args.inventory:
            get_inventory(buy_csv, sell_csv)
        elif args.revenue:
            pass
        # etc etc

    if args.command == 'date':
        pass

    # group1 = parser.add_mutually_exclusive_group()
    # group2 = parser.add_mutually_exclusive_group()
    # group3 = parser.add_mutually_exclusive_group()
    # group1.add_argument("command", help="requires -prod, -amount, -price and -exp", nargs='?')
    # #group1.add_argument("buy", help="requires -prod and -exp", nargs='?')
    # #group1.add_argument("sell", help="requires -prod and -exp", nargs='?')
    # #group1.add_argument("report", help="print report of revenue or profit", nargs='?')
    # parser.add_argument("-prod", help="enter a product to buy or sell", type=str, nargs='?')
    # parser.add_argument("-amount", help="used with buy|sell options", type=int, nargs='?')
    # parser.add_argument("-price", help="used with buy|sell options", type=int, nargs='?')
    # parser.add_argument("-exp", help="used with buy|sell options", nargs='?') # , type=date fails ??
    # group2.add_argument("-inventory", help="show inventory (used with report option)", nargs='?')
    # group2.add_argument("-revenue", help="report revenue (used with report option)", nargs='?')
    # group2.add_argument("-profit", help="report profit (used with report option)", nargs='?')
    # group3.add_argument("-set-date", help="set different date for processing", type=int)
    # group3.add_argument("-yesterday", help="show yesterday's inventory|revenue|profit")
    # group3.add_argument("-now", help="show current inventory|revenue|profit")
    # args = parser.parse_args()

#def Reporting():

def Product():
    def __init__(self, prod_name, price, exp_date):
        self.name = prod_name
        self.price = price
        self.exp_date = exp_date

def get_inventory(buy_csv, sell_csv):
    bought_list = []
    sold_list = []

    # Add all rows from buy_csv to a bought_list
    with open(buy_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            bought_list.append(row)

    # Add all rows from sell_csv to a sold_list
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)

    # Calculate total sold per item and add to sold_totals dict
    sold_totals = {}
    bought_totals = {}
    total_amnt = 0
    for item in sold_list:
        prod = item['Product']
        amnt = item['Amount']
        if len(sold_totals) == 0:
            sold_totals[prod] = int(amnt)
        elif prod not in sold_totals:
            sold_totals[prod] = int(amnt)
        else:
            total_amnt = int(amnt) + int(sold_totals[prod])
            sold_totals[prod] = total_amnt

    # Calculate total bought per item and add to bought_totals dict
    for item in bought_list:
        prod = item['Product']
        amnt = item['Amount']
        if len(bought_totals) == 0:
            bought_totals[prod] = int(amnt)
        elif prod not in bought_totals:
            bought_totals[prod] = int(amnt)
        else:
            total_amnt = int(amnt) + int(bought_totals[prod])
            bought_totals[prod] = total_amnt   

    # Subtract bought_total and sold_total
    inventory_list = {key: bought_totals[key] - sold_totals.get(key, 0) for key in bought_totals}
    print(inventory_list)
    return inventory_list


# def SetDate():
#     pass


## CSV Writer to write a product to any csv file
#inventory_csv = os.path.join(sys.path[0], 'inventory.csv')
buy_csv = os.path.join(sys.path[0], 'bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')


def buy_csv_writer(buy_csv_file, prod, buy_date, amnt, price, exp):
    ## If file doesn't exist, create it with the correct headers
    if not os.path.exists(buy_csv_file):
        file = Path(buy_csv_file)
        file.touch()
        # Write header
        headerlist = ['ID', 'Product', 'Buy_Date', 'Amount', 'Buy_Price', 'Exp_Date']
        with open(buy_csv_file, 'w', newline='') as open_csv:
            head = csv.DictWriter(open_csv, delimiter=',', fieldnames = headerlist)
            head.writeheader()

    # Check last used ID
    with open(buy_csv_file, newline='') as open_csv:
        rowreader = csv.DictReader(open_csv)
        last_used_ID = 0
        for row in rowreader:
            last_used_ID = row['ID']

    # Add product as row to csv
    with open (buy_csv_file, 'a', newline='') as open_csv:
        writer = csv.writer(open_csv)
        new_row = [int(last_used_ID)+1, prod, buy_date, amnt, price, exp]
        writer.writerow(new_row)
        # input("Seems to get to this point")


def sell_csv_writer(sell_csv_file, prod, sell_date, amnt, price):
    # If file doesn't exist, create it with the correct headers
    if not os.path.exists(sell_csv_file):
        file = Path(sell_csv_file)
        file.touch()
        # Write header
        headerlist = ['ID', 'Product', 'Sell_Date', 'Amount', 'Sell_Price', 'Bought_ID']
        with open(sell_csv_file, 'w', newline='') as open_csv:
            head = csv.DictWriter(open_csv, delimiter=',', fieldnames = headerlist)
            head.writeheader()

    # Check last used ID
    with open(sell_csv_file, newline='') as open_csv:
        rowreader = csv.DictReader(open_csv)
        last_used_ID = 0
        for row in rowreader:
            last_used_ID = row['ID']

    # Check availability
    ## FIX : If amnt > row['Amount] only the latest oldest_prod_buy_ID is given !!!
    with open(sell_csv, newline='') as sell_check:
        rowreader = csv.DictReader(sell_check)
        total_sold = 0
        for row in rowreader:
            if row['Product'] == prod:
                total_sold = total_sold + int(row['Amount'])
    with open(buy_csv, newline='') as buy_check:
        rowreader = csv.DictReader(buy_check)
        total_bought = 0
        total_required = total_sold + amnt
        oldest_prod_buy_ID = '1'
        temp_amount = amnt
        row_diff = 0
        new_last_used_ID = 0
        for row in rowreader:
            if row['Product'] == prod:
                total_bought = total_bought + int(row['Amount'])
                if temp_amount > int(row['Amount']):
                    row_diff = temp_amount - int(row['Amount'])
                    with open (sell_csv_file, 'a', newline='') as open_csv:
                        writer = csv.writer(open_csv)
                        new_row = [int(last_used_ID)+1, prod, sell_date, int(row['Amount']), price, oldest_prod_buy_ID]
                        writer.writerow(new_row)
                        new_last_used_ID = int(last_used_ID)+1
                        temp_amount = row_diff
                        continue
                elif total_bought < total_required:
                    #oldest_prod_buy_ID = int(oldest_prod_buy_ID)+1
                    continue
                elif total_bought >= total_required:
                    oldest_prod_buy_ID = row['ID']
                    break
            else:
                continue

    available_prod = total_bought - total_sold
    if amnt <= available_prod:
        # Add product as row to csv
        with open (sell_csv_file, 'a', newline='') as open_csv:
            writer = csv.writer(open_csv)
            new_row = [int(new_last_used_ID)+1, prod, sell_date, temp_amount, price, oldest_prod_buy_ID]
            writer.writerow(new_row)
    else:
        print(f'Not enough {prod} in inventory')

#csv = sell_csv_writer(sell_csv, 'banana', stoday, 3 , 12)
#csv = buy_csv_writer(buy_csv, 'banana', stoday, 2 , 12, stoday)
#print(get_inventory(buy_csv, sell_csv))


if __name__ == "__main__":
    main()

