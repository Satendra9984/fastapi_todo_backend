
from database import engine
from fastapi import FastAPI
from routes import todos, auth
import models

app = FastAPI()

# this will create the databases required
models.Base.metadata.create_all(bind=engine)


app.include_router(todos.router)
app.include_router(auth.router)

@app.get("/")
async def homeroute():
    return {"case": "home"}

