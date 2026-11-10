from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.candidate import CandidateExtraction
from app.services.ai.extraction import score_candidate
from app.services.whatsapp import parse_incoming

client = TestClient(app)

SAMPLE = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "metadata": {"phone_number_id": "123"},
                        "messages": [
                            {
                                "from": "212600000000",
                                "id": "m1",
                                "type": "text",
                                "text": {"body": "Salam, bghit nkhdem"},
                            },
                            {
                                "from": "212600000000",
                                "id": "m2",
                                "type": "audio",
                                "audio": {"id": "media-42"},
                            },
                        ],
                    }
                }
            ]
        }
    ]
}


def test_verify_ok():
    token = get_settings().whatsapp_verify_token
    r = client.get(
        "/api/v1/webhooks/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": token, "hub.challenge": "abc"},
    )
    assert r.status_code == 200 and r.text == "abc"


def test_verify_bad_token():
    r = client.get(
        "/api/v1/webhooks/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "abc"},
    )
    assert r.status_code == 403


def test_parse_incoming():
    msgs = parse_incoming(SAMPLE)
    assert [m["type"] for m in msgs] == ["text", "audio"]
    assert msgs[0]["text"] == "Salam, bghit nkhdem"
    assert msgs[1]["media_id"] == "media-42"


def test_receive_counts_messages():
    r = client.post("/api/v1/webhooks/whatsapp", json=SAMPLE)
    assert r.status_code == 200 and r.json() == {"received": 2}


def test_score_bounds():
    full = CandidateExtraction(
        full_name="A", city="Rabat", experience_years=10, has_pro_card=True, availability="nuit"
    )
    assert score_candidate(full) == 100
    assert score_candidate(CandidateExtraction()) == 0
