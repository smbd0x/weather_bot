from .start import start_router
from .user import user_router
from .admin import admin_router

routers = [start_router, user_router, admin_router]