# example

from KB_Bank_Transaction_Lookup import get_transactions

transaction_list = get_transactions(
        bank_num='74670101827583',
        birthday='900101',
        password='0000',
        # days=30 # Optional: default is 30
    )

for trs in transaction_list:
    print(trs['date'], trs['amount'], trs['transaction_by'])

