import json

from analytics.constants import ANALYTICS_QUERY_ID
from analytics.models import AgentQuery, Query
from django.http.request import HttpRequest
from rest_framework.request import Request


class QueryTracker:
    def track_query(query_name: str):
        def decorator(func):

            query = Query.objects.create()

            def wrapper(*args, **kwargs):
                print("ARGS ", args)
                for arg in args:

                    if isinstance(arg, HttpRequest):
                        request_body = arg.body.decode("utf-8")
                        query.request_body = json.loads(request_body)
                        query.save()
                    if isinstance(arg, Request):
                        request_body = arg.data
                        query.request_body = request_body
                        query.save()
                kwargs[ANALYTICS_QUERY_ID] = query.id
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    raise

            completed = True
            aqs = AgentQuery.objects.filter(queryId=query.id)
            for aq in aqs:
                completed &= aq.completed
            query.completed = completed
            query.save()
            return wrapper

        return decorator
