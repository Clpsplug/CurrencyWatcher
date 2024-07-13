from app import App

app = App()

if __name__ == '__main__':
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # Don't return failure upon Ctrl-C
        exit(0)
