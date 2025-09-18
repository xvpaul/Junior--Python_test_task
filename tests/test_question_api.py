from database.models import Answer as AnswerModel

def test_create_question_and_detail_schema(client, api):
    api = api(client)
    q = api.mk_question("  Why is the sky blue?  ")
    api.validate(q, "Question")

    qid = q["id"]
    detail = api.get(f"/questions/{qid}")
    api.validate(detail, "QuestionDetail")
    assert detail["id"] == qid
    assert detail["answers"] == []

def test_list_questions_desc_order_and_schema(client, api):
    api = api(client)
    api.mk_question("Q1")
    api.mk_question("Q2")
    data = api.get("/questions")
    api.validate(data, "QuestionList")
    ids = [row["id"] for row in data]
    assert ids == sorted(ids, reverse=True)

def test_create_question_validation_blank_and_whitespace(client):
    from conftest import validate_schema
    for bad in ["", "   "]:
        r = client.post("/questions", json={"text": bad})
        assert r.status_code == 422
        validate_schema(r.json(), "Error")

def test_delete_question_cascades_answers(client, db_session, api):
    api = api(client)
    q = api.mk_question("Cascade?")
    qid = q["id"]
    a1 = api.add_answer(qid, 1, "A1")["id"]
    a2 = api.add_answer(qid, 2, "A2")["id"]
    api.delete(f"/questions/{qid}")
    assert client.get(f"/answers/{a1}").status_code == 404
    assert client.get(f"/answers/{a2}").status_code == 404
    remaining = db_session.query(AnswerModel).filter_by(question_id=qid).count()
    assert remaining == 0

def test_questions_404_and_405(client):
    assert client.get("/questions/999999").status_code == 404
    assert client.delete("/questions/999999").status_code == 404
    assert client.post("/questions/1", json={"text": "nope"}).status_code == 405
