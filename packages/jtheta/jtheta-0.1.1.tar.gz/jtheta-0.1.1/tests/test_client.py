from jtheta import JThetaClient

def test_init():
    client = JThetaClient(api_key="test")
    assert client.api_key == "test"
