# Currency watcher

A simple currency rate watcher widget on your desktop
written with Python and Tkinter.

Powered by [GMO Coin Public API](https://api.coin.z.com/fxdocs/en/#outline)

## How to run

1. Install Python (3.12 or later) and tcl-tk using method of your choice.
2. Install poetry.
   ```console
   $ pip install poetry
   ```
3. Create the poetry environment:
   ```console
   $ poetry install
   ```
4. And just run it (by default, it shows the USD-JPY rate.)
   ```console
   $ poetry run python main.py
   ```
   This app only uses public API, so you don't need to have an account to run it.

## LICENSE

MIT
