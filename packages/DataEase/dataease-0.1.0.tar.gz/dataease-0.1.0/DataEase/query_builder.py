class SQLQueryBuilder:
    def __init__(self):
        self.query_parts = {
            "select": "",
            "from": "",
            "join": "",
            "where": "",
            "order": "",
            "limit": "",
            "insert": "",
            "update": "",
            "delete": ""
        }
        self.mode = None

    def select(self, table, columns="*"):
        self.mode = "select"
        cols = ", ".join(columns) if isinstance(columns, list) else columns
        self.query_parts["select"] = f"SELECT {cols}"
        self.query_parts["from"] = f"FROM {table}"
        return self

    def join(self, join_type, table, on_condition):
        self.query_parts["join"] += f" {join_type.upper()} JOIN {table} ON {on_condition}"
        return self

    def order_by(self, column, ascending=True):
        order = "ASC" if ascending else "DESC"
        self.query_parts["order"] = f"ORDER BY {column} {order}"
        return self

    def limit(self, count):
        self.query_parts["limit"] = f"LIMIT {count}"
        return self

    def insert(self, table, data: dict):
        self.mode = "insert"
        cols = ", ".join(data.keys())
        placeholders = ", ".join([f"'{v}'" for v in data.values()])
        self.query_parts["insert"] = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        return self

    def update(self, table, data: dict):
        self.mode = "update"
        set_clause = ", ".join([f"{k}='{v}'" for k, v in data.items()])
        self.query_parts["update"] = f"UPDATE {table} SET {set_clause}"
        return self

    def delete(self, table):
        self.mode = "delete"
        self.query_parts["delete"] = f"DELETE FROM {table}"
        return self

    def where(self, conditions: dict):
        if conditions:
            clause = " AND ".join([f"{k}='{v}'" for k, v in conditions.items()])
            self.query_parts["where"] = f"WHERE {clause}"
        return self

    def build(self):
        if self.mode == "select":
            return " ".join(part for part in [
                self.query_parts["select"],
                self.query_parts["from"],
                self.query_parts["join"],
                self.query_parts["where"],
                self.query_parts["order"],
                self.query_parts["limit"]
            ] if part) + ";"
        elif self.mode == "insert":
            return self.query_parts["insert"] + ";"
        elif self.mode == "update":
            return " ".join(part for part in [
                self.query_parts["update"],
                self.query_parts["where"]
            ] if part) + ";"
        elif self.mode == "delete":
            return " ".join(part for part in [
                self.query_parts["delete"],
                self.query_parts["where"]
            ] if part) + ";"
        else:
            return ""
