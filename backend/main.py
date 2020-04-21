# import datetime
#
#
# from dateutil.relativedelta import relativedelta
#
# from backend import Bank
#
# database_connection = None
# try :
#     today = datetime.date.today()
#     database_connection = Bank.Bank.createConnection ( )
#     my_cursor = database_connection.cursor ( )
#     my_cursor.execute (
#         "INSERT INTO Admins   (name, password,"
#         " id, is_logged,"
#         " email)"
#         "VALUES (%s, %s, %s, %s, %s)" ,
#         ('Vitomir Dragan',
#          '4ed9407630eb1000c0f6b63842defa7d',
#          2 ,
#          0,
#          'vitomir_dragan86@yahoo.com'
#          ) )
#
#     database_connection.commit ( )
#     database_connection.close ( )
# except BaseException as exception :
#     print ( str ( exception ) )
#     database_connection.close ( )
#     raise Exception ( "Something went wrong. Please try again later" )
#
#
# # INSERT INTO `admins` (`name`, `password`, `id`, `email`, `is_logged`) VALUES
# # ('Illes', '56fba4f663e9a9262c890968bf8a72c8', 1, '	 eduardtoth98@gmail.com', 1),
# # ('Vitomir Dragan', '4ed9407630eb1000c0f6b63842defa7d', 2, 'vitomir_dragan86@yahoo.com', 0)


def f() :
    return 1 , 2


(x , y) = f ( )

print ( y )
