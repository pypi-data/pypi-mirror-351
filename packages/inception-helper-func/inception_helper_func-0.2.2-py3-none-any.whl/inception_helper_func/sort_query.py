ES_SORT_QUERY = {
    "newest": {"created_at_epoch": {"order": "desc"}},
    "oldest": {"created_at_epoch": {"order": "asc"}},
    "last_updated": {"updated_at_epoch": {"order": "desc"}},
    "a_z": {"name": {"order": "asc"}},
    "z_a": {"name": {"order": "desc"}},
}

MONGO_DB_SORT_QUERY = {
    "newest": {"created_at_epoch": -1},
    "oldest": {"created_at_epoch": 1},
    "last_updated": {"updated_at_epoch": -1},
    "a_z": {"name": 1},
    "z_a": {"name": -1},
}


def sort_query_es(sort_by: str, field_to_sort_by: str = None) -> dict:
    if sort_by in ["a_z", "z_a"] and field_to_sort_by:
        return {field_to_sort_by: ES_SORT_QUERY[sort_by]["name"]}
    else:
        return ES_SORT_QUERY[sort_by]


def sort_query_mongo(sort_by: str, field_to_sort_by: str = None) -> dict:
    if sort_by in ["a_z", "z_a"] and field_to_sort_by:
        return {field_to_sort_by: MONGO_DB_SORT_QUERY[sort_by]["name"]}
    else:
        return MONGO_DB_SORT_QUERY[sort_by]


if __name__ == "__main__":
    print(sort_query_es("newest"))
