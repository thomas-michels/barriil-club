from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/signin",
    scopes={
        "user:me": "Read information about the current user.",
        "user:get": "Read information about users.",
        "user:update": "Update information about users.",
        "user:delete": "Delete information about users.",
        "product:create": "Create new products.",
        "product:get": "Read information about products.",
        "product:update": "Update information about products.",
        "product:delete": "Delete information about products.",
        "order:create": "Create new orders.",
        "order:get": "Read information about orders.",
        "order:update": "Update information about orders.",
        "order:delete": "Delete information about orders.",
    },
)
