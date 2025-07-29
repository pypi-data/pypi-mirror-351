from __future__ import annotations

import asyncio
import random
from typing import Any, Optional
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from ..environment.sim.person_service import PersonService
from ..logger import get_logger
from ..memory import Memory
from .agent_base import Agent, AgentToolbox, AgentType
from .block import Block
from .decorator import register_get

__all__ = [
    "CitizenAgentBase",
    "FirmAgentBase",
    "BankAgentBase",
    "NBSAgentBase",
    "GovernmentAgentBase",
]


class CitizenAgentBase(Agent):
    """
    Represents a citizen agent within the simulation environment.

    - **Description**:
        - This class extends the base `Agent` class and is designed to simulate the behavior of a city resident.
        - It includes initialization of various clients (like LLM, economy) and services required for the agent's operation.
        - Provides methods for binding the agent to the simulator and economy system, as well as handling specific types of messages.

    - **Attributes**:
        - `_mlflow_client`: An optional client for integrating with MLflow for experiment tracking and management.
    """

    def __init__(
        self,
        id: int,
        name: str,
        toolbox: AgentToolbox,
        memory: Memory,
        agent_params: Optional[Any] = None,
        blocks: Optional[list[Block]] = None,
    ) -> None:
        """
        Initialize a new instance of the CitizenAgent.

        - **Args**:
            - `id` (`int`): The ID of the agent.
            - `name` (`str`): The name or identifier of the agent.
            - `toolbox` (`AgentToolbox`): The toolbox of the agent.
            - `memory` (`Memory`): The memory of the agent.

        - **Description**:
            - Initializes the CitizenAgent with the provided parameters and sets up necessary internal states.
        """
        super().__init__(
            id=id,
            name=name,
            type=AgentType.Citizen,
            toolbox=toolbox,
            memory=memory,
            agent_params=agent_params,
            blocks=blocks,
        )

    async def init(self):
        """
        Initialize the agent.

        - **Description**:
            - Calls the `_bind_to_simulator` method to establish the agent within the simulation environment.
            - Calls the `_bind_to_economy` method to integrate the agent into the economy simulator.
        """
        await super().init()
        await self._bind_to_simulator()
        await self._bind_to_economy()

    async def _bind_to_simulator(self):
        """
        Bind the agent to the Traffic Simulator.

        - **Description**:
            - If the simulator is set, this method binds the agent by creating a person entity in the simulator based on the agent's attributes.
            - Updates the agent's status with the newly created person ID from the simulator.
            - Logs the successful binding to the person entity added to the simulator.
        """
        FROM_MEMORY_KEYS = {
            "attribute",
            "home",
            "work",
            "vehicle_attribute",
            "bus_attribute",
            "pedestrian_attribute",
            "bike_attribute",
        }
        simulator = self.environment
        status = self.status
        dict_person = PersonService.default_person(return_dict=True)
        dict_person["id"] = self.id
        for _key in FROM_MEMORY_KEYS:
            try:
                _value = await status.get(_key)
                if _value:
                    dict_person[_key] = _value
            except KeyError as e:
                continue
        await simulator.add_person(dict_person)

    async def _bind_to_economy(self):
        """
        Bind the agent to the Economy Simulator.
        """
        person_id = await self.status.get("id")
        currency = await self.status.get("currency")
        skill = await self.status.get("work_skill")
        consumption = 0.0
        income = 0.0
        await self.environment.economy_client.add_agents(
            {
                "id": person_id,
                "currency": currency,
                "skill": skill,
                "consumption": consumption,
                "income": income,
            }
        )

    async def update_motion(self):
        """
        Update the motion of the agent. Usually used in the starting of the `forward` method.
        """
        resp = await self.environment.get_person(self.id)
        resp_dict = resp["person"]
        for k, v in resp_dict.get("motion", {}).items():
            try:
                await self.status.get(k)
                await self.status.update(
                    k, v, mode="replace", protect_llm_read_only_fields=False
                )
            except KeyError as e:
                get_logger().debug(
                    f"KeyError: {e} when updating motion of agent {self.id}"
                )
                continue

    async def handle_gather_message(self, payload: dict):
        """
        Handle a gather message received by the agent.

        - **Args**:
            - `payload` (`dict`): The message payload containing the target attribute and sender ID.

        - **Description**:
            - Extracts the target attribute and sender ID from the payload.
            - Retrieves the content associated with the target attribute from the agent's status.
            - Prepares a response payload with the retrieved content and sends it back to the sender using `_send_message`.
        """
        # Process the received message, identify the sender
        # Parse sender ID and message content from the message
        target = payload["target"]
        sender_id = payload["from"]
        content = await self.status.get(f"{target}")
        payload = {
            "from": self.id,
            "content": content,
        }
        await self._send_message(sender_id, payload, "gather_receive")

    async def get_aoi_info(self):
        """Get the surrounding environment information - aoi information"""
        position = await self.status.get("position")
        if "aoi_position" in position:
            parent_id = position["aoi_position"]["aoi_id"]
            return self.environment.sense_aoi(parent_id)
        else:
            return None

    @register_get("Get the current time in the format of HH:MM:SS")
    async def get_nowtime(self):
        """Get the current time"""
        now_time = self.environment.get_datetime(format_time=True)
        return now_time[1]

    async def before_forward(self):
        """
        Before forward.
        """
        await super().before_forward()
        # sync agent status with simulator
        await self.update_motion()
        get_logger().debug(f"Agent {self.id}: Finished main workflow - update motion")


class InstitutionAgentBase(Agent):
    """
    Represents an institution agent within the simulation environment.

    - **Description**:
        - This class extends the base `Agent` class and is designed to simulate the behavior of an institution, such as a bank, government body, or corporation.
        - It includes initialization of various clients (like LLM, economy) and services required for the agent's operation.
        - Provides methods for binding the agent to the economy system and handling specific types of messages, like gathering information from other agents.

    - **Attributes**:
        - `_mlflow_client`: An optional client for integrating with MLflow for experiment tracking and management.
        - `_gather_responses`: A dictionary mapping agent IDs to `asyncio.Future` objects used for collecting responses to gather requests.
    """

    def __init__(
        self,
        id: int,
        name: str,
        toolbox: AgentToolbox,
        memory: Memory,
        agent_params: Optional[Any] = None,
        blocks: Optional[list[Block]] = None,
    ):
        """
        Initialize a new instance of the InstitutionAgent.

        - **Args**:
            - `name` (`str`): The name or identifier of the agent.
            - `toolbox` (`AgentToolbox`): The toolbox of the agent.
            - `memory` (`Memory`): The memory of the agent.

        - **Description**:
            - Initializes the InstitutionAgent with the provided parameters and sets up necessary internal states.
            - Adds a response collector (`_gather_responses`) for handling responses to gather requests.
        """
        super().__init__(
            id=id,
            name=name,
            type=AgentType.Institution,
            toolbox=toolbox,
            memory=memory,
            agent_params=agent_params,
            blocks=blocks,
        )

    async def init(self):
        """
        Initialize the agent.

        - **Description**:
            - Calls the `_bind_to_economy` method to integrate the agent into the economy simulator.
        """
        await super().init()
        await self._bind_to_economy()

    async def _bind_to_economy(self):
        """
        Bind the agent to the Economy Simulator.

        - **Description**:
            - Calls the `_bind_to_economy` method to integrate the agent into the economy system.
            - Note that this method does not bind the agent to the simulator itself; it only handles the economy integration.
        """
        map_header: dict = self.environment.map.get_map_header()
        # TODO: remove random position assignment
        await self.status.update(
            "position",
            {
                "xy_position": {
                    "x": float(
                        random.randrange(
                            start=int(map_header["west"]),
                            stop=int(map_header["east"]),
                        )
                    ),
                    "y": float(
                        random.randrange(
                            start=int(map_header["south"]),
                            stop=int(map_header["north"]),
                        )
                    ),
                }
            },
            protect_llm_read_only_fields=False,
        )
        _type = None
        _status = self.status
        _id = await _status.get("id")
        _type = await _status.get("type")
        nominal_gdp = await _status.get("nominal_gdp", [])
        real_gdp = await _status.get("real_gdp", [])
        unemployment = await _status.get("unemployment", [])
        wages = await _status.get("wages", [])
        prices = await _status.get("prices", [])
        inventory = await _status.get("inventory", 0)
        price = await _status.get("price", 0)
        currency = await _status.get("currency", 0.0)
        interest_rate = await _status.get("interest_rate", 0.0)
        bracket_cutoffs = await _status.get("bracket_cutoffs", [])
        bracket_rates = await _status.get("bracket_rates", [])
        consumption_currency = await _status.get("consumption_currency", [])
        consumption_propensity = await _status.get("consumption_propensity", [])
        income_currency = await _status.get("income_currency", [])
        depression = await _status.get("depression", [])
        locus_control = await _status.get("locus_control", [])
        working_hours = await _status.get("working_hours", [])
        employees = await _status.get("employees", [])
        citizens = await _status.get("citizens", [])
        demand = await _status.get("demand", 0)
        sales = await _status.get("sales", 0)
        await self.environment.economy_client.add_orgs(
            {
                "id": _id,
                "type": _type,
                "nominal_gdp": nominal_gdp,
                "real_gdp": real_gdp,
                "unemployment": unemployment,
                "wages": wages,
                "prices": prices,
                "inventory": inventory,
                "price": price,
                "currency": currency,
                "interest_rate": interest_rate,
                "bracket_cutoffs": bracket_cutoffs,
                "bracket_rates": bracket_rates,
                "consumption_currency": consumption_currency,
                "consumption_propensity": consumption_propensity,
                "income_currency": income_currency,
                "depression": depression,
                "locus_control": locus_control,
                "working_hours": working_hours,
                "employees": employees,
                "citizens": citizens,
                "demand": demand,
                "sales": sales,
            }
        )

    async def react_to_intervention(self, intervention_message: str):
        """
        React to an intervention.

        - **Args**:
            - `intervention_message` (`str`): The message of the intervention.

        - **Description**:
            - React to an intervention.
        """
        ...


class FirmAgentBase(InstitutionAgentBase):
    """
    Represents a firm agent within the simulation environment.
    """


class BankAgentBase(InstitutionAgentBase):
    """
    Represents a bank agent within the simulation environment.
    """

    ...


class NBSAgentBase(InstitutionAgentBase):
    """
    Represents a National Bureau of Statistics agent within the simulation environment.
    """

    ...


class GovernmentAgentBase(InstitutionAgentBase):
    """
    Represents a government agent within the simulation environment.
    """

    ...
