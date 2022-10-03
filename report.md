## <u>Highlighted technical element #1</u>: 
The double use of the function get_inventory(). The get_inventory() is used both in the sell_csv_writer() function to make sure an item is in stock when writing to the csv file and will display a message if not enough of a product is in stock. It is also used in the display_inventory() <br>

    for item in get_inventory(buy_csv, sell_csv):

## <u>Highlighted technical element #2</u>: 
The use of writing the Bought_ID from the bought.csv file to be written in each line of the sold products so a future field such as "batch" could be implemented so a faulty batch can be located. <br>
This Bought_ID is also used in the get_profit() function to make sure the profit is calculated over the correct price an item was bought for.<br>

    ID,Product,Sell_Date,Amount,Sell_Price,Bought_ID  (header from sold.csv)

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

## <u>Highlighted technical element #3</u>:
The used of Rich.console to print a coloured table for the get_inventory() and get_profit() functions <br>

                               Inventory 
    ┏━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ ID ┃ Product ┃ Amount ┃ Buy_Price ┃ Buy_Date   ┃ Exp_Date   ┃
    ┡━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ 1  │ apple   │ 10     │ 1.75      │ 2022-10-03 │ 2022-12-23 │
    │ 2  │ banana  │ 20     │ 1.45      │ 2022-10-03 │ 2022-12-12 │
    │ 3  │ banana  │ 20     │ 3.45      │ 2022-11-22 │ 2022-12-12 │
    └────┴─────────┴────────┴───────────┴────────────┴────────────┘

      Profit over 2022
    ┏━━━━━━━━━┳━━━━━━━━┓
    ┃ Product ┃ Profit ┃
    ┡━━━━━━━━━╇━━━━━━━━┩
    │ apple   │ 6.0    │
    │ banana  │ 12.5   │
    └─────────┴────────┘

## <u>Highlighted technical element #4</u>:
The use of the tkinter.messagebox to display a pop up window when using the get_revenue() or advance_date() functions <br>
I did not want to make all of the input a tkinter.dialoguebox since the project was supposed to be a command-line tool<br>

