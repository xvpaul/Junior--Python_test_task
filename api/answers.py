import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database.models import Question, Answer as AnswerModel
from database.database import get_db
from config.models import AnswerCreate, AnswerRead
from config.config import log_call

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{id}/answers", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
@log_call("add_answer")
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
    return answer


@router.get("/{id}", response_model=AnswerRead)
@log_call()
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
@log_call("remove_answer")
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)
