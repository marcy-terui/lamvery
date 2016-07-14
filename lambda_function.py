import lamvery
import os


def lambda_handler(event, context):
    lamvery.env.load()
    print(os.environ)
    print(context)
    print(lamvery.secret.get('foo'))
    print(open(lamvery.secret.file('bar.txt'), 'r').read())
    return event
