from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base, SessionLocal
from app.database.seed import seed_database
from app.api.routes import products, suppliers, orders, scenarios, agent

app = FastAPI(title="AI Purchasing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(orders.router)
app.include_router(scenarios.router)
app.include_router(agent.router)

@app.get("/")
def root():
    return {"message": "AI Purchasing Agent Backend API Running"}
