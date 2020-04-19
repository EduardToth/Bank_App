from backend.Bank import Bank

db_connection = Bank.createConnection()

my_cursor = db_connection.cursor()

my_cursor.execute("UPDATE Clients SET postal_code = %s, phone_number = %s, nationality = %s, email = %s, monthly_income = %s WHERE True",
                  ('3030046', '0752164477', 'Romanian', 'my_bankAccount@gmail.com', 2000))
db_connection.commit()
print( my_cursor.rowcount )