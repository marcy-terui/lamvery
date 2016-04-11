import lamvery
import os


def lambda_handler(event, context):
    lamvery.env.load()
    print(os.environ)
    print(context)

    return event
