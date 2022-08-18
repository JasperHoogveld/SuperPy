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
    group1 = parser.add_mutually_exclusive_group()
    group2 = parser.add_mutually_exclusive_group()
    group3 = parser.add_mutually_exclusive_group()
    group1.add_argument("command", help="requires -prod and -exp", nargs='?')
    #group1.add_argument("sell", help="requires -prod and -exp", nargs='?')
    #group1.add_argument("report", help="print report of revenue or profit", nargs='?') 
    parser.add_argument("-prod", help="enter a product to buy or sell", type=str, nargs='?')
    parser.add_argument("-amount", help="used with buy|sell options", type=int, nargs='?')
    parser.add_argument("-price", help="used with buy|sell options", type=int, nargs='?')
    parser.add_argument("-exp", help="used with buy|sell options", nargs='?') # , type=date fails ??
    group2.add_argument("-inventory", help="show inventory (used with report option)", nargs='?')
    group2.add_argument("-revenue", help="report revenue (used with report option)", nargs='?')
    group2.add_argument("-profit", help="report profit (used with report option)", nargs='?')
    group3.add_argument("-set-date", help="set different date for processing", type=int)
    group3.add_argument("-yesterday", help="show yesterday's inventory|revenue|profit")
    group3.add_argument("-now", help="show current inventory|revenue|profit")
    args = parser.parse_args()    

    command = args.command

    if command == 'buy':
        buy_csv_writer(buy_csv, args.prod, stoday, args.amount, args.price, args.exp)
        
    if command == 'sell':
        sell_csv_writer(sell_csv, args.prod, stoday, args.amount, args.price)

    if command == 'report':
        pass


# def BuySell():
#     # def __init__(self, id, prod_name, price, exp_date):
#     #     self.id = id
#     #     self.name = prod_name
#     #     self.price = price
#     #     self.exp_date = exp_date
#     #     pass

#     def buy(prod, amount, price, exp):
#         csv_writer(buy_csv, prod, amount, price, exp)

#     def sell(BuySell):
#         pass


#def Reporting():
    
def inventory(buy_csv, sell_csv):
    # with open (buy_csv, 'r', newline='') as in_file:
    #     in_file.readline()
    #     in_lines = in_file.readlines()
    #     current_in = []
    #     current_out = []
    #     for row in in_lines:
    #         if row.rsplit(',')[4] <= strfdate:
    #             current_in.append(row)
    #     product = row.rsplit(',')[1]
            # total = 0
            # for product in row:
            #     total = in_lines.rsplit(',')[2] + total

    invent_list = []
    with open (buy_csv, 'r', newline='') as in_file:
        in_file.readline()
        in_lines = in_file.readlines()
    with open (sell_csv, 'r', newline='') as out_file:
        out_file.readline()
        out_lines = out_file.readlines()
    for row_in in in_lines:
        for row_out in out_lines:
            if row_in.rsplit(',')[1] == row_out.rsplit(',')[1]:
                sub = int(row_in.rsplit(',')[2]) - int(row_out.rsplit(',')[2])
                invent_list.append(sub)
    return invent_list

    # current_in = []
    # current_out = []
    # for line in in_lines:
    #     if line.rsplit(',')[4] <= strfdate:
    #         current_in.append(line)
    # for line in out_lines:
    #     if line.rsplit(',')[4] <= strfdate:
    #         current_out.append(line)

        



# def SetDate():
#     pass


## CSV Writer to write a product to any csv file
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
    with open(sell_csv, newline='') as sell_check:
        rowreader = csv.DictReader(sell_check)
        total_sold = 0
        for row in rowreader:
            total_sold = total_sold + int(row['Amount'])
    with open(buy_csv, newline='') as buy_check:
        rowreader = csv.DictReader(buy_check)
        total_bought = 0
        total_required_inventory = total_sold + amnt
        first_bought_ID = '1'
        for row in rowreader:
            if row['Product'] == prod:
                total_bought = total_bought + int(row['Amount'])
                if total_bought <= total_required_inventory:
                    first_bought_ID = row['ID']
                else:
                    first_bought_ID = int(first_bought_ID)+1
            else:
                continue

    available_prod = total_bought - total_sold
    if amnt <= available_prod:
        # Add product as row to csv
        with open (sell_csv_file, 'a', newline='') as open_csv:
            writer = csv.writer(open_csv)
            new_row = [int(last_used_ID)+1, sell_date, prod, amnt, price, first_bought_ID]
            writer.writerow(new_row)
    else:
        print(f'Not enough {prod} in inventory')

csv = sell_csv_writer(sell_csv, 'banana', stoday, 3 , 12)
#csv = buy_csv_writer(buy_csv, 'banana', stoday, 2 , 12, stoday)
#print(inventory(buy_csv, sell_csv))

if __name__ == "__main__":
    main()

