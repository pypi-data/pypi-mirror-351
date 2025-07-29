from fastapi.middleware.gzip import GZipMiddleware


def add_compression_middleware(app):
    app.add_middleware(GZipMiddleware, minimum_size=1000)
