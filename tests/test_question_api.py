# tests/test_question_api.py
from database.models import Answer as AnswerModel


def test_create_question_trim_and_detail(client):
    r = client.post("/questions", json={"text": "Am I disabled?"})
    assert r.status_code == 201
    q = r.json()
    qid = q["id"]
    assert q["text"] == "Am I disabled?"
    assert "created_at" in q

    r2 = client.get(f"/questions/{qid}")
    assert r2.status_code == 200
    detail = r2.json()
    assert detail["id"] == qid
    assert detail["answers"] == []


def test_list_questions_desc_order(client):
    client.post("/questions", json={"text": "Q1"})
    client.post("/questions", json={"text": "Q2"})
    r = client.get("/questions")
    assert r.status_code == 200
    ids = [row["id"] for row in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_create_question_validation(client):
    for bad in ["", "   "]:
        r = client.post("/questions", json={"text": bad})
        assert r.status_code == 422


def test_delete_question_cascades_answers(client, db_session):
    qid = client.post("/questions", json={"text": "Cascade?"}).json()["id"]
    a1 = client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "A1"}).json()["id"]
    a2 = client.post(f"/answers/{qid}/answers", json={"user_id": 2, "text": "A2"}).json()["id"]

    assert client.delete(f"/questions/{qid}").status_code == 204
    assert client.get(f"/answers/{a1}").status_code == 404
    assert client.get(f"/answers/{a2}").status_code == 404

    remaining = db_session.query(AnswerModel).filter_by(question_id=qid).count()
    assert remaining == 0


def test_questions_404_and_405(client):
    assert client.get("/questions/999999").status_code == 404
    assert client.delete("/questions/999999").status_code == 404
    assert client.post("/questions/1", json={"text": "nope"}).status_code == 405


def test_question_with_unicode_and_long_text(client):
    text = "zovkekzov" + "x" * 900
    r = client.post("/questions", json={"text": text})
    assert r.status_code == 201
    q = r.json()
    assert q["text"].startswith("zovkekzov")
    text = "zovkekzov" + "x" * 1000
    r = client.post("/questions", json={"text": text})
    assert r.status_code == 422
