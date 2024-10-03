from sqlalchemy import text


def test_current_db_test(db_connection):
    query = "SELECT current_database();"
    curr_db_name = db_connection.execute(text(query)).scalar()
    assert curr_db_name == "test_db", f"Expected 'test_db', but got '{curr_db_name}'"


def test_database_exists(db_connection):
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM pg_database
            WHERE datname = 'test_db'
        );
    """

    exists = db_connection.execute(text(query)).scalar()
    assert exists, "The test database 'test_db' does not exist"
