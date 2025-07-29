"""
Scheduler for energy community simulation.

This module provides the main simulation scheduler that coordinates the
interaction between community members, PV production, and the energy
manager. It handles the step-by-step execution of the simulation and
exports the results.
"""

import csv
from typing import Any
from batem.reno.community.creation import CommunityBuilder
from batem.reno.community.model import EnergyCommunity
from batem.reno.simulation.manager.model import BasicManager
from batem.reno.simulation.member.model import Member
from batem.reno.simulation.scenario import Scenario
from batem.reno.utils import FilePathBuilder, TimeSpaceHandler, parse_args


class Scheduler:
    """
    Main scheduler for energy community simulation.

    This class coordinates the simulation of an energy community,
    managing the interaction between community members, PV production,
    and the energy manager. It executes the simulation step by step
    and handles result export.

    Attributes:
        community: Energy community being simulated
        scenario: Simulation scenario configuration
        steps: Total number of simulation steps (hours)
        k: Current simulation step
        manager: Energy system manager
        members: List of community members
    """

    def __init__(self, community: EnergyCommunity, scenario: Scenario):
        """
        Initialize the scheduler.

        The number of steps is determined by the number of hours in the
        simulation period, defined by the time space handler of the
        community.

        Args:
            community: Energy community to simulate
            scenario: Simulation scenario configuration

        Example:
            >>> scheduler = Scheduler(community, scenario)
        """
        self.community = community
        self.scenario = scenario
        self.steps = len(self.community.time_space_handler.range_hourly)
        self.k = 0

        self.manager = BasicManager(
            self.community.time_space_handler,
            self.scenario.indication_interval)

        self.members = self._create_members()

    def _create_members(self) -> list[Member]:
        """
        Create Member instances for all houses in the community.
        """
        members: list[Member] = []
        for house in self.community.houses:
            member = Member(
                self.community.time_space_handler,
                house)
            members.append(member)
        return members

    def run(self):
        """
        Run the complete simulation step by step.

        Each step represents one hour of simulation time. The simulation
        progresses through all steps, updating member states and
        generating recommendations. Results are exported to CSV and the
        scenario is saved to JSON at the end.

        Example:
            >>> scheduler.run()
        """
        ts_handler = self.community.time_space_handler
        for k in range(self.steps):
            timestamp = ts_handler.get_datetime_from_k(k)
            print(f"Step {k} ({timestamp}) of {self.steps}")
            self._step(k)

        self.to_csv()
        self.scenario.to_json()

    def _step(self, k: int):
        """
        Execute a single simulation step.

        For each step:
        1. Get recommendation from the manager
        2. Update each member's state based on the recommendation

        Args:
            k: Current simulation step index
        """
        recommendation = self.manager.step(
            k=k,
            members=self.members,
            pv=self.community.pv_plant)

        for member in self.members:
            member.step(k, recommendation)

    def to_csv(self):
        """
        Export simulation results to a CSV file.

        The CSV file contains the following columns:
        - timestamp: Simulation timestamp
        - exp_{house_id}: Expected consumption for each house
        - sim_{house_id}: Simulated consumption for each house
        - manager: Manager's recommendation
        - pv: PV production value

        The file is saved in the simulation results folder with a name
        based on the location and time range.
        """
        file_path = FilePathBuilder().get_simulation_results_path(
            self.community.time_space_handler)

        header = ["timestamp"]
        for member in self.members:
            header.append(f"exp_{member.house.house_id}")
            header.append(f"sim_{member.house.house_id}")

        header.append("manager")
        header.append("pv")

        with open(file_path, "w") as f:
            writer = csv.writer(f)

            writer.writerow(header)

            ts_handler = self.community.time_space_handler

            for k in range(self.steps):
                timestamp = ts_handler.get_datetime_from_k(k)

                result: dict[Any, Any] = {'timestamp': timestamp}

                for member in self.members:
                    h_id = member.house.house_id
                    result[f"exp_{h_id}"] = member.exp_consumption[timestamp]
                    result[f"sim_{h_id}"] = member.sim_consumption[timestamp]

                result["manager"] = (
                    self.manager.recommendations[timestamp].type.value)
                result["pv"] = (
                    self.community.pv_plant.power_production_hourly[timestamp])

                writer.writerow(result.values())


if __name__ == "__main__":
    # python batem/reno/simulation/scheduler/model.py

    args = parse_args()

    time_space_handler = TimeSpaceHandler(
        location=args.location,
        start_date=args.start_date,
        end_date=args.end_date)

    number_of_panels = 30
    peak_power_kW = 0.455
    exposure_deg = 0.0
    slope_deg = 152.0

    community = CommunityBuilder(time_space_handler
                                 ).build(
        panel_peak_power_kW=peak_power_kW,
        number_of_panels=number_of_panels,
        exposure_deg=exposure_deg,
        slope_deg=slope_deg,
        regerenate_consumption=False,
        exclude_houses=[2000926, 2000927, 2000928])

    scenario = Scenario(
        location=args.location,
        start_date=args.start_date,
        end_date=args.end_date,
        house_ids=[house.house_id for house in community.houses],
        pv_number_of_panels=number_of_panels,
        pv_panel_height_m=community.pv_plant.panel_height_m,
        pv_panel_width_m=community.pv_plant.panel_width_m,
        pv_exposure_deg=exposure_deg,
        pv_slope_deg=slope_deg,
        pv_peak_power_kW=peak_power_kW,
        pv_mount_type=community.pv_plant.mount_type,
        indication_interval=[7, 22]
    )

    Scheduler(community, scenario).run()
