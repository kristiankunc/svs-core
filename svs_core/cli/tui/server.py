from aiohttp import web
from textual_serve.server import Server


class SVSServer(Server):  # noqa D101
    async def _make_app(self) -> web.Application:  # noqa D102
        app = await super()._make_app()

        ADDITIONAL_ROUTES = [
            web.get("/auth", self.handle_auth),
        ]
        app.add_routes(ADDITIONAL_ROUTES)
        return app

    async def handle_auth(self, request: web.Request) -> web.Response:  # noqa D102
        if request.method == "GET":
            return web.Response(text="Authentication Page")

        # post request -> process form data
        elif request.method == "POST":
            data = await request.post()
            username = data.get("username")
            password = data.get("password")

            def _to_str(val: object) -> str:
                if val is None:
                    return ""
                if isinstance(val, (bytes, bytearray)):
                    return val.decode("utf-8", errors="replace")
                return str(val)

            username = _to_str(username)
            password = _to_str(password)

            return web.Response(text=f"Authenticated user: {username}")

        return web.Response(status=405)
