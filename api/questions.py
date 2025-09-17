# /api/questions.py

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database.models import Question as QuestionModel
from database.database import get_db

from config.config import QUESTION_TEXT_MAX 

logger = logging.getLogger(__name__)
router = APIRouter()


class QuestionCreate(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("text cannot be empty")
        if len(v) > QUESTION_TEXT_MAX:
            raise ValueError(f"text must be at most {QUESTION_TEXT_MAX} characters")
        return v

class QuestionRead(BaseModel):
    id: int
    text: str
    created_at: datetime


class AnswerRead(BaseModel):
    id: int
    question_id: int
    user_id: int
    text: str
    created_at: datetime


class QuestionDetail(QuestionRead):
    answers: List[AnswerRead]


@router.get("", response_model=List[QuestionRead])
def list_questions(db: Session = Depends(get_db)) -> List[QuestionRead]:
    """
    GET /questions
    Question listing.
    """
    items = db.query(QuestionModel).order_by(QuestionModel.id.desc()).all()
    return items


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)) -> QuestionRead:
    """
    POST /questions
    Question creation.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=422, detail="Empty question empty")

    question = QuestionModel(text=payload.text.strip())
    db.add(question)
    db.commit()
    db.refresh(question)

    logger.info("Created question %s", question.id)
    return question


@router.get("/{id}", response_model=QuestionDetail)
def get_question_info(id: int, db: Session = Depends(get_db)) -> QuestionDetail:
    """
    GET /questions/{id}
    Get question info.
    """
    question = db.get(QuestionModel, id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_question(id: int, db: Session = Depends(get_db)) -> Response:
    """
    DELETE /questions/{id}
    Remove question
    """
    question = db.get(QuestionModel, id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    logger.info("Deleted question %s", id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
