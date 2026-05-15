from supabase import create_client, Client
from app.core.config import settings

# For generic queries from the backend
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# For admin operations that need to bypass RLS
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
