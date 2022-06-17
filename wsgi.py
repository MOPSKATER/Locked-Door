from main import app


def run(ssl=True):
    if ssl:
        app.run(ssl_context=('fullchain.pem', 'privkey.pem'))
    else:
        app.run()


if __name__ == "__main__":
    run()
