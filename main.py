import os
import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=os.getenv('DB_PASSWORD'),
    database='bank_project'
)

cursor = db.cursor(buffered=True)
db.autocommit = True


def account():
    first_name = input("What is your first name?: ")
    last_name = input("What is your last name?: ")
    birth_date = input("When is your birthday (YYYY-MM-DD)?: ")
    email = input("Your email?: ")
    phone_number = input("Your phone number?: ")
    password = input("Create password: ")
    starting_balance = float(input("How much do you want to deposit?: "))
    account_type = 'Checking'
    branch_id = 1
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, date_of_birth, email, phone_number, passwd) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, birth_date, email, phone_number, password))
    customer_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO accounts (customer_id, branch_id, account_type, balance) 
        VALUES (%s, %s, %s, %s)
        """, (customer_id, branch_id, account_type, starting_balance))
    print("Account successfully made!")

def login():
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    input_password = input("Password: ")
    cursor.execute("SELECT customer_id, passwd FROM customers WHERE first_name = %s AND last_name = %s", (first_name, last_name))
    user_data = cursor.fetchone()
    if user_data and user_data[1] == input_password:
        print("Login successful!")
        operation(user_data[0])
    else:
        print("Login failed. Check your credentials.")
		
def operation(customer_id):
    while True:
        operation_decision = input("What would you like to do? (Deposit, Withdraw, Check balance, Settings, Exit): ")
        cursor.execute("SELECT account_number, balance FROM accounts WHERE customer_id = %s", (customer_id,))
        account_data = cursor.fetchone()
        if account_data is None:
            print("No account found.")
            return
        
        if operation_decision == 'Check balance':
            print("Your current balance is: $", account_data[1])
        elif operation_decision == "Deposit":
            get_deposit(account_data[0])
        elif operation_decision == "Withdraw":
            get_withdrawal(account_data[0])
        elif operation_decision == "Settings":
            settings(account_data[0])
        elif operation_decision.lower() == 'exit':
            break
        else:
            print("Invalid option, try again.")

def get_deposit(account_number):
    deposit_amount = float(input("How much would you like to deposit? "))
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", (deposit_amount, account_number))
    print("Deposit successful.")

def get_withdrawal(account_number):
    withdrawal_amount = float(input("How much would you like to withdraw? "))
    cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (account_number,))
    current_balance = cursor.fetchone()[0]
    if current_balance >= withdrawal_amount:
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", (withdrawal_amount, account_number))
        print("Withdrawal successful.")
    else:
        print("Insufficient funds.")

def settings(customer_id):
    while True:
        what_setting = input("Settings: Change name, Delete account, Exit: ").lower()
        if what_setting == "change name":
            new_first_name = input('New first name: ')
            new_last_name = input("New last name: ")
            cursor.execute("UPDATE customers SET first_name = %s, last_name = %s WHERE customer_id = %s",
                           (new_first_name, new_last_name, customer_id))
            print("Name updated!")
        elif what_setting == "delete account":
            cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            cursor.execute("DELETE FROM accounts WHERE customer_id = %s", (customer_id,))
            print("Account has been deleted!")
            break
        elif what_setting == "exit":
            break
        else:
            print("Invalid option, try again.")

def initialize_database():
    cursor.execute("""
        INSERT INTO branches (branch_id, branch_name, branch_address, branch_city, branch_state, branch_zip)
        VALUES (1, 'Main Branch', '123 Main St', 'Anytown', 'Anystate', '12345')
        ON DUPLICATE KEY UPDATE branch_name=VALUES(branch_name),
                                branch_address=VALUES(branch_address),
                                branch_city=VALUES(branch_city),
                                branch_state=VALUES(branch_state),
                                branch_zip=VALUES(branch_zip);
    """)
    db.commit()

initialize_database()

exit = 'N'
while exit != 'Y':
    print("Welcome to Hani Bank!")
    has_account = input("Do you have an account? (Y or N): ").upper()
    if has_account == 'Y':
        login()
    else:
        like_to_make_acc = input("Would you like to make an account? (Y or N): ").upper()
        if like_to_make_acc == 'Y':
            account()

    exit_prompt = input("Would you like to exit? (Y or N): ").upper()
    if exit_prompt == 'Y':
        exit = 'Y'

print("Please Come back Soon!")
