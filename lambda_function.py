import lamvery
import os


def lambda_handler(event, context):
    lamvery.env.load()
#    print(lamvery.secret.get('foo'))
    print(os.environ)
    print(context)
