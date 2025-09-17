import api.questions as qmod
import api.answers as amod

def _mk_question(client, txt="Q"):
    return client.post("/questions", json={"text": txt}).json()["id"]

def test_question_length_limit_trimmed(client, monkeypatch):
    monkeypatch.setattr(qmod, "QUESTION_TEXT_MAX", 5, raising=False)

    assert client.post("/questions", json={"text": "abcde"}).status_code == 201
    assert client.post("/questions", json={"text": "  abcde  "}).status_code == 201

    assert client.post("/questions", json={"text": "abcdef"}).status_code == 422
    assert client.post("/questions", json={"text": "  abcdef  "}).status_code == 422

    assert client.post("/questions", json={"text": "   "}).status_code == 422

def test_answer_length_limit_trimmed(client, monkeypatch):
    qid = _mk_question(client, "Len test Q")

    monkeypatch.setattr(amod, "ANSWER_TEXT_MAX", 3, raising=False)

    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "abc"}).status_code == 201
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "  abc  "}).status_code == 201

    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "abcd"}).status_code == 422
    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "  abcd  "}).status_code == 422

    assert client.post(f"/answers/{qid}/answers", json={"user_id": 1, "text": "   "}).status_code == 422
