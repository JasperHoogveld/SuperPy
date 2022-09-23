# Imports
from asyncio.proactor_events import _ProactorBasePipeTransport
from genericpath import exists
import sys
import argparse
import csv
from datetime import date, datetime, timedelta
from typing import Optional
import os.path
import shutil
from pathlib import Path
import pprint
import traceback

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
    report_parser.add_argument("-mode", choices=['inventory', 'revenue', 'profit'])
    # report_parser.add_argument("-inventory", help="show inventory (used with report option)", nargs='?')
    # report_parser.add_argument("-revenue", help="report revenue (used with report option)", nargs='?')
    # report_parser.add_argument("-profit", help="report profit (used with report option)", nargs='?')

    args = parser.parse_args()

    if args.command == 'buy':
        buy_csv_writer(buy_csv, args.prod, stoday, args.amount, args.price, args.exp)

    if args.command == 'sell':
        sell_csv_writer(sell_csv, args.prod, stoday, args.amount, args.price)

    if args.command == 'report':
        if args.mode == 'inventory':
            get_inventory(buy_csv, sell_csv)
        elif args.mode == 'revenue':
            get_revenue(args.spec_date)
        elif args.mode == 'profit':
            get_profit(args.spec_date)      


class Product():
    def __init__(self, prod_name, price, exp_date):
        self.name = prod_name
        self.price = price
        self.exp_date = exp_date


def advance_time(adv_time):
    # Create txt file with current dat in YYYY-MM-DD
    current_date = os.path.join(sys.path[0], 'date.txt')
    if not os.path.exists(current_date):
        file = Path(current_date)
        file.touch()
    with open(current_date, 'w') as file:
        file.write(stoday)

    # Return a date with the requested delta
    req_time = datetime.strftime(today + timedelta(days=adv_time), '%Y-%m-%d')
    return req_time


def get_inventory(buy_csv, sell_csv):
    bought_list = []
    sold_list = []

    # Add all rows from buy_csv to a bought_list
    with open(buy_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            row['in_inv'] = row['Amount']
            exp_date = datetime.strptime(row['Exp_Date'], '%Y-%m-%d')
            if exp_date > today:
                row['is_expired'] = 0
            else:
                row['is_expired'] = 1
            bought_list.append(row)

    # Add all rows from sell_csv to a sold_list
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)

    # Subtract all sold amounts from 'in_inv' column in bought_list
    for key in sold_list:
        sold_prod = key['Product']
        sold_amnt = int(key['Amount'])
        bought_ID = key['Bought_ID']
        for buy_key in bought_list:
            a = buy_key['Product']
            if sold_prod == buy_key['Product'] and bought_ID == buy_key['ID']:
                in_inv = int(buy_key['in_inv'])
                if in_inv == 0:
                    continue
                elif in_inv > sold_amnt:
                    buy_key['in_inv'] = in_inv - sold_amnt
                    break
                else:
                    buy_key['in_inv'] = 0
                    break
            else:
                continue

    return bought_list

## Build in a totals system to counter selling the last stack when sell_amnt is greater ???

def totals_system():
    # Calculate total sold per item and add to sold_totals dict
    sold_totals = dict()
    bought_totals = dict()
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
    inv_totals = dict()
    for key in bought_totals:
        inv_totals[key] = bought_totals[key] - sold_totals.get(key, 0)
    pass

def get_revenue(spec_date):
    # Add all sales to a list
    sold_list = []
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)

    # Check if Day, Month or Year and add totals of sales prices for that period per sold item
    timespan = len(spec_date)
    for key in sold_list:
        total_revenue = 0
        sell_price = key['Sell_Price']
        sell_date = key['Sell_Date'][:timespan:]
        if spec_date == sell_date:
            total_revenue = total_revenue + int(sell_price)

    return (f'The total revenue for {spec_date} is {total_revenue} euros')

def get_profit():
    pass

# CSV Files locations
buy_csv = os.path.join(sys.path[0], 'bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')

# CSV Writer to write a product to bought.csv file
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

# CSV Writer to write a product to sold.csv file
def sell_csv_writer(sell_csv_file, prod, sell_date, amnt, price):
    # If file doesn't exist, create it with the correct headers
    if not os.path.exists(sell_csv_file):
        file = Path(sell_csv_file)
        file.touch()
        # Write header to csv file
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

    # Check availability from get_inventory() and write to sold_csv
    prod_available = False
    for key in get_inventory(buy_csv, sell_csv):
        if prod == key['Product']:
            if key['in_inv'] == 0:
                continue
            elif key['is_expired'] == 1:
                continue
            elif amnt > int(key['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, sell_date, int(key['in_inv']), price, key['ID']]
                    writer.writerow(new_row)
                    last_used_ID = int(last_used_ID)+1
                    prod_available = True
                    amnt = amnt - int(key['in_inv'])
                continue
            elif amnt <= int(key['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, sell_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                break
            else:
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, sell_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                break
        else:
            continue

    # 'amnt != 0' is quite redundant here
    if amnt != 0 or prod_available == False:
        print(f'There were {amnt} {prod}s too few in inventory')


#csv = sell_csv_writer(sell_csv, 'banana', stoday, 3 , 12)
#csv = buy_csv_writer(buy_csv, 'banana', stoday, 2 , 12, stoday)
#print(get_inventory(buy_csv, sell_csv))
#print(advance_time(current_date, 2))
#print(revenue('2022-09-22'))

if __name__ == "__main__":
    main()

