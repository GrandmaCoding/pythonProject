from enum import Enum
from typing import Dict, Optional
from collections import deque
import time


class ZoneQueueException(Exception):
    """Base exception for ZoneQueue"""
    pass


class QueueFullException(ZoneQueueException):
    """Raised when attempting to add to a full queue"""
    pass


class InvalidZoneException(ZoneQueueException):
    """Raised when an invalid zone is specified"""
    pass


class InvalidItemException(ZoneQueueException):
    """Raised when invalid item data is provided"""
    pass


class ZoneType(Enum):
    RED = 3
    YELLOW = 2
    GREEN = 1


class ZoneQueue:
    def __init__(self,
                 red_timeout: int = 60,
                 yellow_timeout: int = 300,
                 green_timeout: int = 900,
                 max_zone_size: Dict[ZoneType, int] = None):

        self.red_timeout = red_timeout
        self.yellow_timeout = yellow_timeout
        self.green_timeout = green_timeout

        self.max_zone_size = max_zone_size or {
            ZoneType.RED: 100,
            ZoneType.YELLOW: 250,
            ZoneType.GREEN: 500
        }

        self.queues = {ZoneType.RED: deque(maxlen=self.max_zone_size[ZoneType.RED]),
                       ZoneType.YELLOW: deque(maxlen=self.max_zone_size[ZoneType.YELLOW]),
                       ZoneType.GREEN: deque(maxlen=self.max_zone_size[ZoneType.GREEN])
                       }

        self.health_status = {
            'expired_items': 0,
            'total_items': 0,
            'total_load_percentage': 0.0,
            'zones': {
                ZoneType.RED: {'avg_wait_time': 0.0, 'current_items': 0, 'items_processed': 0, 'load_percentage': 0.0},
                ZoneType.YELLOW: {'avg_wait_time': 0.0, 'current_items': 0, 'items_processed': 0,
                                  'load_percentage': 0.0},
                ZoneType.GREEN: {'avg_wait_time': 0.0, 'current_items': 0, 'items_processed': 0, 'load_percentage': 0.0}
            }
        }
        """
                Initialize queue zones and monitoring systems

                Parameters:
                -----------
                red_timeout: int
                    Timeout in milliseconds for RED zone items
                yellow_timeout: int
                    Timeout in milliseconds for YELLOW zone items
                green_timeout: int
                    Timeout in milliseconds for GREEN zone items
                max_zone_size: Dict[ZoneType, int]
                    Maximum size for each zone
                """

    def refresh_health_status(self, zone: ZoneType) -> None:
        zone_queue = self.queues[zone]
        current_load = len(zone_queue) / self.max_zone_size[zone] * 100

        self.health_status['zones'][zone]['current_items'] = len(zone_queue)
        self.health_status['zones'][zone]['load_percentage'] = current_load

        total_load_percentage = sum(len(self.queues[zone]) / self.max_zone_size[zone] *
                                    100 for zone in ZoneType) / len(ZoneType)
        self.health_status['total_load_percentage'] = total_load_percentage

    def enqueue(self, item: dict, zone: ZoneType) -> None:
        """
        Add item to specified zone
        """
        if not isinstance(zone, ZoneType):
            raise InvalidZoneException  # Не распознано название зоны

        if not isinstance(self.max_zone_size, dict):
            raise InvalidZoneException

        if len(self.queues[zone]) >= self.max_zone_size[zone]:
            raise QueueFullException

        if not isinstance(item, dict):
            raise InvalidItemException  # Невалидная структура процесса

        if ('id' not in item) or ('type' not in item) or ('data' not in item) or ('timestamp' not in item):
            raise InvalidItemException

        if ((not isinstance(item['id'], str)) or (item['type'] not in ['TRADE', 'RISK', 'REPORT']) or
                (not isinstance(item['data'], dict)) or (not isinstance(item['timestamp'], float))):
            raise InvalidItemException

        self.queues[zone].append(item)
        self.health_status['total_items'] += 1
        self.refresh_health_status(zone)

    def get_zone_timeout(self, zone: ZoneType) -> int:
        if zone == ZoneType.RED:
            return self.red_timeout
        elif zone == ZoneType.YELLOW:
            return self.yellow_timeout
        elif zone == ZoneType.GREEN:
            return self.green_timeout

    def dequeue(self) -> Optional[dict]:
        """
        Remove and return highest priority item

        Returns:
        --------
        dict or None
            Highest priority non-expired item, or None if queue is empty
        """
        for zone in sorted(ZoneType, key=lambda z: z.value, reverse=True):
            if self.queues[zone]:
                self.health_status['total_items'] -= 1
                self.health_status['zones'][zone]['items_processed'] += 1
                self.refresh_health_status(zone)
                return self.queues[zone].popleft()
        return None

    def get_health_status(self) -> dict:
        """
                    Return queue health metrics:
                    - Items per zone
                    - Average waiting time per zone
                    - Number of expired items
                    - Current load percentage per zone
                    """
        return self.health_status

    def cleanup_expired(self) -> list:
        """
        Remove and return list of expired items
        """
        expired_items = []
        current_time = time.time() * 1000

        for zone in ZoneType:
            while self.queues[zone]:
                item = self.queues[zone][0]
                if current_time - item['timestamp'] > self.get_zone_timeout(zone):
                    expired_items.append(self.queues[zone].popleft())
                    self.health_status['total_items'] -= 1
                    self.health_status['expired_items'] += 1
                    self.refresh_health_status(zone)
                else:
                    break

        return expired_items


# the second
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum


class DeveloperSpecialization(Enum):
    """Developer specializations in Decimal Precision"""
    CORE_ENGINE = "Trading Engine Developer"
    HFT = "High-Frequency Trading Engineer"
    DATA = "Data Engineer"
    REALTIME = "Real-time Analytics Engineer"
    INFRASTRUCTURE = "Infrastructure Engineer"


@dataclass
class Developer:
    """
    Represents a developer in the trading floor

    Attributes:
        name: Developer's full name
        specialization: Developer's primary expertise area
        years_experience: Years of development experience
        team_lead: Whether the developer is a team lead
    """
    name: str
    specialization: DeveloperSpecialization
    years_experience: int
    team_lead: bool = False

    def post_init(self):
        if self.years_experience < 0:
            raise ValueError("Years of experience cannot be negative")

class Node:
    def __init__(self, developer: Developer):
        self.developer = developer
        self.next = None
        self.prev = None


class CircularDeveloperList:
    """
    Circular doubly linked list for managing developer seating arrangements
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def add_developer(self, developer: Developer, position: Optional[int] = None) -> bool:
        """
        Add developer to the specified position (or end if position=None)

        Args:
            developer: Developer instance to add
            position: Position to insert. None for append

        Returns:
            bool: Success status

        Raises:
            ValueError: If position is invalid
        """
        new_node = Node(developer)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            if position is None or position >= self.size:
                self.tail.next = new_node
                new_node.prev = self.tail
                new_node.next = self.head
                self.head.prev = new_node
                self.tail = new_node
            else:
                if position < 0:
                    raise ValueError("Invalid position")
                current = self.head
                for _ in range(position):
                    current = current.next
                previous = current.prev
                previous.next = new_node
                new_node.prev = previous
                new_node.next = current
                current.prev = new_node
                if position == 0:
                    self.head = new_node
        self.size += 1
        return True

    def rotate_team(self, steps: int, section: Optional[Tuple[int, int]] = None) -> None:
        """
        Rotate developers by specified number of positions

        Args:
            steps: Number of positions to rotate
                  (positive - clockwise, negative - counterclockwise)
            section: Tuple of (start_pos, end_pos) for section rotation
                    None to rotate entire list

        Raises:
            ValueError: If section boundaries are invalid
        """
        if self.head is None:
            return


        if section is None:
                    steps = steps % self.size
                    if steps < 0:
                        steps += self.size
                    for _ in range(steps):
                        self.head = self.head.next
                        self.tail = self.tail.next
        else:
            start, end = section
            if start < 0 or end >= self.size or start >= end:
                raise ValueError("Invalid section boundaries")
            current = self.head
            for _ in range(start):
                current = current.next
            section_head = current
            section_tail = current
            for _ in range(end - start):
                section_tail = section_tail.next
            for _ in range(steps):
                section_head = section_head.next
                section_tail = section_tail.next

    def swap_teams(self, section1: Tuple[int, int], section2: Tuple[int, int]) -> None:
        """
        Swap two teams' positions

        Args:
            section1: (start, end) positions of first team
            section2: (start, end) positions of second team

        Raises:
            ValueError: If section boundaries overlap or are invalid
        """
        start1, end1 = section1
        start2, end2 = section2
        if start1 < 0 or end1 >= self.size or start2 < 0 or end2 >= self.size or \
                start1 > end1 or start2 > end2 or \
                (start1 <= end2 <= end1) or (start2 <= end1 <= end2):
            raise ValueError("Invalid section boundaries")

        section1_nodes = []
        section2_nodes = []

        current = self.head
        for i in range(self.size):
            if start1 <= i <= end1:
                section1_nodes.append(current)
            if start2 <= i <= end2:
                section2_nodes.append(current)
            current = current.next

        for node in section1_nodes:
            section2_nodes[0].prev.next = node
            node.prev = section2_nodes[0].prev
            node.next = section2_nodes[0]
            section2_nodes[0].prev = node

        for node in section2_nodes:
            section1_nodes[0].prev.next = node
            node.prev = section1_nodes[0].prev
            node.next = section1_nodes[0]
            section1_nodes[0].prev = node

    def group_by_specialization(self, spec: DeveloperSpecialization) -> None:
        """
        Reorganize list to group developers with specified specialization together
        Useful during incidents or releases

        Args:
            spec: Specialization to group together
        """
        if self.head is None:
            return

        current = self.head
        special_nodes = []
        other_nodes = []

        for _ in range(self.size):
            if current.developer.specialization == spec:
                special_nodes.append(current)
            else:
                other_nodes.append(current)
            current = current.next

        new_order = special_nodes + other_nodes
        self.head = new_order[0]
        self.tail = new_order[-1]

        for i in range(len(new_order)):
            new_order[i].next = new_order[(i + 1) % len(new_order)]
            new_order[i].prev = new_order[(i - 1) % len(new_order)]

    def validate_arrangement(self) -> bool:
        """
        Validate the current arrangement:
        - No two team leads should be adjacent
        - Each section should have at least one experienced developer

        Returns:
            bool: Whether the current arrangement is valid
        """
        if self.head is None:
            return True

        current = self.head
        for _ in range(self.size):
            if current.developer.team_lead and current.next.developer.team_lead:
                return False
            current = current.next

        experienced_developers = any(dev.years_experience >= 5 for dev in [node.developer for node in self._iter_nodes()])
        return experienced_developers

    def _iter_nodes(self):
        current = self.head
        for _ in range(self.size):
            yield current
            current = current.next
