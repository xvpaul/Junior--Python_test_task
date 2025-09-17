# main.py

from fastapi import FastAPI
from fastapi import FastAPI
from api.answers import router as answers_router
from api.questions import router as questions_router
import logging

logs = logging.getLogger(__name__)

app = FastAPI()

app.include_router(answers_router, prefix="/answers", tags=["answers"])
app.include_router(questions_router, prefix="/questions", tags=["questions"])
