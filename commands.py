# Imports
from genericpath import exists
import sys
import csv
import os.path
from datetime import datetime, timedelta
import shutil
from rich.table import Table
from rich.console import Console
from tkinter import messagebox
from pathlib import Path
from rich import print as rprint

## Set some date variables
today = datetime.now()
stoday = today.strftime("%Y-%m-%d")

## File locations
date_file = os.path.join(sys.path[0], 'date.txt')
temp_buy_csv = os.path.join(sys.path[0], 'temp_bought.csv')
temp_sell_csv = os.path.join(sys.path[0], 'temp_sold.csv')
buy_csv = os.path.join(sys.path[0], 'bought.csv')
# If buy_csv file doesn't exist, create it with the correct headers
if not os.path.exists(buy_csv):
    file = Path(buy_csv)
    file.touch()
    # Write header
    headerlist = ['ID', 'Product', 'Buy_Date', 'Amount', 'Buy_Price', 'Exp_Date']
    with open(buy_csv, 'w', newline='') as open_csv:
        head = csv.DictWriter(open_csv, delimiter=',', fieldnames = headerlist)
        head.writeheader()

sell_csv = os.path.join(sys.path[0], 'sold.csv')
# If sell_csv file doesn't exist, create it with the correct headers
if not os.path.exists(sell_csv):
    file = Path(sell_csv)
    file.touch()
    # Write header to csv file
    headerlist = ['ID', 'Product', 'Sell_Date', 'Amount', 'Sell_Price', 'Bought_ID']
    with open(sell_csv, 'w', newline='') as open_csv:
        head = csv.DictWriter(open_csv, delimiter=',', fieldnames = headerlist)
        head.writeheader()


def get_date():
    # Create a date.txt file if it doesn't exist and write today's date into it
    if not os.path.exists(date_file):
        file = Path(date_file)
        file.touch()
        with open(date_file, 'w') as file:
            file.write(stoday) 
        set_date = stoday  
    # Or read the advanced date that was set with the advance_date() function
    else:
        with open(date_file, 'r') as f:
            set_date = f.readline()
    return set_date

def advance_date(num_days):
    # Create txt file with advanced date in YYYY-MM-DD
    adv_date = datetime.strftime(today + timedelta(days=int(num_days)), '%Y-%m-%d')
    if not os.path.exists(date_file):
        file = Path(date_file)
        file.touch()
    with open(date_file, 'w') as file:
        file.write(adv_date)

    # Print a date with the requested delta
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

    rprint(f'The processing date has been set back to {stoday} and all future lines have been removed from the csv files')

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
    prof_table = Table(title=f"Profit over {period}")
    prof_table.add_column("Product", no_wrap=True, style="green")
    prof_table.add_column("Profit", no_wrap=True, style="yellow")

    # Print the table
    for item in profit_list:
        prof_table.add_row(item['Product'], str(item['Profit']))
    console = Console()
    print('')
    console.print(prof_table)                    

def buy_csv_writer(buy_csv_file, prod, amnt, price, exp):
    ## CSV Writer to write a product to bought.csv file
    # Read advanced date if set
    set_date = get_date()

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

    # Check last used ID
    with open(sell_csv_file, newline='') as open_csv:
        rowreader = csv.DictReader(open_csv)
        last_used_ID = 0
        for row in rowreader:
            last_used_ID = row['ID']

    # Check availability from get_inventory() and write to sold_csv
    prod_available = False
    for item in get_inventory(buy_csv, sell_csv):
        if prod == item['Product']:
            if item['in_inv'] == 0:
                continue
            elif item['is_expired'] == 1:
                continue
            elif amnt > int(item['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, set_date, int(item['in_inv']), price, item['ID']]
                    writer.writerow(new_row)
                    last_used_ID = int(last_used_ID)+1
                    prod_available = True
                    amnt = amnt - int(item['in_inv'])
                continue
            elif amnt <= int(item['in_inv']):
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, set_date, amnt, price, item['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                    amnt = 0
                break
            else:
                with open (sell_csv_file, 'a', newline='') as open_csv:
                    writer = csv.writer(open_csv)
                    new_row = [int(last_used_ID)+1, prod, set_date, amnt, price, item['ID']]
                    writer.writerow(new_row)
                    prod_available = True
                    amnt = 0
                break
        else:
            continue

    if amnt != 0 or prod_available == False:
        print(f'There were {amnt} {prod}s too few in inventory')