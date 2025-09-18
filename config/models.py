from pydantic import BaseModel, field_validator
from datetime import datetime
from config.config import QUESTION_TEXT_MAX, ANSWER_TEXT_MAX
from typing import List


class AnswerCreate(BaseModel):
    user_id: int
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("text cannot be empty")
        if len(v) > ANSWER_TEXT_MAX:
            raise ValueError(f"text must be at most {ANSWER_TEXT_MAX} characters")
        return v


class AnswerRead(BaseModel):
    id: int
    question_id: int
    user_id: int
    text: str
    created_at: datetime


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