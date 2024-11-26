import datetime
import json

from django.http.request import HttpRequest
from rest_framework.request import Request
from rest_framework.response import Response

from analytics.constants import ANALYTICS_QUERY_ID
from analytics.models import Agent, AgentQuery, Query


class QueryTracker:
    # def track_query(query_name: str):
    #     def decorator(func):
    #         def wrapper(*args,**kwargs):
    #             return func(*args,**kwargs):
    #         return wrapper
    #     return decorator
    def track_query(query_name: str):
        def decorator(func):

            query = Query.objects.create()
            start_agent, _ = Agent.objects.get_or_create(name="__start__")
            first_agent_query = AgentQuery.objects.create(
                queryId=query,
                agent=start_agent,
                token_usage=0,
                startTimestamp=datetime.datetime.now(),
                endTimestamp=datetime.datetime.now(),
                response=None,
                completed=True,
                metadata=None,
            )
            first_agent_query.save()
            query.save()

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
                    response = func(*args, **kwargs)
                except Exception as e:
                    end_agent, _ = Agent.objects.get_or_create(name="__end__")
                    query.refresh_from_db()
                    last_agent_query = AgentQuery.objects.create(
                        queryId=query,
                        agent=end_agent,
                        token_usage=0,
                        startTimestamp=datetime.datetime.now(),
                        endTimestamp=datetime.datetime.now(),
                        response=query.response,
                        completed=False,
                        metadata=None,
                    )
                    query.refresh_from_db()
                    query.end_timestamp = datetime.datetime.now()
                    query.save()
                    last_agent_query.save()
                    raise
                else:
                    if isinstance(response, Response):
                        query.refresh_from_db()
                        query.response = str(response.data)
                        # query.end_timestamp = datetime.datetime.now()
                        query.save()

                    return response

            completed = True
            aqs = AgentQuery.objects.filter(queryId=query.id)
            for aq in aqs:
                completed &= aq.completed
            query.refresh_from_db()
            query.completed = completed
            end_agent, _ = Agent.objects.get_or_create(name="__end__")
            last_agent_query = AgentQuery.objects.create(
                queryId=query,
                agent=end_agent,
                token_usage=0,
                startTimestamp=datetime.datetime.now(),
                endTimestamp=datetime.datetime.now(),
                response=query.response,
                completed=True,
                metadata=None,
            )
            last_agent_query.save()
            query.save()
            return wrapper

        return decorator
