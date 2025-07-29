"""
Performance indicators for renewable energy systems.

This module provides functions to calculate key performance indicators (KPIs)
for renewable energy systems, particularly focusing on self-consumption and
self-sufficiency metrics.
"""

from datetime import datetime

from batem.reno.simulation.recommendation import (
    Recommendation, RecommendationType)


def self_consumption(load_by_time: dict[datetime, float],
                     production_by_time: dict[datetime, float]) -> float:
    """
    Calculate the self-consumption ratio of a house.

    The self-consumption ratio represents the proportion of locally produced
    energy that is consumed on-site. It is calculated as the ratio between
    the energy consumed from local production and the total energy produced.

    Args:
        load_by_time: Dictionary mapping timestamps to load values (kWh)
        production_by_time: Dictionary mapping timestamps to production values
            (kWh)

    Returns:
        float: Self-consumption ratio between 0 and 1

    Raises:
        ValueError: If input dictionaries have different lengths
        ValueError: If production_by_time is empty

    Example:
        >>> load = {datetime(2023, 1, 1, 12): 2.0}
        >>> prod = {datetime(2023, 1, 1, 12): 3.0}
        >>> self_consumption(load, prod)
        0.6666666666666666
    """
    if len(load_by_time) != len(production_by_time):
        msg = (f"load_by_time and production_by_time must have the same length"
               f" {len(load_by_time)} != {len(production_by_time)}")
        raise ValueError(msg)

    if len(production_by_time) == 0:
        print("warning: production_by_time is empty")
        return 0

    self_consumption = 0
    total_production = sum(production_by_time.values())
    for timestamp, load in load_by_time.items():
        self_consumption += min(load, production_by_time[timestamp])

    return self_consumption / total_production


def self_sufficiency(load_by_time: dict[datetime, float],
                     production_by_time: dict[datetime, float]) -> float:
    """
    Calculate the self-sufficiency ratio of a house.

    The self-sufficiency ratio represents the proportion of energy demand
    that is met by local production. It is calculated as the ratio between
    the energy consumed from local production and the total energy demand.

    Args:
        load_by_time: Dictionary mapping timestamps to load values (kWh)
        production_by_time: Dictionary mapping timestamps to production values
            (kWh)

    Returns:
        float: Self-sufficiency ratio between 0 and 1

    Raises:
        ValueError: If input dictionaries have different lengths
        ValueError: If production_by_time is empty
        ValueError: If load_by_time is empty

    Example:
        >>> load = {datetime(2023, 1, 1, 12): 2.0}
        >>> prod = {datetime(2023, 1, 1, 12): 3.0}
        >>> self_sufficiency(load, prod)
        1.0
    """
    if len(load_by_time) != len(production_by_time):
        msg = (f"load_by_time and production_by_time must have the same length"
               f" {len(load_by_time)} != {len(production_by_time)}")
        raise ValueError(msg)

    if len(production_by_time) == 0:
        print("warning: production_by_time is empty")
        return 0

    if len(load_by_time) == 0:
        print("warning: load_by_time is empty")
        return 0

    self_consumption = 0
    total_consumption = sum(load_by_time.values())
    for timestamp, load in load_by_time.items():
        self_consumption += min(load, production_by_time[timestamp])

    return self_consumption / total_consumption


def demanded_contribution(
        recommendations_by_time: dict[datetime, Recommendation],
        recommendation_interval: list[int]) -> float:
    """
    Calculate the demanded contribution of a house.

    The demanded contribution is the ration between the number of
    recommendations different then None
    and the total number of recommendations,
    but only during the recommendation interval.
    """
    if len(recommendations_by_time) == 0:
        return 0

    ccr = 0
    valid_hours = 0
    for timestamp, recommendation in recommendations_by_time.items():
        if (timestamp.hour >= recommendation_interval[0] and
                timestamp.hour <= recommendation_interval[1]):
            valid_hours += 1
            if RecommendationType(recommendation) != RecommendationType.NONE:
                ccr += 1

    return ccr / valid_hours
