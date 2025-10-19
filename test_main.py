from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Sentiment Analysis API is running!"}


def test_predict_sentiment():
    test_text = "What a lovely day!"

    response = client.post(
        "predict/",
        headers={"Content-Type": "application/json"},
        json={"text": test_text}
    )

    assert response.status_code == 200
    res = response.json()
    print("response content: ", res)
    assert res["input_text"] == test_text
    assert res["prediction"]["label"] in ["POSITIVE", "NEGATIVE"]
    assert 0 < res["prediction"]["score"] < 1