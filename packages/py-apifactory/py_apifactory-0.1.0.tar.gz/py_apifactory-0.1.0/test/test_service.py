from uvicorn import run

from apifactory import Service

app = Service()

if __name__ == '__main__':
    run(app)
