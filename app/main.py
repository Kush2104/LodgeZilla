from fastapi import FastAPI
from fastapi.openapi.models import Info
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
import uvicorn

app = FastAPI(
    title="Lodgezilla API",
    description="API for Lodgezilla Property Management",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
)

# Include your API routers here
# Example: from app.api import property

from api import properties

# Include the routers in your app
app.include_router(properties.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
