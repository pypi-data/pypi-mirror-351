from ..token.currency import Currency
from ..token.transaction import Transaction
from ..roles.user import User

# executed = False
def migration():
    solt = Currency.resource.read(name='Solt')
    if not solt:
        solt = Currency(name='Solt', \
                        aliases=['соль','соли', 'соли', 'соль', 'солью', 'соль']).save()
        solt = Currency.resource.read(name='Solt')
    solt = solt[0]

    honey = Currency.resource.read(name='Honey')
    if not honey:
        honey = Currency(name='Honey', \
                        aliases=['медок','медка', 'медку', 'медок', 'медком', 'медке']).save()
        honey = Currency.resource.read(name='Honey')
    honey = honey[0]
    honey.aliases=['медок','медка', 'медку', 'медок', 'медком', 'медке']
    honey.save()

    marat = User.resource.read(telegram_id=7790094619)
    if not marat:
        marat = User()
        marat.first_name = 'marat'
        marat.last_name = 'marat'
        marat.telegram_id = 7790094619
        marat.username = 'taalc_bot'
        marat.save()
        marat = User.resource.read(telegram_id=7790094619)
    marat = marat[0]

    test_transaction = Transaction.resource.read()

    if not test_transaction:        
        me = User.resource.read(first_name = 'Никита', last_name = 'Сексова')[0]
        tr = Transaction(marat, me, solt, 10000)
        tr.save()