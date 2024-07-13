import time
import tkinter as tk
from typing import Optional

from gmo import GMOStatus, GMOCurrency, CurrencyData


class TooEarlyError(Exception):
    pass


class IsUnderMaintenanceError(Exception):
    pass


class MarketIsClosedError(Exception):
    pass


class StatusAPIFailureError(Exception):
    pass


class CurrencyAPIFailureError(Exception):
    pass


class App(tk.Tk):
    def __init__(self, master: Optional[tk.Widget] = None):
        super().__init__(master)
        self.master = master

        self.overrideredirect(True)  # Remove self decorations (border, title bar, etc.)
        self.geometry("300x200")

        # Add some content
        self.label = tk.Label(self, text="Getting currency data", font=("Helvetica", 16))
        self.label.pack(expand=True)

        # Bind mouse events to the self
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)

        self.x: int = 0
        self.y: int = 0
        self.last_update_at: float = 0
        self.next_update_interval: int = 5
        self.update_task()

    def start_drag(self, event: tk.Event) -> None:
        self.x = event.x
        self.y = event.y

    def on_drag(self, event: tk.Event) -> None:
        self.geometry(f'+{event.x_root - self.x}+{event.y_root - self.y}')

    def update_task(self) -> None:
        try:
            if self.last_update_at + 5 > time.time():
                raise TooEarlyError()

            self.last_update_at = time.time()

            response = GMOStatus().call()
            if response.status != 0:
                raise StatusAPIFailureError()

            if response.data.status == "MAINTENANCE":
                raise IsUnderMaintenanceError()

            currency_response = GMOCurrency().call()
            if currency_response.status != 0:
                raise CurrencyAPIFailureError()

            usd_jpy: CurrencyData = list(filter(lambda d: d.symbol == "USD_JPY", currency_response.data))[0]

            self.label.config(text=(
                f"USD-JPY: {usd_jpy.bid} - {usd_jpy.ask}\n"
                f"Last updated at: {currency_response.get_readable_time()}"
            ))

            print(
                f"[{currency_response.get_response_time()}] USD-JPY: {usd_jpy.bid} - {usd_jpy.ask}"
            )

            if usd_jpy.status == "CLOSE":
                raise MarketIsClosedError()
            self.next_update_interval = 100
        except TooEarlyError:
            self.next_update_interval = 100
        except StatusAPIFailureError:
            self.label.config(text="API is failing!\nWill try again after an hour.")
            self.next_update_interval = 1000 * 60 * 60
        except IsUnderMaintenanceError:
            self.label.config(text="Under maintenance - cannot get data.\nWill try again after 30 min.")
            self.next_update_interval = 1000 * 60 * 30
        except CurrencyAPIFailureError:
            self.label.config(text="Currency API is failing!\nWill try again after 5 min.")
            self.next_update_interval = 1000 * 60 * 5
        except MarketIsClosedError:
            print("Market is closed. Will run on a lower update frequency.")
            self.next_update_interval = 1000 * 60 * 60
        except Exception as e:
            self.label.config(text=f"Unexpected API error!\nWill try again after a minute.\n Exception: {e}")
            self.next_update_interval = 1000 * 60
        finally:
            self.after(self.next_update_interval, self.update_task)
