import lamvery


def lambda_handler(event, context):
    print(lamvery.secret.get('foo'))
    print(event)
    print(context)
