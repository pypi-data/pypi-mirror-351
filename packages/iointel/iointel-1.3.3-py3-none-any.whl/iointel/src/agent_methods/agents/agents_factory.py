from ...agents import Agent
from ..data_models.datamodels import AgentParams, Tool, AgentSwarm
from typing import Sequence
from .tool_factory import resolve_tools


def create_agent(params: AgentParams) -> Agent:
    """
    Create an Agent instance from the given AgentParams.
    When rehydrating from YAML, each tool in params.tools is expected to be either:
      - a dict (serialized Tool) with a "body" field,
      - a Tool instance,
      - or a callable.
    In the dict case, we ensure that the "body" is preserved.
    """
    # Dump the rest of the agent data (excluding tools) then reinsert our resolved tools.
    agent_data = params.model_dump(exclude={"tools"})
    agent_data["tools"] = resolve_tools(params)
    if output_type := agent_data.get("output_type"):
        if isinstance(output_type, str):
            agent_data["output_type"] = globals().get(output_type) or getattr(
                __builtins__, output_type, output_type
            )
    return Agent(**agent_data)


def create_swarm(agents: list[AgentParams] | AgentSwarm):
    raise NotImplementedError()


def agent_or_swarm(
    agent_obj: Agent | Sequence[Agent], store_creds: bool
) -> list[AgentParams] | AgentSwarm:
    """
    Serializes an agent object into a list of AgentParams.

    - If the agent_obj is an individual agent (has an 'api_key'),
      returns a list with one AgentParams instance.
    - If the agent_obj is a swarm (has a 'members' attribute),
      returns a list of AgentParams for each member.
    """

    def get_api_key(agent: Agent) -> str:
        if not (api_key := agent.api_key):
            return None
        if store_creds and hasattr(api_key, "get_secret_value"):
            return api_key.get_secret_value()
        return api_key

    def make_params(agent: Agent) -> AgentParams:
        return AgentParams(
            name=agent.name,
            instructions=agent.instructions,
            persona=agent.persona,
            tools=[
                Tool.from_function(t).model_dump(exclude={"fn", "fn_metadata"})
                for t in agent.tools
            ],
            model=getattr(agent.model, "model_name", None),
            model_settings=agent.model_settings,
            api_key=get_api_key(agent),
            base_url=agent.base_url,
            memory=agent.memory,
            context=agent.context,
            output_type=agent.output_type,
        )

    if isinstance(agent_obj, Sequence):
        # group of agents not packed as a swarm
        assert all(not hasattr(ag, "members") for ag in agent_obj), (
            "Nested swarms not allowed"
        )
        return [make_params(ag) for ag in agent_obj]
    if hasattr(agent_obj, "api_key"):
        # Individual agent.
        return [make_params(agent_obj)]
    if hasattr(agent_obj, "members"):
        # Swarm: return AgentParams for each member.
        return AgentSwarm(members=[make_params(member) for member in agent_obj.members])
    # Fallback: return a minimal AgentParams.
    return [make_params(agent_obj)]
