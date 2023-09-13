from app.auth import utils


def test_password():
    password = "password"
    password_hash = utils.hashpwd(password)

    assert len(password_hash) == 60
    assert utils.checkpwd(password, password_hash) is True
    assert utils.checkpwd("bad_password", password_hash) is False


def test_token():
    assert len(utils.new_token()) == 43
