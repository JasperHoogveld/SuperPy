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
strfdate = today.strftime("%Y-%m-%d")
strfmonth = today.strftime("%Y-%m")



def main():
    parser = argparse.ArgumentParser(prog="Inventastic", 
                                    description="Program to edit/check store Inventory",
                                    epilog="I hope this is clear enough")
    group1 = parser.add_mutually_exclusive_group()
    group2 = parser.add_mutually_exclusive_group()
    group3 = parser.add_mutually_exclusive_group()
    group1.add_argument("buy", help="requires -prod and -exp", nargs='?')
    group1.add_argument("sell", help="requires -prod and -exp", nargs='?')
    group1.add_argument("report", help="print report of revenue or profit", nargs='?')
    parser.add_argument("-prod", help="enter a product to buy or sell", type=str, nargs='?')
    parser.add_argument("-price", help="used with buy|sell options", type=int, nargs='?')
    parser.add_argument("-exp", help="used with buy|sell options", nargs='?') # , type=date fails ??
    group2.add_argument("-inventory", help="show inventory (used with report option)", nargs='?')
    group2.add_argument("-revenue", help="report revenue (used with report option)", nargs='?')
    group2.add_argument("-profit", help="report profit (used with report option)", nargs='?')
    parser.add_argument("-set-time", help="set different date for processing", type=int)
    group3.add_argument("-yesterday", help="show yesterday's inventory|revenue|profit")
    group3.add_argument("-now", help="show current inventory|revenue|profit")
    args = parser.parse_args()    

    if args.buy == 'buy':
        csv_writer(buy_csv, args.prod, args.price, args.exp)
        
    if args.sell == 'sell':
        csv_writer(sell_csv, args.prod, args.price, args.exp)


# def BuySell():
#     def __init__(self, id, prod_name, price, exp_date):
#         self.id = id
#         self.name = prod_name
#         self.price = price
#         self.exp_date = exp_date
#         pass

#     def buy(BuySell):

#         pass

#     def sell(BuySell):
#         pass


# def Reporting():
#     pass


# def SetDate():
#     pass


## CSV Writer to write a product to any csv file
buy_csv = os.path.join(sys.path[0], 'bought.csv')
sell_csv = os.path.join(sys.path[0], 'sold.csv')

def csv_writer(csv_file, prod, price, exp):
    ## If file doesn't exist, create it with the correct headers
    if not os.path.exists(csv_file):
        file = Path(csv_file)
        file.touch()
        # Write header
        headerlist = ['ID', 'Product', 'BuyPrice', 'Exp-Date']
        with open (csv_file, 'w', newline='') as open_csv:
            head = csv.DictWriter(open_csv, delimiter=',', fieldnames = headerlist)
            head.writeheader()
            
    # Check last used ID
    with open (csv_file, 'r', newline='') as open_csv:
        # Read one line.The first line is the header, so discard the result
        open_csv.readline()
        # Check what last used ID is
        lines = open_csv.readlines()
        if lines:
            last_used_ID = lines[-1].rsplit(',')[0]
        else:
            last_used_ID = 0

    # Add product as row to csv
    with open (csv_file, 'a', newline='') as open_csv:
        writer = csv.writer(open_csv)
        new_row = [int(last_used_ID)+1, prod, price, exp]
        writer.writerow(new_row)
        # input("Seems to get to this point")
    return csv_file

# csv = csv_writer(sell_csv, 'banana', 12, strfdate)


if __name__ == "__main__":
    main()
