import os
import uvicorn
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")

description = f"""
Welcome to this Real-time Payments API! Try it out 🕹️
## Endpoints

There is currently just a few endpoints:

* `/`: **GET** request that display a simple default message.
* `/current-transactions`: **GET** request that gives you 1 current transaction

The API limits the number of calls to **{RATE_LIMIT}** 🚧. If you try more, your endpoint will throw back an error.
"""

app = FastAPI(
    title="Real-time Payments API 💵",
    description=description,
    version="0.1",
    contact={
        "name": "Slim Ghorbal",
    },
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@lru_cache(maxsize=1)
def get_full_dataframe():
    """
    Get the full dataframe from the CSV file.
    This function is cached for performance reasons.
    """
    filename = "https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv"
    return pd.read_csv(filename, header=0, index_col=[0])

@app.get("/current-transactions")
@limiter.limit(RATE_LIMIT)
async def current_transactions(request: Request):
    """
    Return one current transaction in [`.to_json(orient="split")`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html) format in Pandas.
    """
    df = get_full_dataframe()
    df = df.sample().loc[:, ~df.columns.isin(["trans_date_trans_time", "fraud", "unix_time"])]
    df["current_time"]= datetime.now()
    
    return df.to_json(orient="split")

# ========================================================================
if __name__=="__main__":
    PORT = os.getenv("PORT", 4000)
    uvicorn.run(app, host="0.0.0.0", port=PORT) 