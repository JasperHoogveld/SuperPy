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
from rich import print as rprint

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.

today = datetime.now()
stoday = today.strftime("%Y-%m-%d")
smonth = today.strftime("%Y-%m")
adv_date = today

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

    date_parser = subparsers.add_parser('adv_date', help="type a number of days you want to check inventory in the future or reset that date")
    date_parser.add_argument('-mode', choices=['time_delta', 'reset'])
    date_parser.add_argument('num_days', nargs=1, type=int)

    args = parser.parse_args()

    if args.command == 'buy':
        buy_csv_writer(buy_csv, args.prod, args.amount, args.price, args.exp)

    if args.command == 'sell':
        sell_csv_writer(sell_csv, args.prod, args.amount, args.price)

    if args.command == 'report':
        if args.mode == 'inventory':
            get_inventory(buy_csv, sell_csv)
        elif args.mode == 'revenue':
            get_revenue(args.spec_date)
        elif args.mode == 'profit':
            get_profit(args.spec_date)  

    if args.command == 'adv_date':
        if args.mode == 'time_delta':
            advance_date(args.num_days)
        elif args.mode == 'reset':
            reset_date()


# Files locations
buy_csv = os.path.join(sys.path[0], 'bought.csv')
temp_buy_csv = os.path.join(sys.path[0], 'temp_bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')
temp_sell_csv = os.path.join(sys.path[0], 'temp_sold.csv')
advanced_date = os.path.join(sys.path[0], 'date.txt')

class Product():
    def __init__(self, prod_name, price, exp_date):
        self.name = prod_name
        self.price = price
        self.exp_date = exp_date

def advance_date(num_days):
    # Create txt file with advanced date in YYYY-MM-DD
    #adv_delta = int(adv_delta)
    print(type(num_days))
    adv_date = datetime.strftime(today + timedelta(days=num_days), '%Y-%m-%d')
    #advanced_date = os.path.join(sys.path[0], 'date.txt')
    if not os.path.exists(advanced_date):
        file = Path(advanced_date)
        file.touch()
    with open(advanced_date, 'w') as file:
        file.write(adv_date)

    # Return a date with the requested delta
    return print(f' Date for processing set to {adv_date}')

def reset_date():
    # Delete avanced date file
    if exists(advanced_date):
        os.remove(advanced_date)
    
    # Write only the rows on or before today to temp file
    with open(buy_csv, 'r') as inp, open(temp_buy_csv, 'w', newline='') as outp:
        rowreader = csv.DictReader(inp)
        headerlist = ['ID', 'Product', 'Buy_Date', 'Amount', 'Buy_Price', 'Exp_Date']
        writer = csv.DictWriter(outp, delimiter=',', fieldnames = headerlist)
        writer.writeheader()
        for row in rowreader:
            buy_date = datetime.strptime(row['Buy_Date'], '%Y-%m-%d')
            if buy_date <= today:
                writer.writerow(row)
    
    # Write only the rows on or before today to temp file
    with open(sell_csv, 'r') as inp, open(temp_sell_csv, 'w', newline='') as outp:
        rowreader = csv.DictReader(inp)
        headerlist = ['ID', 'Product', 'Sell_Date', 'Amount', 'Sell_Price', 'Bought_ID']
        writer = csv.DictWriter(outp, delimiter=',', fieldnames = headerlist)
        writer.writeheader()
        for row in rowreader:
            sell_date = datetime.strptime(row['Sell_Date'], '%Y-%m-%d')
            if sell_date <= today:
                writer.writerow(row)

    # Copy temp files over originals and remove temp files
    shutil.copyfile(temp_buy_csv, buy_csv)
    shutil.copyfile(temp_sell_csv, sell_csv)
    os.remove(temp_buy_csv)
    os.remove(temp_sell_csv)
    

def get_inventory(buy_csv, sell_csv):
    bought_list = []
    sold_list = []

    # Read advanced date if set
    if exists(advanced_date):
        with open(advanced_date, 'r') as f:
            adv_date = f.readline()
        adv_date = datetime.strptime(adv_date, '%Y-%m-%d')
    else:
        adv_date = today
    # Add all rows from buy_csv to a bought_list
    with open(buy_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            row['in_inv'] = row['Amount']
            exp_date = datetime.strptime(row['Exp_Date'], '%Y-%m-%d')
            if exp_date > adv_date:
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
    for item in sold_list:
        sold_prod = item['Product']
        sold_amnt = int(item['Amount'])
        bought_ID = item['Bought_ID']
        for item in bought_list:
            if sold_prod == item['Product'] and bought_ID == item['ID']:
                in_inv = int(item['in_inv'])
                if in_inv == 0:
                    continue
                elif in_inv > sold_amnt:
                    item['in_inv'] = in_inv - sold_amnt
                    break
                else:
                    item['in_inv'] = 0
                    break
            else:
                continue
    
    return bought_list

    #return pprint.pprint(bought_list, sort_dicts=False)
    # Also gives back a None???

def get_revenue(spec_date):
    # Add all sales to a list
    sold_list = []
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)

    # Check if Day, Month or Year and add totals of sales prices for that period
    total_revenue = 0
    for item in sold_list:
        sell_price = item['Sell_Price']
        if item['Sell_Date'].startswith(spec_date):
            total_revenue = total_revenue + float(sell_price)

    return print(f'The total revenue for {spec_date} is {total_revenue} euros')


def get_profit(spec_date):
    # Add all sold and bought items from csv to lists with dicts
    sold_list = []
    bought_list = []
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)
    
    with open(buy_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            bought_list.append(row)

    # Add total sold for that period
    total_sold = 0
    for item in sold_list:
        sell_price = item['Sell_Price']
        if item['Sell_Date'].startswith(spec_date):
            total_sold = total_sold + int(sell_price) 

    # Add total bought for that period
    total_bought = 0
    for item in bought_list:
        buy_price = item['Buy_Price']
        if item['Buy_Date'].startswith(spec_date):
            total_bought = total_bought + int(buy_price)
    
    total_profit = float(total_sold) - float(total_bought)

    return print(f'The total profit for {spec_date} is {total_profit} euros')    

# CSV Files locations
buy_csv = os.path.join(sys.path[0], 'bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')

# CSV Writer to write a product to bought.csv file
def buy_csv_writer(buy_csv_file, prod, amnt, price, exp):
    # Read advanced date if set
    if exists(advanced_date):
        with open(advanced_date, 'r') as f:
            adv_date = f.readline()
    else:
        adv_date = stoday

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
        new_row = [int(last_used_ID)+1, prod, adv_date, amnt, price, exp]
        writer.writerow(new_row)

# CSV Writer to write a product to sold.csv file
def sell_csv_writer(sell_csv_file, prod, amnt, price):
    # Read advanced date if set
    if exists(advanced_date):
        with open(advanced_date, 'r') as f:
            adv_date = f.readline()
    else:
        adv_date = stoday

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
                    new_row = [int(last_used_ID)+1, prod, adv_date, int(key['in_inv']), price, key['ID']]
                    writer.writerow(new_row)
                    last_used_ID = int(last_used_ID)+1
                    prod_available = True
                    amnt = amnt - int(key['in_inv'])
                continue
            elif amnt <= int(key['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, adv_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                break
            else:
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, adv_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                break
        else:
            continue

    # Doesn't seemn to work 100% <--- CHECK
    if amnt != 0 or prod_available == False:
        print(f'There were {amnt} {prod}s too few in inventory')


#csv = sell_csv_writer(sell_csv, 'banana', 3 , 14)
#csv = buy_csv_writer(buy_csv, 'banana', 2 , 12, '2022-12-13')
#print(get_inventory(buy_csv, sell_csv))
print(advance_date(60))
#print(reset_date())
#print(get_revenue())
#print(get_profit('2022'))

if __name__ == "__main__":
    main()

