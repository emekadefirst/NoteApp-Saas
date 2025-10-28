from src.apps.organization.routes import organization_router
from src.apps.user.routes import user_router
from src.apps.note.routes import note_router
from src.apps.admin.routes import admin_router

routes = [
   organization_router,
   user_router,
   note_router,
   admin_router
]