from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIUrlsSettings(BaseModel):
    """API public urls settings."""

    docs: str = "/docs"
    redd: str = "/redoc"


class PublicApiSettings(BaseModel):
    """Configure public API service settings."""

    name: str = "CHANGE_ME"
    urls: APIUrlsSettings = APIUrlsSettings()


class DatabaseSettings(BaseModel):
    name: str = "db.sqlite3"

    @property
    def url(self) -> str:
        # return f"sqlite+aiosqlite:///./{self.name}"
        return f"mysql+aiomysql://root:admin123@localhost:3306/demo?charset=utf8mb4"


class LoggingSettings(BaseModel):
    """Configure the logging engine."""

    # The time field can be formatted using more human-friendly tokens.
    # These constitute a subset of the one used by the Pendulum library
    # https://pendulum.eustace.io/docs/#tokens
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <5} | {message}"

    # The .log filename
    file: str = "CHANGE_ME"

    # The .log file Rotation
    rotation: str = "10MB"

    # The type of compression
    compression: str = "zip"


class AccessTokenSettings(BaseModel):
    secret_key: str = (
        "4ce959cfa398058e1f24e27171fe04bf57d5752671b448a99887ab6b916c07b2"
    )
    ttl: int = 1  # hours


class RefreshTokenSettings(BaseModel):
    secret_key: str = (
        "152c65ad34b10b7cf65e81fa2580b27c15535e41bdc985b2a51caeca183caadf"
    )
    ttl: int = 14  # days


class AuthenticationSettings(BaseModel):
    access_token: AccessTokenSettings = AccessTokenSettings()
    refresh_token: RefreshTokenSettings = RefreshTokenSettings()
    algorithm: str = "HS256"
    scheme: str = "Bearer"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    # Infrastructure settings
    database: DatabaseSettings = DatabaseSettings()

    # Application configuration
    root_dir: Path
    src_dir: Path
    debug: bool = True
    public_api: PublicApiSettings = PublicApiSettings()
    logging: LoggingSettings = LoggingSettings()
    authentication: AuthenticationSettings = AuthenticationSettings()


# Define the root path
# --------------------------------------
ROOT_PATH = Path(__file__).parent.parent.parent.parent.parent

# ======================================
# Load settings
# ======================================
settings = Settings(
    # NOTE: We would like to hard-code the root and applications directories
    #       to avoid overriding via environment variables
    root_dir=ROOT_PATH,
    src_dir=ROOT_PATH / "src",
)
