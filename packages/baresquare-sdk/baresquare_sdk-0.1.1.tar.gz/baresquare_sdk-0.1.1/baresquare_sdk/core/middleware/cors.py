from fastapi.middleware.cors import CORSMiddleware


# Very permissive settings, review before you enable this middleware
def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=86400,
    )
