import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:////home/mkz/Documents/PiDrop/db/pidrop.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    UPLOAD_ROOT = os.environ.get("UPLOAD_ROOT", "/home/mkz/Documents/PiDrop/data")

    ALLOWED_EXTENSIONS = {

        "documents": {
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".txt", ".md", ".csv", ".odt", ".ods", ".odp", ".rtf"
        },
        "portfolio": {
            ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".md", ".csv",
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp4", ".mov", ".webm",
            ".zip", ".7z", ".tar", ".gz", ".rar", ".zip"
        },
        "media": {
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic",
            ".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a"
        },
        "samples": {
            ".zip", ".7z", ".tar", ".gz",
            ".js", ".py", ".sh", ".ps1", ".bat", ".cmd",
            ".exe", ".dll", ".bin", ".apk", ".jar",
            ".html", ".hta", ".vbs", ".psm1", ".iso", ".rar" 
        }
    }