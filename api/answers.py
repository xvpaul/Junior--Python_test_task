# /api/answers.py

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import Question, Answer as AnswerModel
from database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class AnswerCreate(BaseModel):
    user_id: int
    text: str


class AnswerRead(BaseModel):
    id: int
    question_id: int
    user_id: int
    text: str
    created_at: datetime



@router.post("/{id}/answers", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
def add_answer(id: int, payload: AnswerCreate, db: Session = Depends(get_db)) -> AnswerModel:
    """
    POST /answers/{id}/answers
    Add answer.
    """
    question = db.get(Question, id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = AnswerModel(user_id=payload.user_id, text=payload.text)
    question.answers.append(answer)

    db.add(question) 
    db.commit()
    db.refresh(answer)

    logger.info("Created answer %s for question %s by user %s", answer.id, id, payload.user_id)
    return answer


@router.get("/{id}", response_model=AnswerRead)
def get_answer(id: int, db: Session = Depends(get_db)) -> AnswerModel:
    """
    GET /answers/{id}/
    Get answer by id.
    """
    answer = db.get(AnswerModel, id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    return answer


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_answer(id: int, db: Session = Depends(get_db)) -> Response:
    """
    GET /answers/{id}/ 
    Remove answer by id. 
    """
    answer = db.get(AnswerModel, id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    db.delete(answer)
    db.commit()
    logger.info("Deleted answer %s", id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
 