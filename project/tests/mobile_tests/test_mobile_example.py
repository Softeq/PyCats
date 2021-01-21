import pytest


@pytest.mark.usefixtures("start_mobile_session")
@pytest.mark.mabile_sample
@pytest.mark.parametrize('city', ['San Jose', "Los Angeles"])
def test_mobile_sample(api_token, city):
    """
    TBD
    """
    pass
