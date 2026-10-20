from src.database.loader import DatabaseLoader


def test_deduplicate_tuples_keeps_first_row_for_each_conflict_key():
    rows = [
        ("NGA001", "Total", "all"),
        ("NGA001", "Total", "children"),
        ("NGA002", "Total", "all"),
    ]

    deduplicated = DatabaseLoader._deduplicate_tuples(rows, (0, 1))

    assert deduplicated == [
        ("NGA001", "Total", "all"),
        ("NGA002", "Total", "all"),
    ]
