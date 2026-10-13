from unittest.mock import patch

from app.agent import run_forever, run_once
from app.config import Settings
from app.sender import MetricsDeliveryError

SETTINGS = Settings(
    metrics_endpoint="http://api:8000/metrics",
    collection_interval=1,
    request_timeout=1,
)

METRICS = {
    "timestamp": "t",
    "hostname": "h",
    "cpu": {},
    "memory": {},
    "system": {},
}


@patch("app.agent.send_metrics")
@patch("app.agent.collect_system_metrics")
def test_run_once(mock_collect, mock_send):
    mock_collect.return_value = METRICS
    mock_send.return_value = {"status_code": 201}

    result = run_once(SETTINGS)

    assert result == {"status_code": 201}
    mock_send.assert_called_once()


@patch("app.agent.time.sleep", side_effect=KeyboardInterrupt)
@patch("app.agent.run_once", return_value={"status_code": 201})
@patch("app.agent.Settings.from_env", return_value=SETTINGS)
def test_run_forever_stops_on_interrupt(mock_env, mock_run, mock_sleep):
    # Le KeyboardInterrupt levé par sleep() sort de la boucle.
    try:
        run_forever()
    except KeyboardInterrupt:
        pass

    mock_run.assert_called_once()


@patch("app.agent.time.sleep", side_effect=KeyboardInterrupt)
@patch(
    "app.agent.run_once",
    side_effect=MetricsDeliveryError("API indisponible"),
)
@patch("app.agent.Settings.from_env", return_value=SETTINGS)
def test_run_forever_survives_delivery_error(mock_env, mock_run, mock_sleep):
    try:
        run_forever()
    except KeyboardInterrupt:
        pass

    mock_run.assert_called_once()
