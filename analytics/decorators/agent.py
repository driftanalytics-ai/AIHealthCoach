import json
import time
from datetime import datetime
from functools import wraps

from analytics.constants import ANALYTICS_QUERY_ID
from analytics.models import Agent, AgentQuery, Query, Stats
from analytics.utils import count_characters_in_json


class AgentTrackers:
    def track_agent(agent_name: str):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                metadata = []
                for arg in args:
                    try:
                        a = str(arg)
                    except:
                        continue
                    else:
                        metadata.append(a)
                for k, v in kwargs.items():
                    try:
                        ks = str(k)
                        vs = str(v)
                    except:
                        continue
                    else:
                        metadata.append((ks, vs))
                if not len(metadata):
                    metadata = None
                qid = kwargs.get(ANALYTICS_QUERY_ID)
                start = time.time()
                try:
                    response = func(*args, **kwargs)

                    end = time.time()
                except Exception as e:
                    completed = False
                    end = time.time()
                    update_agent_query(
                        qid, agent_name, start, end, completed, str(e), metadata
                    )
                    raise
                else:
                    completed = True
                    update_agent_query(
                        qid,
                        agent_name,
                        start,
                        end,
                        completed,
                        json.dumps(response),
                        metadata,
                    )
                    return response

            return wrapper

        return decorator


def update_agent_query(
    qid,
    agent_name: str,
    start_timestamp,
    end_timestamp,
    completed: bool,
    response,
    metadata,
):
    query, _ = Query.objects.get_or_create(id=qid)
    agent, created = Agent.objects.get_or_create(name=agent_name)
    if created:
        agent.token_usage_stats = Stats.objects.create()
        agent.runtime_stats = Stats.objects.create()
    tokens = count_characters_in_json(response)
    agent.runtime_stats.update_stats(end_timestamp - start_timestamp)
    agent.token_usage_stats.update_stats(float(tokens))
    print("creating agent query")
    agent_query = AgentQuery.objects.create(
        queryId=query,
        agent=agent,
        token_usage=tokens,
        startTimestamp=datetime.fromtimestamp(int(start_timestamp)),
        endTimestamp=datetime.fromtimestamp((int(end_timestamp))),
        response=response,
        metadata=metadata,
    )
    print("update complete")
