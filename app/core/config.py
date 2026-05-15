from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hunkx API"
    # Database Settings
    DATABASE_URL: str = ""
    
    # Razorpay Settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    
    # Resend Email Settings
    RESEND_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "allow" # This allows other variables in .env without crashing

settings = Settings()
