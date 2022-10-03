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
import matplotlib.pyplot as plt
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from tkinter import messagebox, simpledialog


# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.

today = datetime.now()
stoday = today.strftime("%Y-%m-%d")

# Files locations
buy_csv = os.path.join(sys.path[0], 'bought.csv')
temp_buy_csv = os.path.join(sys.path[0], 'temp_bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')
temp_sell_csv = os.path.join(sys.path[0], 'temp_sold.csv')
date_file = os.path.join(sys.path[0], 'date.txt')

###########
########### Stil need to fix get_profit and the arguments in report Revenue/profit ##
###########

def main():
    parser = argparse.ArgumentParser(prog="Inventory Manager",
                                    description="Program to edit/check store Inventory",
                                    epilog="I hope this is clear enough")
    subparsers = parser.add_subparsers(dest='command')

    buy_parser = subparsers.add_parser('buy', help='Add a bought product')
    buy_parser.add_argument("-prod", help="Enter a product to buy or sell", type=str)
    buy_parser.add_argument("-amount", help="Amount of items", type=int)
    buy_parser.add_argument("-price", help="Price per item", type=float)
    buy_parser.add_argument("-exp", help="Expiration date")

    sell_parser = subparsers.add_parser('sell', help='Add a sold product')
    sell_parser.add_argument("-prod", help="Enter a product to buy or sell", type=str)
    sell_parser.add_argument("-amount", help="Amount of items", type=int)
    sell_parser.add_argument("-price", help="Price per item", type=float)

    report_parser = subparsers.add_parser('report', help='Report Inventory or Revenue/Profit over a time period')
    report_parser.add_argument('mode', choices=['inventory', 'revenue', 'profit'])
    report_parser.add_argument('-period', type=str)

    date_parser = subparsers.add_parser('adv_date', help="Type a number of days you want to test in the future or reset to today")
    date_parser.add_argument('mode', choices=['time_delta', 'reset'])
    date_parser.add_argument('-num_days', type=int)

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

def get_date():
    if not os.path.exists(date_file):
        file = Path(date_file)
        file.touch()
        with open(date_file, 'w') as file:
            file.write(stoday) 
        set_date = stoday  
    else:
        with open(date_file, 'r') as f:
            set_date = f.readline()

    return set_date

def advance_date(num_days):
    # Create txt file with advanced date in YYYY-MM-DD
    #adv_delta = int(adv_delta)
    adv_date = datetime.strftime(today + timedelta(days=int(num_days)), '%Y-%m-%d')
    #advanced_date = os.path.join(sys.path[0], 'date.txt')
    if not os.path.exists(date_file):
        file = Path(date_file)
        file.touch()
    with open(date_file, 'w') as file:
        file.write(adv_date)

    # Return a date with the requested delta
    print(messagebox.showinfo(None, f'Date for processing set to {adv_date}'))

def reset_date():
    # Delete avanced date file
    with open(date_file, 'w') as file:
        file.write(stoday) 
    
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
    # Read advanced date if set
    if exists(date_file):
        with open(date_file, 'r') as f:
            adv_date = f.readline()
        adv_date = datetime.strptime(adv_date, '%Y-%m-%d')
    else:
        adv_date = today


    # Add all rows from buy_csv to a bought_list
    bought_list = []    
    with open(buy_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            row['in_inv'] = row['Amount']
            #exp_date = datetime.strptime(row['Exp_Date'], '%Y-%m-%d')
            if datetime.strptime(row['Exp_Date'], '%Y-%m-%d') > datetime.strptime(get_date(), '%Y-%m-%d'):
                row['is_expired'] = 0
            else:
                row['is_expired'] = 1
            bought_list.append(row)


    # Add all rows from sell_csv to a sold_list
    sold_list = []
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

def display_inventory():
    # Create a table with columns
    inv_table = Table(title="Inventory")
    inv_table.add_column("ID", no_wrap=True, style="red")
    inv_table.add_column("Product", no_wrap=True, style="green")
    inv_table.add_column("Amount", no_wrap=True, style="yellow")
    inv_table.add_column("Buy_Price", no_wrap=True, style="yellow")
    inv_table.add_column("Buy_Date", no_wrap=True, style="cyan")
    inv_table.add_column("Exp_Date", no_wrap=True, style="cyan")

    # Check what's in inventory that's not expired and print the table
    for item in get_inventory(buy_csv, sell_csv):
        if item['in_inv'] != 0 and item['is_expired']!=1:
            inv_table.add_row(item['ID'], item['Product'], str(item['in_inv']), item['Buy_Price'], item['Buy_Date'], item['Exp_Date'])
    console = Console()
    print('')
    console.print(inv_table)

def get_revenue(period):
    # Add all sales to a list
    sold_list = []
    with open(sell_csv, 'r', newline='') as open_csv:
        in_file = csv.DictReader(open_csv)
        for row in in_file:
            sold_list.append(row)

    # Check if Day, Month or Year and add totals of sales prices for that period
    total_revenue = 0
    for item in sold_list:
        sell_price = float(item['Sell_Price'])
        sell_quant = float(item['Amount'])
        if item['Sell_Date'].startswith(str(period)):
            total_revenue = total_revenue + (sell_price*sell_quant)

    print(messagebox.showinfo(None, f'The total revenue for {period} is {total_revenue} euros'))

def get_profit(period):
#### Change to check BoughtIDs

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

    # Add sold items for that period into new list
    new_sold_list = []
    for item in sold_list:
        if item['Sell_Date'].startswith(str(period)):
            new_key = dict()
            new_key['Product'] = item['Product']
            sold_price_total = float(item['Sell_Price']) * float(item['Amount'])
            for item2 in bought_list:
                if item2['ID'] == item['Bought_ID']:
                    bought_price_total = float(item['Amount']) * float(item2['Buy_Price'])
                    new_key['Profit'] = sold_price_total - bought_price_total
                    new_sold_list.append(new_key)
                    break    
    
    # Calculate profits and add to profit_list
    profit_list = []
    for new_product in new_sold_list:
        product_is_known = False
        for product in profit_list:
            if new_product["Product"] == product["Product"]:
                product_is_known = True
                product["Profit"] += new_product["Profit"]
        if not product_is_known:
            profit_list.append(new_product)
        product_is_known = False
    
    # Create a table with columns
    prof_table = Table(title="Profit")
    prof_table.add_column("Product", no_wrap=True, style="green")
    prof_table.add_column("Profit", no_wrap=True, style="yellow")

    # Print the table
    for item in profit_list:
        prof_table.add_row(item['Product'], str(item['Profit']))
    console = Console()
    print(f'Period: {period}')
    console.print(prof_table)                    

def buy_csv_writer(buy_csv_file, prod, amnt, price, exp):
    ## CSV Writer to write a product to bought.csv file
    # Read advanced date if set
    set_date = get_date()

    # If file doesn't exist, create it with the correct headers
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
        new_row = [int(last_used_ID)+1, prod, set_date, amnt, price, exp]
        writer.writerow(new_row)

def sell_csv_writer(sell_csv_file, prod, amnt, price):
    ## CSV Writer to write a product to sold.csv file
    # Read advanced date if set
    set_date = get_date()

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
                    new_row = [int(last_used_ID)+1, prod, set_date, int(key['in_inv']), price, key['ID']]
                    writer.writerow(new_row)
                    last_used_ID = int(last_used_ID)+1
                    prod_available = True
                    amnt = amnt - int(key['in_inv'])
                continue
            elif amnt <= int(key['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, set_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                    amnt = 0
                break
            else:
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, set_date, amnt, price, key['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                    amnt = 0
                break
        else:
            continue

    if amnt != 0 or prod_available == False:
        print(f'There were {amnt} {prod}s too few in inventory')


#csv = sell_csv_writer(sell_csv, 'banana', 10 , 3.25)
#csv = buy_csv_writer(buy_csv, 'banana', 2 , 12, '2022-12-13')
#print(get_inventory(buy_csv, sell_csv))
#print(display_inventory())
#print(advance_date(60))
#print(reset_date())
#print(get_revenue(2022))
#print(get_profit('2022'))

if __name__ == "__main__":
    main()

