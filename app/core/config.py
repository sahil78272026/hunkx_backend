from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hunkx API"
    # Database Settings
    DATABASE_URL: str = ""
    
    # Razorpay Settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    # Resend Email Settings
    RESEND_API_KEY: str = ""

    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    class Config:
        env_file = ".env"
        extra = "allow" # This allows other variables in .env without crashing

settings = Settings()
