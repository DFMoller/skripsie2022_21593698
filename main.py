from venv import create
from website import create_app

app = create_app()

app.debug = True

if __name__ == "__main__":
    print('+++++ Starting app.run: +++++')
    app.run(host="0.0.0.0")