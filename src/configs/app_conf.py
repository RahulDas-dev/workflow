from pydantic_settings import SettingsConfigDict

from .database_conf import DatabaseConfig
from .deployment_conf import DeploymentConfig
from .feature import FeatureConfig
from .log_conf import LoggingConfig


class InvoiceInferConfig(DeploymentConfig, LoggingConfig, DatabaseConfig, FeatureConfig):
    model_config = SettingsConfigDict(env_file=".config", env_file_encoding="utf-8", extra="ignore")
