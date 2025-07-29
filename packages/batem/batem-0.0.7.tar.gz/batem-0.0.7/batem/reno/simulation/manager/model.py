"""
Manager models for energy system control.

This module provides abstract and concrete implementations of energy
system managers that control and optimize energy distribution between
PV production and member consumption.
"""

from abc import ABC, abstractmethod
from batem.reno.pv.model import PVPlant
from batem.reno.simulation.member.model import Member
from batem.reno.simulation.recommendation import (
    Recommendation, RecommendationType)
from datetime import datetime

from batem.reno.simulation.scenario import Scenario
from batem.reno.utils import TimeSpaceHandler


class Manager(ABC):
    """
    Abstract base class for energy system managers.

    This class defines the interface for energy system managers that
    control and optimize energy distribution between PV production and
    member consumption.

    Attributes:
        time_space_handler: Handler for time and space operations
        recommendations: Dictionary mapping timestamps to recommendations
    """

    def __init__(self, time_space_handler: TimeSpaceHandler,
                 recommendation_interval: list[int]):
        """
        Initialize a new manager.

        Args:
            time_space_handler: Handler for time and space operations
            recommendation_interval: Interval of the day
            when recommendations are valid
        """
        self.time_space_handler = time_space_handler
        self.recommendation_interval = recommendation_interval
        self.recommendations: dict[datetime, Recommendation] = {}

    @abstractmethod
    def step(self,
             k: int,
             members: list[Member],
             pv: PVPlant) -> Recommendation:
        """
        Run a single step of the manager's control logic.

        Args:
            k: Time step index
            members: List of energy community members
            pv: PV plant instance

        Returns:
            Recommendation: Generated recommendation for this time step

        Example:
            >>> recommendation = manager.step(0, members, pv_plant)
        """
        pass


class BasicManager(Manager):
    """
    Basic implementation of an energy system manager.

    This manager implements a simple control strategy based on comparing
    total expected consumption with PV production. It recommends
    decreasing consumption when it exceeds production, and increasing
    consumption otherwise.
    """

    def __init__(self, time_space_handler: TimeSpaceHandler,
                 recommendation_interval: list[int]):
        """
        Initialize a new basic manager.

        Args:
            time_space_handler: Handler for time and space operations
        """
        super().__init__(time_space_handler, recommendation_interval)

    def step(self,
             k: int,
             members: list[Member],
             pv: PVPlant) -> Recommendation:
        """
        Run a single step of the basic manager's control logic.

        If the total expected consumption is greater than the production,
        the manager will recommend a decrease. Otherwise, the manager will
        recommend an increase.

        Args:
            k: Time step index
            members: List of energy community members
            pv: PV plant instance

        Returns:
            Recommendation: Generated recommendation for this time step

        Example:
            >>> recommendation = manager.step(0, members, pv_plant)
        """
        current_datetime = self.time_space_handler.get_datetime_from_k(k)

        if not self._should_recommend(current_datetime):
            new_recommendation = Recommendation(RecommendationType.NONE)
            self.recommendations[current_datetime] = new_recommendation
            return new_recommendation

        total_consumption = self._get_total_exp_consumption(
            members, current_datetime)
        production = pv.power_production_hourly[current_datetime]

        if total_consumption > 1.1 * production:
            new_recommendation = Recommendation(RecommendationType.DECREASE)
            self.recommendations[current_datetime] = new_recommendation
        elif total_consumption < 0.9 * production:
            new_recommendation = Recommendation(RecommendationType.INCREASE)
            self.recommendations[current_datetime] = new_recommendation
        else:
            new_recommendation = Recommendation(RecommendationType.NONE)
            self.recommendations[current_datetime] = new_recommendation

        return new_recommendation

    def _should_recommend(self, current_datetime: datetime) -> bool:
        """
        Check if the manager should recommend an action based
        on the indication interval.

        Args:
            current_datetime: Current timestamp

        Returns:
            bool: True if the manager should recommend an action,
            False otherwise.
        """
        if (current_datetime.hour < self.recommendation_interval[0] or
                current_datetime.hour > self.recommendation_interval[1]):
            return False
        return True

    def _get_total_exp_consumption(self, members: list[Member],
                                   current_datetime: datetime) -> float:
        """
        Calculate the total expected consumption of all members.

        Args:
            members: List of energy community members
            current_datetime: Current timestamp

        Returns:
            float: Total expected consumption in kW

        Example:
            >>> total = manager._get_total_exp_consumption(members, dt)
        """
        return sum(member.exp_consumption[current_datetime]
                   for member in members)
