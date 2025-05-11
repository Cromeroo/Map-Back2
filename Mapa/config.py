import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  
    MYSQL_DB = "bomqaeinqjipko184nen"
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_PORT = os.getenv("MYSQL_PORT")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10
    }
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecreto")
