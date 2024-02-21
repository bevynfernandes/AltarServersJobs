import json
from math import ceil, sqrt
from random import shuffle
from statistics import fmean

from objects import Job, Server

DEBUG = False
MPRINT = True

def dprint(*args, **kwargs):
    """
    Prints the given arguments if the DEBUG flag is set.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    if DEBUG:
        print(*args, **kwargs)

def mprint(*args, **kwargs):
    """
    Prints the given arguments if the MPRINT flag is set.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    if MPRINT:
        print(*args, **kwargs)

class Suggestion:
    """
    Represents a suggestion for a job.

    Attributes:
        job_name (str): The name of the job.
        _suggestions (dict[str, list[Server]]): A dictionary that stores the suggestions for different requirement levels.
        pair_suggest (tuple[Server]): A pair of suggested servers.
    """

    def __init__(self, job_name: str):
        self.job_name = job_name

        self._suggestions: dict[str, list[Server]] = {
            "min": [],  # Meets minimum requirements
            "med": [],  # Meets most requirements
            "max": [],  # Meets all requirements
        }
        self.suggested: tuple[Server] = ()  # Suggested Server(s)

    @staticmethod
    def calculate_distance(server1: Server, server2: Server) -> float:
        """
        Calculates the Euclidean distance between two servers based on their height and stamina values.

        Args:
            server1 (Server): The first server.
            server2 (Server): The second server.

        Returns:
            float: The Euclidean distance between the two servers.
        """
        return sqrt(
            (server1.height.value - server2.height.value) ** 2
            + (server1.stamina.value - server2.stamina.value) ** 2
        )

    def move_server(self, server: Server, from_list: str, to_list: str, reason: str):
        """
        Moves a server from one list to another.

        Args:
            server (Server): The server to be moved.
            from_list (str): The name of the list from which the server will be moved.
            to_list (str): The name of the list to which the server will be moved.
            reason (str): The reason for the server movement.
        """
        if server in self._suggestions[from_list]:
            self._suggestions[from_list].remove(server)
            self._suggestions[to_list].append(server)
            dprint(f"Moved {server.name} from {from_list} to {to_list}: {reason}")

    def add_server(self, server: Server, reason: str):
        """
        Adds a server to the minimum suggestion list.

        Args:
            server (Server): The server to be added.
            reason (str): The reason for adding the server.
        """
        if server not in self._suggestions["min"]:
            self._suggestions["min"].append(server)
            dprint(f"Added {server.name} to min_suggest: {reason}")

    def remove_server(self, server: Server, reason: str):
        """
        Removes a server from the suggestion lists.

        Args:
            server (Server): The server to be removed.
            reason (str): The reason for removing the server.
        """
        for list_name in ("min", "med", "max"):
            if server in self._suggestions[list_name]:
                self._suggestions[list_name].remove(server)
                dprint(f"Removed {server.name} from {list_name}: {reason}")
                break

    def contains(self, server: Server) -> str | bool:
        """
        Checks if a server is present in any of the suggestion lists.

        Args:
            server (Server): The server to be checked.

        Returns:
            str | bool: The name of the list in which the server is present, or False if not found.
        """
        for list_name in self._suggestions:
            if server in self._suggestions[list_name]:
                return list_name
        return False

    def pair(self, servers: list[Server], previous_pairs: list[tuple[Server]], remove_previous: int = 2, store: bool = True):
        """
        Pair servers for a job based on suggestions and previous pairs.

        Args:
            servers (list[Server]): List of servers available for pairing.
            previous_pairs (list[tuple[Server]]): List of previous pairs to avoid repeating.
            remove_previous (int, optional): Number of previous pairs to remove from consideration. Defaults to 2.
            store (bool, optional): Flag to indicate whether to store the suggested pair. Defaults to True.

        Returns:
            list[Server] or None: List of suggested servers for the job, or None if store is False.

        Raises:
            ValueError: If no pair is found for the job.
        """
        total = sum(len(servers) for servers in self._suggestions.values())
        if total < 2:  # Only one server in the suggestion
            server1 = self.single(False)
            min_distance = float("inf")
            most_similar = None

            for server2 in servers:
                if server2 == server1 or server2 in self.suggested:
                    continue

                distance = self.calculate_distance(server1, server2)

                if distance < min_distance:
                    min_distance = distance
                    most_similar = server2

            if most_similar:
                self.suggested = (server1, most_similar)
                most_similar.jobs_doing += 1
        else:
            for list_name in ("min", "med", "max"):
                servers = self._suggestions[list_name]
                min_distance = float("inf")
                most_similar = None

                for i in range(len(servers)):
                    for j in range(i + 1, len(servers)):
                        server1, server2 = servers[i], servers[j]
                        distance = self.calculate_distance(server1, server2)

                        if distance < min_distance and {server1, server2} not in previous_pairs[:remove_previous]:
                            min_distance = distance
                            most_similar = (server1, server2)
    
                if most_similar:
                    if not store:
                        return most_similar
                    self.suggested = most_similar
    
        if not store:
            return []
        for server in self.suggested:
            server.jobs_doing += 1
    
        if len(self.suggested) == 0:
            raise ValueError(f"No pair found for job: '{self.job_name}'!")

    def single(self, store: bool = True):
        """
        Retrieves a single suggestion from the available suggestions.

        Args:
            store (bool, optional): Indicates whether to store the suggestion or not. 
                If True, the suggestion will be stored in the 'suggested' attribute and 
                the 'jobs_doing' count of the suggestion will be incremented by 1. 
                If False, the suggestion will be returned without storing it.

        Returns:
            Suggestion: The retrieved suggestion if 'store' is False, otherwise None.

        """
        for list_name in ("min", "med", "max"):
            if self._suggestions[list_name]:
                if store:
                    self.suggested = (self._suggestions[list_name][0],)
                    self._suggestions[list_name][0].jobs_doing += 1
                else:
                    return self._suggestions[list_name][0]
                break

    def __str__(self) -> str:
        """
        Returns a string representation of the Suggestion object.

        Returns:
            str: The string representation of the Suggestion object.
        """
        s = f"Job Name: {self.job_name}"
        for list_name in self._suggestions:
            s += f"\n{list_name}_suggest={self._suggestions[list_name]}"
        s += f"\npair_suggest={self.suggested}\n"
        return s

class JobAllocator:
    def __init__(self, shuffle: bool = False, remove_previous_suggestions: int = 2, max_jobs_override: int = False):
        """
        Initialize the AltarServersJobs class.

        Args:
            shuffle (bool, optional): Whether to shuffle the servers list. Defaults to False.
            remove_previous_suggestions (int, optional): Number of previous suggestions to remove servers from. Defaults to 1.
            max_jobs_override (int, optional): Maximum number of jobs to override. Defaults to False.
        """
        self.max_jobs = 2
        self.max_jobs_override = max_jobs_override
        self.shuffle = shuffle
        self.remove_previous_suggestions = remove_previous_suggestions
        
        self.previous_suggestions: dict[str, list[tuple[Server]]] = {}
        self.previous_pairs: list[tuple[Server]] = []

        self.servers: list[Server] = self.read("servers.json", Server)
        self.jobs: list[Job] = self.read("jobs.json", Job)

    def read(self, file: str, object: Server | Job) -> list[Server | Job]:
        """
        Reads data from a file and returns a list of Server or Job objects.

        Args:
            file (str): The path to the file to be read.
            object (Server | Job): The class representing the object type.

        Returns:
            list[Server | Job]: A list of Server or Job objects.

        """
        with open(file) as f:
            data: list[dict[str, str | bool]] = json.load(f)

        return [object.from_json(object_item) for object_item in data]

    def get_average_jobs(self, servers: list[Server], exclude: list[str] = None) -> float:
        """
        Calculates the average number of jobs being done by the servers, excluding the ones specified in the 'exclude' list.

        Args:
            servers (list[Server]): A list of Server objects representing the servers.
            exclude (list[str], optional): A list of server names to exclude from the calculation. Defaults to None.

        Returns:
            float: The average number of jobs being done by the servers.

        """
        if exclude is None:
            exclude = ()

        numbers = [server.jobs_doing for server in servers if not server.name in exclude]
        return fmean(numbers)

    def _logic(self, servers: list[Server], job: Job) -> Suggestion:
        """
        Determines the best server suggestions for a given job based on various criteria.

        Args:
            servers (list[Server]): A list of Server objects representing available servers.
            job (Job): A Job object representing the job to be assigned.

        Returns:
            Suggestion: A Suggestion object containing the suggested servers for the job.

        """
        suggest = Suggestion(job.name)

        if self.shuffle:
            shuffle(servers)

        servers.sort(key=lambda server: server.jobs_doing)

        for server in servers:
            if server.jobs_doing == 0 and (not server.is_senior or job.senior_required):
                suggest.add_server(server, "Not doing any jobs and (not senior or senior required)")

        for server in servers:
            if (
                server.height.value >= job.min_height.value
                and server.stamina.value >= job.min_stamina.value
            ):
                suggest.add_server(server, "Meets minimum requirements")
            if (
                (job.younger_required == 1 and server.is_young)
                or (job.younger_required == 2 and server.is_young)
                or job.senior_required
                and server.is_senior
                or job.older_required
                and server.is_older
            ):
                suggest.move_server(server, "min", "med", "Meets age requirement")
            if job.younger_required == 1 and not server.is_young:
                suggest.remove_server(server, "Not a younger server")
            if job.younger_required == 2 and server.is_senior:
                suggest.remove_server(server, "Not a younger server")
            if server.jobs_doing >= self.max_jobs and not (job.younger_required != 0 and server.is_young):
                suggest.remove_server(server, f"Doing more than {self.max_jobs} jobs")

        if self.remove_previous_suggestions:
            for prev_suggestion in self.previous_suggestions.get(job.name, ())[:(self.remove_previous_suggestions - 1)]:
                for server in prev_suggestion:
                    suggest.remove_server(server, "Previously suggested")

        if job.requires_pair:
            suggest.pair(servers, [set(pair) for pair in self.previous_pairs], self.remove_previous_suggestions)
            self.previous_pairs.append(suggest.suggested)
        else:
            suggest.single()

        if job.name not in self.previous_suggestions:
            self.previous_suggestions[job.name] = [suggest.suggested]
        else:
            self.previous_suggestions[job.name].append(suggest.suggested)

        return suggest

    def main(self):
        """
        Executes the main logic of the program.

        This method assigns jobs to servers based on the number of servers and jobs available.
        It calculates the maximum number of jobs per person and assigns jobs to servers accordingly.
        It also checks for servers that are not assigned any jobs and prints a warning message.

        Returns:
            tuple: A tuple containing the calculated jobs and the number of servers not doing any jobs.
        """
        for server in self.servers:
            server.jobs_doing = 0
        
        mprint(f"{len(self.servers)=}, {len(self.jobs)=}")
        mjobs = len(self.servers) / len(self.jobs)
        if not self.max_jobs_override:
            self.max_jobs = ceil(mjobs)
            if self.max_jobs == 0:
                self.max_jobs = 1
        mprint(f"Set MAX_JOBS (per person) to {self.max_jobs}.")

        mprint()
        self.calc_jobs: list[Suggestion] = []
        for job in self.jobs:
            dprint(f"\nProcessing Job: {job.name}...")
            self.calc_jobs.append(self._logic(self.servers, job))
            mprint(
                f"{job.name}: {" & ".join([server.name for server in self.calc_jobs[-1].suggested])}"
            )

        mprint()
        self.not_doing = 0
        for server in self.servers:
            if server.jobs_doing == 0:
                self.not_doing += 1
                mprint(f"WARNING: {server.name} is not doing any jobs!")
        return self.calc_jobs, self.not_doing

    def find_complete(self):
        """
        Finds a complete allocation of jobs to servers.

        This method iteratively calls the `main` method to calculate job allocations
        until all servers are doing jobs. It prints the progress and final allocation
        to the console.

        """
        global MPRINT
        MPRINT = False
        self.shuffle = True

        found = False
        while not found:
            calc_jobs, not_doing = self.main()
            if not_doing == 0:
                found = True
            else:
                print(f"{not_doing} server{'s' if not_doing > 1 else ''} not doing any jobs. Trying again...")

        print()
        for job in calc_jobs:
            print(f"{job.job_name}: {' & '.join([server.name for server in job.suggested])}")

if __name__ == "__main__":
    allocator = JobAllocator()
    for _ in range(5):
        allocator.find_complete()
