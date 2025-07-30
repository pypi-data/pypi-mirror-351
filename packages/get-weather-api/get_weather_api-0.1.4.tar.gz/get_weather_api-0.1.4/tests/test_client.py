from getweatherunderground.client import dummy_api_call, get_weather_data

def test_dummy_api_call(monkeypatch):
    monkeypatch.setenv("API_KEY", "testkey123")
    assert dummy_api_call() == "Calling API with key: test****"

def test_get_weather_data(monkeypatch):
    # Mock the API key
    # monkeypatch.setenv("API_KEY", "testkey123")
    # weather_data = get_weather_data(weather_station="RJAA", country_code="JP", startDate="20190201", endDate="20190301", number=2, timezone="US/Pacific")
    weather_data = get_weather_data(weather_station="RPLL", country_code="PH", startDate="20201001", endDate="20201101", number=2, timezone="Asia/Manila")
    # print(weather_data.head())
    assert not weather_data.empty

def test_get_weather_data_fail(monkeypatch):
    # Mock the API key
    monkeypatch.setenv("API_KEY", "testkey123")
    weather_data = get_weather_data(weather_station="RPLL", country_code="PH", startDate="20201001", endDate="20201101", number=2, timezone="Asia/Manila")
    assert weather_data.empty