import json
from math import ceil, sqrt
from random import shuffle
from statistics import fmean

from objects import Job, Server

MAX_JOBS = 2
MAX_JOBS_OVERRIDE = False
SHUFFLE = False

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

def read(file: str, object: Server | Job) -> list[Server | Job]:
    """
    Read data from a file and convert it into a list of Server or Job objects.

    Args:
        file (str): The path to the file to be read.
        object (Server | Job): The class representing the object type (Server or Job).

    Returns:
        list[Server | Job]: A list of Server or Job objects created from the data in the file.
    """
    with open(file) as f:
        data: list[dict[str, str | bool]] = json.load(f)

    return [object.from_json(object_item) for object_item in data]


def get_average_jobs(servers: list[Server], exclude: list[str] = None) -> float:
    """
    Calculate the average number of jobs being done by servers, excluding the specified servers.

    Args:
      servers (list[Server]): A list of Server objects representing the servers.
      exclude (list[str], optional): A list of server names to exclude from the calculation. Defaults to None.

    Returns:
      float: The average number of jobs being done by servers, excluding the specified servers.
    """
    if exclude is None:
        exclude = ()

    numbers = [server.jobs_doing for server in servers if not server.name in exclude]
    return fmean(numbers)


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

    def pair(self, store: bool = True):
        """
        Finds a pair of servers that are most similar based on their attributes.

        Args:
            store (bool, optional): Whether to store the pair of servers in the `pair_suggest` attribute. Defaults to True.

        Returns:
            tuple[Server] | list: The pair of servers if `store` is False, otherwise an empty list.
        """
        for list_name in ("min", "med", "max"):
            people = self._suggestions[list_name]
            min_distance = float("inf")
            most_similar = None

            for i in range(len(people)):
                for j in range(i + 1, len(people)):
                    person1, person2 = people[i], people[j]
                    distance = sqrt(
                        (person1.height.value - person2.height.value) ** 2
                        + (person1.stamina.value - person2.stamina.value) ** 2
                    )

                    if distance < min_distance:
                        min_distance = distance
                        most_similar = (person1, person2)

            if most_similar:
                if not store:
                    return most_similar
                self.suggested = most_similar

        if not store:
            return []
        for server in self.suggested:
            server.jobs_doing += 1

    def single(self):
        """
        Finds a single server from the suggestion lists.

        Returns:
            None
        """
        for list_name in ("min", "med", "max"):
            if self._suggestions[list_name]:
                self.suggested = (self._suggestions[list_name][0],)
                self._suggestions[list_name][0].jobs_doing += 1
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

def logic(servers: list[Server], job: Job) -> Suggestion:
    """
    Determines the best server suggestion for a given job based on various criteria.

    Args:
        servers (list[Server]): A list of Server objects representing available servers.
        job (Job): A Job object representing the job to be assigned.

    Returns:
        Suggestion: A Suggestion object containing the suggested server(s) for the job.

    """
    suggest = Suggestion(job.name)
    
    if SHUFFLE:
        shuffle(servers)

    # Prioritize servers that are not currently doing any jobs
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
            job.younger_required
            and server.is_young
            or job.senior_required
            and server.is_senior
            or job.older_required
            and server.is_older
        ):
            suggest.move_server(server, "min", "med", "Meets age requirement")
        if server.jobs_doing >= MAX_JOBS:
            suggest.remove_server(server, f"Doing more than {MAX_JOBS} jobs")

    if job.requires_pair:
        suggest.pair()
    else:
        suggest.single()

    return suggest

def main():
    """
    This is the main function that performs the job allocation logic for altar servers.

    It reads server and job data from JSON files, calculates the maximum number of jobs per person,
    assigns jobs to servers, and checks for servers that are not assigned any jobs.

    Returns:
        calc_jobs (list[Suggestion]): A list of suggestions containing the assigned jobs for each job.
        not_doing (int): The number of servers that are not assigned any jobs.
    """
    global MAX_JOBS
    servers: list[Server] = read("servers.json", Server)
    jobs: list[Job] = read("jobs.json", Job)

    mprint(f"{len(servers)=}, {len(jobs)=}")
    mjobs = len(servers) / len(jobs)
    if not MAX_JOBS_OVERRIDE:
        MAX_JOBS = ceil(mjobs)
        if MAX_JOBS == 0:
            MAX_JOBS = 1
    mprint(f"Set MAX_JOBS (per person) to {MAX_JOBS}.")

    mprint()
    calc_jobs: list[Suggestion] = []
    for job in jobs:
        dprint(f"\nProcessing Job: {job.name}...")
        calc_jobs.append(logic(servers, job))
        mprint(
            f"{job.name}: {" & ".join([server.name for server in calc_jobs[-1].suggested])}"
        )

    mprint()
    not_doing = 0
    for server in servers:
        if server.jobs_doing == 0:
            not_doing += 1
            mprint(f"WARNING: {server.name} is not doing any jobs!")
    return calc_jobs, not_doing

def find_complete():
    global MPRINT
    global SHUFFLE
    MPRINT = False
    SHUFFLE = True
    
    found = False
    while not found:
        calc_jobs, not_doing = main()
        if not_doing == 0:
            found = True
        else:
            print(f"{not_doing} server{"s" if not_doing > 1 else ""} not doing any jobs. Trying again...")
    
    print("Compelete Allocation Found!\n")
    for job in calc_jobs:
        print(f"{job.job_name}: {" & ".join([server.name for server in job.suggested])}")
    

if __name__ == "__main__":
    find_complete()
    #main()
