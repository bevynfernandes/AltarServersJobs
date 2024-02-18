import json

# from adaptiveui import ui
from tkinter import messagebox

from import_o import ask, get_attribute, objects

height_dict = {
    1: objects.Height.VERY_SHORT,
    2: objects.Height.SHORT,
    3: objects.Height.MEDIUM,
    4: objects.Height.TALL,
}

stamina_dict = {
    1: objects.Stamina.LOW,
    2: objects.Stamina.MEDIUM,
    3: objects.Stamina.HIGH,
}


def read(file: str) -> list[objects.Job]:
    with open(file, "r") as f:
        return [objects.Job.from_json(job) for job in json.load(f)]


def write(file: str, jobs: list[objects.Job]):
    """
    Write a list of jobs to a JSON file.

    Args:
        file (str): The path to the output file.
        jobs (list[objects.Job]): The list of jobs to write.

    Returns:
        None
    """
    with open(file, "w") as f:
        json.dump([job.to_json() for job in jobs], f, indent=4)


def create_job():
    """
    Creates a new job object based on user input.

    Returns:
        objects.Job: The created job object.
    """
    print("\n")
    name = input("Job Name: ").strip()

    height = get_attribute("Job", "Min Height", height_dict)
    stamina = get_attribute("Job", "Min Stamina", stamina_dict)
    senior = ask("Senior Required?")
    younger = False if senior else ask("Younger Required?")
    requires_pair = ask("Pair Required?")
    if younger:
        older = False
    elif senior:
        older = True
    else:
        older = ask("Older Required?")
    return objects.Job(name, height, stamina, senior, younger, older, requires_pair)


def create_job_gui():
    master = ui.UserInterface("Job Creator", (400, 300))
    window = master.frame

    # Create labels and entry fields
    name_label = ui.ttk.Label(window, text="Job Name:")
    name_entry = ui.ttk.Entry(window)
    height_label = ui.ttk.Label(window, text="Height (1-4):")
    height_entry = ui.ttk.Entry(window)
    stamina_label = ui.ttk.Label(window, text="Stamina (1-3):")
    stamina_entry = ui.ttk.Entry(window)

    # Define validation function for height
    def validate_height(input: str):
        if input.isdigit() and 1 <= int(input) <= 4:
            return True
        elif input == "":
            return True
        else:
            return False

    # Define validation function for stamina
    def validate_stamina(input: str):
        if input.isdigit() and 1 <= int(input) <= 3:
            return True
        elif input == "":
            return True
        else:
            return False

    # Register validation functions
    validate_height_cmd = window.register(validate_height)
    validate_stamina_cmd = window.register(validate_stamina)

    # Set validation options
    height_entry.config(validate="key", validatecommand=(validate_height_cmd, "%P"))
    stamina_entry.config(validate="key", validatecommand=(validate_stamina_cmd, "%P"))

    # Create checkboxes
    senior_var = ui.tk.IntVar()
    senior_check = ui.ttk.Checkbutton(window, text="Senior", variable=senior_var)
    senior_check.bind("<Return>", lambda e: senior_check.invoke())
    young_var = ui.tk.IntVar()
    young_check = ui.ttk.Checkbutton(window, text="Young", variable=young_var)
    young_check.bind("<Return>", lambda e: senior_check.invoke())
    older_var = ui.tk.IntVar()
    older_check = ui.ttk.Checkbutton(window, text="Older", variable=older_var)
    older_check.bind("<Return>", lambda e: senior_check.invoke())
    requires_pair_var = ui.tk.IntVar()
    requires_pair = ui.ttk.Checkbutton(window, text="Pair", variable=requires_pair_var)
    requires_pair.bind("<Return>", lambda e: senior_check.invoke())

    # Function to disable/enable checkbuttons
    def check_young():
        if young_var.get():
            older_check.config(state="disabled")
            senior_check.config(state="disabled")
        else:
            older_check.config(state="normal")
            senior_check.config(state="normal")

    def check_older():
        if older_var.get():
            young_check.config(state="disabled")
        else:
            young_check.config(state="normal")

    def check_senior():
        if senior_var.get():
            young_check.config(state="disabled")
        else:
            young_check.config(state="normal")

    young_check.config(command=check_young)
    older_check.config(command=check_older)
    senior_check.config(command=check_senior)

    # Function to create a new job
    def add_job():
        try:
            name = name_entry.get().strip()
            height = height_dict[int(height_entry.get())]
            stamina = stamina_dict[int(stamina_entry.get())]
            senior = bool(senior_var.get())
            young = bool(young_var.get())
            older = bool(older_var.get())
            server = objects.Job(
                name, height, stamina, senior, young, older, requires_pair
            )
            jobs.append(server)
            write("jobs.json", jobs)
            master.info(f"Job {name} added successfully.", "Job Added")
        except Exception as e:
            master.error(f"Error adding job: {e}", "Error")

    # Create add button
    add_button = ui.Tools.button("Add Job", add_job, window=window)

    # Grid layout with vertical spacing
    name_label.grid(row=0, column=0, pady=(0, 10), padx=6)
    name_entry.grid(row=0, column=1, pady=(0, 10), padx=6)
    height_label.grid(row=1, column=0, pady=(0, 10), padx=6)
    height_entry.grid(row=1, column=1, pady=(0, 10), padx=6)
    stamina_label.grid(row=2, column=0, pady=(0, 10), padx=6)
    stamina_entry.grid(row=2, column=1, pady=(0, 10), padx=6)
    senior_check.grid(row=3, column=0, pady=(0, 10))
    young_check.grid(row=3, column=1, pady=(0, 10))
    older_check.grid(row=4, column=0, pady=(0, 10))
    requires_pair.grid(row=4, column=1, pady=(0, 10))
    add_button.grid(row=5, column=0, columnspan=2, pady=(0, 10))

    master.mount_ui_rc_menu()
    master.run()


if __name__ == "__main__":
    jobs = read("jobs.json")
    # create_job_gui()
    try:
        njobs = [create_job() for _ in range(100)]
    except KeyboardInterrupt:
        print("\n\nSaving and Exiting...")
    write("jobs.json", jobs + njobs)
