from fastapi import FastAPI
from .config import configs
from .database import Database
from .api.routes import router

def create_app(config_name: str):
    config = configs[config_name]
    app = FastAPI(title=config.app_name, debug=config.debug)

    # Initializing the database for the first time.
    db = Database(config.database_url)

    @app.on_event("startup")
    def startup_event():
        db.create_db_and_tables()

    @app.on_event("shutdown")
    def shutdown_event():
        db.drop_all_tables()
    
    app.include_router(router)

    return app
