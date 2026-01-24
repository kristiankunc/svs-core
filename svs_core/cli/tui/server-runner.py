if __name__ == "__main__":
    from svs_core.cli.tui.server import SVSServer

    server = SVSServer("python svs_core/cli/tui/web.py")
    server.serve()
