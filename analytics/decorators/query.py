import json

from analytics.constants import ANALYTICS_QUERY_ID
from analytics.models import Query
from django.http.request import HttpRequest


class QueryTracker:
    def track_query(query_name: str):
        def decorator(func):

            def wrapper(*args, **kwargs):
                query = Query.objects.create()
                for arg in args:
                    if isinstance(arg, HttpRequest):
                        request_body = arg.body.decode("utf-8")
                        query.request_body = json.loads(request_body)
                        query.save()
                kwargs[ANALYTICS_QUERY_ID] = query.id
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    raise

            return wrapper

        return decorator
