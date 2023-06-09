[![PyPI](https://img.shields.io/pypi/v/pymojang)](https://pypi.org/project/pymojang/)
[![CI](https://github.com/Lucino772/proxyctx/actions/workflows/ci.yml/badge.svg)](https://github.com/Lucino772/proxyctx/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Lucino772/proxyctx/main.svg)](https://results.pre-commit.ci/latest/github/Lucino772/proxyctx/main)
[![codecov](https://codecov.io/gh/Lucino772/proxyctx/branch/main/graph/badge.svg?token=U4O9F1K0R4)](https://codecov.io/gh/Lucino772/proxyctx)
![PyPI - Downloads](https://img.shields.io/pypi/dm/proxyctx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/proxyctx)

# proxyctx
**ProxyCTX** is a handy utility library that empowers developers to establish a global context accessible from anywhere within their application. Its creation was inspired by [Flask](https://flask.palletsprojects.com/en/latest/), a popular web framework. Under the hood, **ProxyCTX** leverages the Python standard module [contextvars](https://docs.python.org/3/library/contextvars.html).

The library consists of just two key components:
- `Proxy`: Inspired by Werkzeug's **LocalProxy** class ([werkzeug.local](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/local.py))
- `Context`: Inspired by Flask's **AppContext** class ([flask.ctx](https://github.com/pallets/flask/blob/main/src/flask/ctx.py))

## Flask Example

In Flask, when defining a route, the corresponding method does not receive any parameters representing the incoming request. Instead, you can import a global variable called `request`, which conveniently holds information about the incoming request. Here's an example code snippet illustrating this:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    print(request.method)
```

It's worth noting that `request` is not the only global variable available in Flask. You can explore the [flask.globals](https://github.com/pallets/flask/blob/main/src/flask/globals.py) module, which encompasses all the global variables provided by Flask.

## Usage

To install the library use the following command:

```bash
pip install proxyctx
```

### Proxy

```python
from contextvars import ContextVar
from proxyctx import Proxy

class Greet:
    def __init__(self, message: str = None):
        self.message = message

    def greet(self, name: str):
        if self.message is None:
            print(f"Hello {name} !")
        else:
            print(f"Hello {name}, {self.message}")

ctx: ContextVar["Greet"] = ContextVar("ctx")
current_greet: "Greet" = Proxy(ctx)
current_message: str = Proxy(ctx, lambda obj: obj.message)

ctx.set(Greet("how are you ?"))
print(current_message) # "how are you ?"
current_greet.greet("Lucino772") # "Hello Lucino772, how are you ?"

ctx.set(Greet("have a nice day !"))
print(current_message) # "have a nice day !"
current_greet.greet("Lucino772") # "Hello Lucino772, have a nice day !"
```

## Context

```python
from contextvars import ContextVar
from proxyctx import Proxy, Context

ctx: ContextVar["GreetContext"] = ContextVar("ctx")
current_greet: "Greet" = Proxy(ctx, lambda obj: obj.greet)

class Greet:
    def __init__(self, message: str = None):
        self.message = message

    def greet(self, name: str):
        if self.message is None:
            print(f"Hello {name} !")
        else:
            print(f"Hello {name}, {self.message}")

    def greet_context(self):
        return GreetContext(self)

class GreetContext(Context):
    def __init__(self, greet: "Greet"):
        super().__init__(ctx)
        self.greet = greet

with Greet("how are you ?").greet_context():
    current_greet.greet("Lucino772") # "Hello Lucino772, how are you ?"
    with Greet("have a nice day !").greet_context():
        current_greet.greet("Lucino772") # "Hello Lucino772, have a nice day !"
    current_greet.greet("Lucino772") # "Hello Lucino772, how are you ?"
```

## Licence
This project uses a
**MIT** Licence [view](https://github.com/Lucino772/proxyctx/blob/main/LICENSE)