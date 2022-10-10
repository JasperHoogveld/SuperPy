### Superpy will take input from the commandline/terminal as below.

***

## Positional arguments buy|sell|report|adv_date are required and sent to args.command

<u>Required options for 'buy' are </u>:
- -prod (to enter the product name)
- -amount (to enter the amount of bought products)
- -price (to enter the price as a float per item)
- -exp (to enter the expiration date)

<u>Required options for 'sell' are </u>:
- -prod (to enter the product name)
- -amount (to enter the amount of bought products)
- -price (to enter the price as a float per item)

<u>Required options for 'report' are </u>:
- inventory (to show current inventory)
- revenue -period <*yyyy, yyyy-mm or yyyy-mm-dd*> (show revenue over entered period)
- profit -period <*yyyy, yyyy-mm or yyyy-mm-dd*> (show profit over entered period)

<u>Required options for 'adv_date' are </u>:
- time_delta -num_days <*int*> (to advance the current time that will be used for processing)
- reset (to reset the date in date.txt to datetime.now() and it will remove all lines from the bought and sold csv files\
    with a bought or sold date higher than today)

<br>

For 'buy' the program will write the data to bought.csv with an ID that will be used for linking it to a sell of that product.<br>
For 'sell' the program will write the data to sold.csv (using the get_inventory to check if the product is in stock) with the Bought_ID so it can be linked later in the processing of the profit.<br>
When using the 'report' options it will either print the output in a Rich table (inventory and profit) or show it in a messagebox (revenue).<br>
When setting the 'adv_date' to use a date in the future (for test cases/simulation) it will write that date to the date.txt file which is used by the get_date() function.<br>
After using the 'adv_date reset' option it will write back the current date to the date.txt file and remove all lines, that have a buy or sell date in the future, from the csv files.<br>
<br>

## Examples

    python.exe superpy.py buy -prod apple -amount 20 -price 1.75 -exp 2022-12-23
    python.exe superpy.py buy -prod banana -amount 20 -price 1.45 -exp 2022-12-12
    python.exe superpy.py sell -prod apple -amount 10 -price 2.35
    python.exe superpy.py report inventory
                            Inventory
    ┏━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ ID ┃ Product ┃ Amount ┃ Buy_Price ┃ Buy_Date   ┃ Exp_Date   ┃
    ┡━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ 1  │ apple   │ 10     │ 1.75      │ 2022-10-03 │ 2022-12-23 │
    │ 2  │ banana  │ 20     │ 1.45      │ 2022-10-03 │ 2022-12-12 │
    └────┴─────────┴────────┴───────────┴────────────┴────────────┘
    python .\superpy.py adv_date time_delta -num_days 50
    python.exe superpy.py buy -prod banana -amount 20 -price 3.45 -exp 2022-12-12
    python.exe .\superpy.py report inventory
                               Inventory
    ┏━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ ID ┃ Product ┃ Amount ┃ Buy_Price ┃ Buy_Date   ┃ Exp_Date   ┃
    ┡━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ 1  │ apple   │ 10     │ 1.75      │ 2022-10-03 │ 2022-12-23 │
    │ 2  │ banana  │ 20     │ 1.45      │ 2022-10-03 │ 2022-12-12 │
    │ 3  │ banana  │ 20     │ 3.45      │ 2022-11-22 │ 2022-12-12 │
    └────┴─────────┴────────┴───────────┴────────────┴────────────┘
    python.exe .\superpy.py report profit -period 2022-10
    Profit over 2022-10
    ┏━━━━━━━━━┳━━━━━━━━┓
    ┃ Product ┃ Profit ┃
    ┡━━━━━━━━━╇━━━━━━━━┩
    │ apple   │ 6.0    │
    └─────────┴────────┘