from flask import current_app


def add_to_index(index, model):
    if current_app.elasticsearch is None:
        return
    payload = {field: getattr(model, field) for field in model.__searchable__}
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)


def remove_from_index(index, model):
    if current_app.elasticsearch is None:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if current_app.elasticsearch is None:
        return [], 0
    results = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page,
    )
    ids = [int(hit['_id']) for hit in results['hits']['hits']]
    return ids, results['hits']['total']['value']
