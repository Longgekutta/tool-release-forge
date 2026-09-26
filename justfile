default:
    @python main.py health

setup:
    @python main.py setup

test:
    @python main.py test

health:
    @python main.py health

clean:
    @python main.py clean

forge target="." tag="v0.1.0":
    @python main.py forge --target {{target}} --tag {{tag}}

notes target="." tag="v0.1.0":
    @python main.py notes --target {{target}} --tag {{tag}}
