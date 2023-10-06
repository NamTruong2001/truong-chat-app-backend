from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, user_router, messenger_router, file_router
from dependencies import sio
import socketio
import uvicorn


fastapi_app = FastAPI()
fastapi_app.include_router(auth_router)
fastapi_app.include_router(user_router)
fastapi_app.include_router(messenger_router, prefix="/message")
fastapi_app.include_router(file_router, prefix="/file")

app = socketio.ASGIApp(sio, fastapi_app)


fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.on_event("shutdown")
def shutdown_event():
    print("shut down server")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
