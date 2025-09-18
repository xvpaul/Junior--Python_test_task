import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database.models import Question as QuestionModel
from database.database import get_db
from config.models import QuestionCreate, QuestionRead, QuestionDetail
from config.config import log_call  

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[QuestionRead])
@log_call()
def list_questions(db: Session = Depends(get_db)) -> List[QuestionRead]:
    """
    GET /questions
    Question listing.
    """
    items = db.query(QuestionModel).order_by(QuestionModel.id.desc()).all()
    return items


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
@log_call("create_question")
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
    return question


@router.get("/{id}", response_model=QuestionDetail)
@log_call()
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
@log_call("remove_question")
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)
