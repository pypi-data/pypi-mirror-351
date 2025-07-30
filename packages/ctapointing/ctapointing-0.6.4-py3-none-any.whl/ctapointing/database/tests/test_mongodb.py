from ctapointing.database import mongodb


def _test_create_read_mongo_config():
    user = "user"
    password = "password"
    host = "host"
    port = "port"
    assert mongodb.read_mongo_config() is None
    assert mongodb.read_mongo_config(filename="some random string") is None
    config = mongodb.create_mongo_config(
        user, password, host, port, filename="some_file.json"
    )
    assert config == mongodb.read_mongo_config("some_file.json")
