class Config:
    app_name: str = "Messages"
    debug: bool = True
    database_url: str

class DevConfig(Config):
    database_url: str = "sqlite:///./messages/database.db"

class TestConfig(Config):
    database_url: str = "sqlite:///:memory:"

configs = {
    "development": DevConfig(),
    "testing": TestConfig()
}
