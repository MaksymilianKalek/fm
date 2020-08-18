import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "secret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
    S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
    S3_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_LOCATION = f"http://{S3_BUCKET}.s3.amazonaws.com/"
