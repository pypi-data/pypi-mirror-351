from DataEase.query_builder import SQLQueryBuilder

def test_join_and_order():
    query = (
        SQLQueryBuilder()
        .select("orders", ["orders.id", "users.name"])
        .join("LEFT", "users", "orders.user_id = users.id")
        .order_by("orders.id")
        .build()
    )
    assert "LEFT JOIN users ON orders.user_id = users.id" in query
    assert "ORDER BY orders.id ASC" in query

def test_limit_clause():
    query = SQLQueryBuilder().select("users").limit(10).build()
    assert query.endswith("LIMIT 10;")
