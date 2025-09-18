from database.models import Answer as AnswerModel
import config.models as smod

def test_add_get_delete_answer_flow(client, db_session, api):
    api = api(client)
    qid = api.mk_question("With answer?")["id"]
    ans = api.add_answer(qid, 7, "Because.")
    api.validate(ans, "Answer")
    aid = ans["id"]
    got = api.get(f"/answers/{aid}")
    api.validate(got, "Answer")
    assert got["id"] == aid
    api.delete(f"/answers/{aid}")
    assert client.get(f"/answers/{aid}").status_code == 404
    assert db_session.get(AnswerModel, aid) is None

def test_add_answer_question_not_found(client):
    r = client.post("/answers/999999/answers", json={"user_id": 1, "text": "x"})
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body

def test_add_answer_payload_validation(client, api):
    api = api(client)
    qid = api.mk_question()["id"]
    assert client.post(f"/answers/{qid}/answers", json={"text": "hi"}).status_code == 422
    assert client.post(f"/answers/{qid}/answers", json={"user_id": "oops", "text": "hi"}).status_code == 422
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1}).status_code == 422

def test_answer_unicode_long_text(client, api):
    api = api(client)
    qid = api.mk_question("Unicode Q")["id"]
    long_text = "λ" * 1024 + " 🧪"
    ans = api.add_answer(qid, 42, long_text)
    assert ans["text"].endswith("🧪")

def test_length_limits_monkeypatch(client, api, monkeypatch):
    monkeypatch.setattr(smod, "QUESTION_TEXT_MAX", 5, raising=False)
    monkeypatch.setattr(smod, "ANSWER_TEXT_MAX", 3, raising=False)
    api = api(client)
    assert client.post("/questions", json={"text": "abcde"}).status_code in (200, 201)
    assert client.post("/questions", json={"text": "abcdef"}).status_code == 422
    assert client.post("/questions", json={"text": "   "}).status_code == 422
    qid = api.mk_question("abcde")["id"]
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "abc"}).status_code in (200, 201)
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "abcd"}).status_code == 422
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "   "}).status_code == 422


def test_answer_404s(client):
    assert client.get("/answers/999999").status_code == 404
    assert client.delete("/answers/999999").status_code == 404
