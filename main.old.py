import json
from math import floor, sqrt
from pprint import pformat
from statistics import fmean
from typing import List, Union

from objects import Job, Server

MAX_JOBS = 1


def read(file: str, object: Server | Job) -> list:
    with open(file) as f:
        data: list = json.load(f)

    return [object.from_json(server) for server in data]


def get_average_jobs(servers: list[Server], exclude: list[str] = None) -> float:
    if exclude is None:
        exclude = []

    numbers = []
    for server in servers:
        if not server.name in exclude:
            numbers.append(server.jobs_doing)
    return fmean(numbers)


class Suggestion:
    def __init__(self, job_name: str) -> None:
        self.job_name = job_name

        self.min_suggest = []  # Meets minimum requirements
        self.med_suggest = []  # Meets most requirements
        self.max_suggest = []  # Meets all requirements
        self.pair_suggest = []  # Pair of Servers

    def increase(self, server: Server, reason: str):
        try:
            self.min_suggest.remove(server)
            try:
                self.med_suggest.remove(server)
                self.max_suggest.append(server)
                print(f"Moved {server.name} from med_suggest to max_suggest: {reason}")
            except ValueError:
                self.med_suggest.append(server)
                print(f"Moved {server.name} from min_suggest to med_suggest: {reason}")
        except ValueError:
            self.min_suggest.append(server)
            print(f"Added {server.name} to min_suggest: {reason}")

    def decrease(self, server: Server, reason: str):
        try:
            self.min_suggest.remove(server)
            print(f"Removed {server.name} from min_suggest: {reason}")
        except ValueError:
            try:
                self.med_suggest.remove(server)
                self.min_suggest.append(server)
                print(f"Moved {server.name} from med_suggest to min_suggest: {reason}")
            except ValueError:
                self.max_suggest.remove(server)
                self.med_suggest.append(server)
                print(f"Moved {server.name} from max_suggest to med_suggest: {reason}")

    def contains(self, server: Server) -> str | bool:
        if server in self.min_suggest:
            return "min"
        elif server in self.med_suggest:
            return "med"
        elif server in self.max_suggest:
            return "max"
        else:
            return False

    def remove(self, server: Server, reason: str):
        try:
            self.min_suggest.remove(server)
            print(f"Removed {server.name} from min_suggest: {reason}")
        except ValueError:
            try:
                self.med_suggest.remove(server)
                print(f"Removed {server.name} from med_suggest: {reason}")
            except ValueError:
                try:
                    self.max_suggest.remove(server)
                    print(f"Removed {server.name} from max_suggest: {reason}")
                except ValueError:
                    pass

    def pair(self, quick: bool = False):
        """Use Euclidean distance to measure the similarity between two people.
        The pair with the smallest Euclidean distance between their height and stamina is considered the most similar.
        """
        for people in [
            self.min_suggest,
            self.med_suggest,
            self.max_suggest,
        ]:  # In order of most preferred list of Servers
            min_distance = float("inf")
            most_similar = None

            for i in range(len(people)):
                for j in range(i + 1, len(people)):
                    person1: Server = people[i]
                    person2: Server = people[j]

                    distance = sqrt(
                        (person1.height.value - person2.height.value) ** 2
                        + (person1.stamina.value - person2.stamina.value) ** 2
                    )

                    if distance < min_distance:
                        min_distance = distance
                        most_similar = (person1, person2)

            if most_similar:
                if quick:
                    return most_similar
                self.pair_suggest = most_similar

        if quick:
            return []
        for server in self.pair_suggest:
            server.jobs_doing += 1

    def pp_print(self) -> str:
        s = f"Job Name: {self.job_name}"
        s += f"\nmin_suggest={pformat(self.min_suggest)}"
        s += f"\nmed_suggest={pformat(self.med_suggest)}"
        s += f"\nmax_suggest={pformat(self.max_suggest)}"
        s += f"\npair_suggest={pformat(self.pair_suggest)}\n"
        return s


def write(file: str, servers: list[Server]):
    with open(file, "w") as f:
        json.dump([server.to_json() for server in servers], f)


def logic(servers: list[Server], job: Job) -> Suggestion:
    suggest = Suggestion(job.name)
    # avg_jobs = get_average_jobs(servers)

    for server in servers:
        # Increase Suggestion Level
        if (
            server.height.value >= job.min_height.value
            and server.stamina.value >= job.min_height.value
        ):
            suggest.increase(server, "Meets minimum requirements")
        if job.younger_required and server.is_young:
            suggest.increase(server, "Younger Required")
        if job.senior_required and server.is_senior:
            suggest.increase(server, "Senior Required")
        if job.older_required and server.is_older:
            suggest.increase(server, "Older Required")

        # if server.jobs_doing < avg_jobs:
        #    suggest.increase(server, "Doing less than average jobs")

        # Decrease Suggestion Level
        if job.younger_required and server.is_senior and suggest.contains(server):
            suggest.decrease(server, "Younger Required")
        if job.older_required and not server.is_older and suggest.contains(server):
            suggest.remove(server, "Older Required")
        if server.jobs_doing >= MAX_JOBS:
            suggest.remove(server, f"Doing more than {MAX_JOBS} jobs")

    suggest.pair()
    return suggest


def main():
    global MAX_JOBS
    servers = read("servers.json", Server)
    jobs = read("jobs.json", Job)

    print(f"{len(servers)=}, {len(jobs)=}")
    mjobs = len(servers) / len(jobs)
    MAX_JOBS = floor(mjobs) / 2
    print(f"Set MAX_JOBS to {MAX_JOBS}")

    if isinstance(mjobs, float):
        print("WARNING: 1 or more Servers will not have a job!")

    calc_jobs: list[Suggestion] = []
    for job in jobs:
        calc_jobs.append(logic(servers, job))
        print(calc_jobs[-1].pp_print())
    print(pformat(servers))


if __name__ == "__main__":
    main()
