import time
import tkinter as tk
from typing import Optional

from gmo import GMOStatus, GMOCurrency


class TooEarlyError(Exception):
    pass


class IsOnMaintenanceError(Exception):
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
        self.label = tk.Label(self, text="Drag me around!", font=("Helvetica", 16))
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
                raise IsOnMaintenanceError()

            currency_response = GMOCurrency().call()
            if currency_response.status != 0:
                raise CurrencyAPIFailureError()

            usd_jpy = list(filter(lambda d: d.symbol == "USD_JPY", currency_response.data))[0]

            self.label.config(text=(
                f"USD-JPY: {usd_jpy.bid} - {usd_jpy.ask}\n"
                f"Last updated at: {currency_response.get_readable_time()}"
            ))

            print(
                f"[{currency_response.get_response_time()}] USD-JPY: {usd_jpy.bid} - {usd_jpy.ask}"
            )
            self.next_update_interval = 100
        except TooEarlyError:
            self.next_update_interval = 100
        except StatusAPIFailureError:
            self.label.config(text="API is failing! Will try again after an hour.")
            self.next_update_interval = 1000 * 60 * 60
        except IsOnMaintenanceError:
            self.label.config(text="On maintenance - cannot get data, will try again after 30 min.")
            self.next_update_interval = 1000 * 60 * 30
        except CurrencyAPIFailureError:
            self.label.config(text="Currency API is failing! Will try again after 5 min.")
            self.next_update_interval = 1000 * 60 * 5
        except Exception as e:
            self.label.config(text=f"Unexpected API error! Will try again after a minute.\n Exception: {e}")
            self.next_update_interval = 1000 * 60
        finally:
            self.after(self.next_update_interval, self.update_task)
