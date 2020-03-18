import Bank
import Admin
import Client

#Verificam functionalitatea pentru Bank

#b = Bank.Bank("")
#print(b.getTotalAmountOfMoney())
#mydb = Bank.Bank.createConnection()
#print(b.passwordExistInDatabase(mydb,'illes_password','admins')) nu merge :(
#b.createClientAccount('Mihai', '1234', 10090000)
#print(b.getClient('Dragan', '1235').__str__())
#print(b.getAdmin("Illes","illes_password").__str__())


#Verificam functionalitatea pentru admin

#a = Admin.Admin('Stoian', '1234', b)
#a.createAdminAccount('Dragan', 'dragan')
#print(a.getAllClientsAsString())
#a.addMoneyForBank(2000000)
#a.deleteClient('Dragan', '1235')
#a.deleteClient('Dragomir','1235')


#Verificam functionalitatea pentru client

#c  = Client.Client('Dragan','1235', b, 1000, 10)
#c.depositMoney(3500)
#c.withdrawMoney(150)
#c.getCreditFromBank(8000)
#print(c.payDebt(3000))
#print(c.getUserName())
#print(c.getPassword())
#print(c.getDepositedMoney())
#print(c.getMoneyBorrowed())




