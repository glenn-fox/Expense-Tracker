import sqlite3
import pandas as pd
import csv

DATABASE = "budget_db"

def get_transactions():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = """SELECT s.split_id, description, t.transaction_date, t.amount, tt.transaction_type_name, c.category_name FROM
    transaction_split AS s
    LEFT JOIN transactions AS t
    ON s.transaction_id = t.transaction_id
    LEFT JOIN transaction_type as tt
    ON t.transaction_type_id = tt.transaction_type_id
    LEFT JOIN categories as c
    ON s.category_id = c.category_id
    ORDER BY t.transaction_date
    """

    df = pd.read_sql_query(query, connection)
    connection.close()
    return df

def get_monthly_category_summary():
    connection = sqlite3.connect(DATABASE)

    query = """SELECT strftime('%Y-%m', t.transaction_date) AS year_month, c.category_id, c.category_name, SUM(ts.amount) AS total FROM
        categories AS c
        LEFT JOIN transaction_split AS ts
        ON c.category_id = ts.category_id
        LEFT JOIN transactions as t
        ON ts.transaction_id = t.transaction_id
        WHERE c.is_visable = 'True'
        GROUP BY c.category_id, c.category_name, year_month
        ORDER BY year_month
        """

    df = pd.read_sql_query(query, connection)
    connection.close()
    return df


def month_summary():
    connection = sqlite3.connect(DATABASE)

    query = """SELECT strftime('%Y-%m', t.transaction_date) AS year_month,tt.transaction_type_name, sum(t.amount) AS amount FROM
    transaction_split AS s
    LEFT JOIN transactions AS t
    ON s.transaction_id = t.transaction_id
    LEFT JOIN transaction_type as tt
    ON t.transaction_type_id = tt.transaction_type_id
    LEFT JOIN categories as c
    ON s.category_id = c.category_id
    WHERE c.is_visable = 'True'
	GROUP BY year_month, tt.transaction_type_name
    ORDER BY year_month, tt.transaction_type_name desc
    """

    df = pd.read_sql_query(query, connection)
    connection.close()
    return df


def get_categories():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = "SELECT * FROM categories ORDER BY category_name ASC"
    
    return pd.read_sql_query(query, connection)

def get_accounts():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = "SELECT * FROM accounts"

    return pd.read_sql_query(query, connection)

def add_category(category_name, parent_category, is_visable):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories WHERE category_name = ?", (category_name,))
    
    #print(cursor.fetchone())
    try:
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO categories (category_name, parent_category_id, is_visable) VALUES (?, ?, ?)", (category_name, parent_category, is_visable,))
            connection.commit()
            connection.close()
            return "Added Category Successfully"
        else:
            return "Category already in database"
    except Exception as e:
        return e

    
def update_categories(change_list):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    result = ""

    query = """
            UPDATE transaction_split
            SET category_id = ?
            WHERE split_id = ?
        """
    try:

        cursor.executemany(query, change_list)

        connection.commit()

        result = f"Successfully updated {cursor.rowcount} rows!"

    except sqlite3.Error as e:
        result = f"A database error occured: {e}"
        connection.rollback()
    
    finally:
        connection.close()
        return result

def categorize_transactions(db):
    user_in = ""
    results = []

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("Select * From categories")
    categories = cursor.fetchall()

    query = """SELECT s.split_id, s.transaction_id, t.description, s.amount, s.category_id 
        FROM transaction_split AS s 
        LEFT JOIN transactions AS t 
        ON s.transaction_id = t.transaction_id WHERE s.category_id IS NULL
        AND t.description LIKE ?
        ORDER BY t.transaction_date ASC"""
    
    while True:
        user_in = input("What would you like to search for?: ")
        user_in = "%" + user_in + "%"

        cursor.execute(query, (user_in,))

        results = cursor.fetchall()
    
        for result in results:
            print(result)
        if input("Do you want to update the category on these transactions? y/N ").upper() == "Y":
            break


    for category in categories:
        print(category)

    user_in = int(input("please select a category id to assign to the transactions: "))


    ids = []
    for i in results:
        ids.append((user_in, i[0]))
    

        
    #print(ids)

    query = """Update transaction_split SET category_id = ? WHERE split_id = ?"""
    #query = f"SELECT * FROM transaction_split WHERE split_id IN {ids}"
    cursor.executemany(query, ids)
    connection.commit()
    #print(query)
    connection.close()


def sync_transactions():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    query = "SELECT t.transaction_id, t.amount FROM transactions AS t LEFT JOIN transaction_split AS s ON t.transaction_id = s.transaction_id WHERE s.split_id IS NULL"
    cursor.execute(query)
    transactions = cursor.fetchall()

    cursor.executemany("INSERT into transaction_split (transaction_id, amount) VALUES (?, ?)", transactions)

    connection.commit()
    connection.close()


def import_file_to_db(df, account_id):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()
    #cursor.execute("SELECT * FROM accounts")

    #accounts = cursor.fetchall()
    
    #print("Select an option:")

    #for account in accounts:
    #    print(f"{account[0]}: {account[1]}")
    #account_id = int(input("Your Choice: "))

    #df = pd.read_csv(file, skiprows = 1)

    df.columns = [col.strip() for col in df.columns]
    df["Amount"] = df["Amount"] .str.replace(",", "").astype(float)
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%Y').dt.date


    data = []
    for index, row in df.iterrows():
        transaction_type_id = 0
        if (row["Amount"] < 0 and account_id == 1) or (row["Amount"] > 0 and account_id == 2): #account_id 1 == checking
            transaction_type_id = 2 # transaction_type_id 2 == expense, 1 == income
        else:
            transaction_type_id = 1
        
        data.append((row['Date'].strftime('%Y-%m-%d'), row['Description'], abs(row['Amount']), transaction_type_id, account_id))

    #for line in data:
    #    print(line)

    cursor.executemany("INSERT into transactions (transaction_date, description, amount, transaction_type_id, account_id) VALUES (?, ?, ?, ?, ?)", data)
    connection.commit()

    connection.close()


def menu():
    choice = ""
    database = "budget_db"

    while choice.upper() != "Q":

        print("choose option:")
        print("1: view categories")
        print("2: categorize transactions")
        choice = input("your choice: ")


        if choice == "1":
            get_categories(database)
        if choice == "2":
            categorize_transactions(database)
        if choice == "3":
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            df = pd.read_sql_query("Select * FROM transactions", connection)

            print(df)



if __name__ == "__main__":
    print("hello")
    database = "budget_db"
    
    sync_transactions(database)
    
    #get_categories(database)
    #categorize_transactions(database)
    

    menu()


    #import_file_to_db(file, database)

    #print(df)

    # data = []
    # for i, row in df.iterrows():
    #     transaction_type = 0
    #     if row['Amount'] < 0:
    #         transaction_type= 1
    #     else:
    #         transaction_type = 2
    #     data.append((row['Date'].strftime('%Y-%m-%d'), row['Description'], abs(row['Amount']), transaction_type))
    # for j in data:
    #     print(j)
    #
    #
    # connection.commit()

