# tests/test_answer_api.py

from database.models import Answer as AnswerModel


def _mk_question(client, txt="Q"):
    return client.post("/questions", json={"text": txt}).json()["id"]


def test_add_get_delete_answer(client, db_session):
    qid = _mk_question(client, "With answer?")
    r = client.post(f"/answers/{qid}/answers", json={"user_id": 7, "text": "Because."})
    assert r.status_code == 201
    ans = r.json()
    aid = ans["id"]

    assert ans["question_id"] == qid
    assert ans["user_id"] == 7
    assert ans["text"] == "Because."
    assert "created_at" in ans

    r2 = client.get(f"/answers/{aid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == aid

    assert client.delete(f"/answers/{aid}").status_code == 204
    assert client.get(f"/answers/{aid}").status_code == 404

    assert db_session.get(AnswerModel, aid) is None


def test_add_answer_question_not_found(client):
    r = client.post("/answers/999999/answers", json={"user_id": 1, "text": "x"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Question not found"


def test_add_answer_payload_validation(client):
    qid = _mk_question(client)
    assert client.post(f"/answers/{qid}/answers", json={"text": "hi"}).status_code == 422 
    assert client.post(f"/answers/{qid}/answers", json={"user_id": "oops", "text": "hi"}).status_code == 422
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1}).status_code == 422 


def test_answer_unicode_and_very_long(client):
    qid = _mk_question(client, txt="Unicode Q")
    long_text = "λ" * 1024 + " 🧪"
    r = client.post(f"/answers/{qid}/answers", json={"user_id": 42, "text": long_text})
    assert r.status_code == 201
    body = r.json()
    assert body["text"].endswith("🧪")


def test_answer_404s(client):
    assert client.get("/answers/999999").status_code == 404
    assert client.delete("/answers/999999").status_code == 404
