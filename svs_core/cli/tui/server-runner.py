if __name__ == "__main__":
    from textual_serve.server import Server

    server = Server("python svs_core/cli/tui/web.py")
    server.serve()
