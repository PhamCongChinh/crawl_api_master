from fastapi import FastAPI
import uvicorn
from src.core.config import settings
from src.api import router_post, router_checkhealth

app = FastAPI()

app.include_router(router_post)
app.include_router(router_checkhealth)

def main():
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=False, access_log=False)

if __name__ == "__main__":
    main()

@app.get("/")
async def root():
    return {"message": "Hello World"}