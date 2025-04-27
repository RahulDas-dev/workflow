from pydantic_settings import SettingsConfigDict

from .database_conf import DatabaseConfig
from .deployment_conf import DeploymentConfig
from .feature import FeatureConfig
from .log_conf import LoggingConfig
from .uploads_conf import UploadConfig


class AppConfig(DeploymentConfig, LoggingConfig, DatabaseConfig, FeatureConfig, UploadConfig):
    model_config = SettingsConfigDict(env_file=".config", env_file_encoding="utf-8", extra="ignore")
