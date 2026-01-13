from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Database
from app.database import engine, Base

# Routers
from app.routes import sentiment, insight, stock_routes, ai_routes, market_routes, history_routes

# -------------------------------------------------
# 1️⃣ CREATE FASTAPI APP
# -------------------------------------------------
app = FastAPI(title="Stock Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory - pointing to app/static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve index.html at root
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("app/static/index.html")

# -------------------------------------------------
# 2️⃣ CREATE TABLES
# -------------------------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# 3️⃣ REGISTER ROUTERS
# -------------------------------------------------
app.include_router(sentiment.router, tags=["Sentiment"])
app.include_router(insight.router, tags=["Insight"])
app.include_router(stock_routes.router, tags=["Stocks"])
app.include_router(ai_routes.router, tags=["AI"])
app.include_router(market_routes.router, tags=["Market"])
app.include_router(history_routes.router, tags=["History"])

# -------------------------------------------------
# 4️⃣ BASIC HEALTH ROUTE
# -------------------------------------------------
@app.get("/health")
def root():
    return {"status": "ok", "message": "Backend is running successfully"}
