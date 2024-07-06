from app import App

app = App()

if __name__ == '__main__':
    try:
        app.mainloop()
    except KeyboardInterrupt:
        exit(0)
