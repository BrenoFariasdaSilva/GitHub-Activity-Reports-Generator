"""
GitHub activity scraper (date range)
Collects issues, sub-issues, PRs and commits for a repository within a date range,
saves raw JSON responses to ./responses/, and generates a markdown report.
Follows the style and structure of the provided template.
"""

# Library imports
import argparse # For CLI arguments
import datetime as dt # For date handling
import json # For handling JSON responses
import os # For running commands and file operations
import platform # For detecting the OS
import requests # For making HTTP requests
import shutil # For file operations
import subprocess # For running commands
from colorama import Style # For coloring terminal output
from dotenv import load_dotenv # For loading environment variables
from zoneinfo import ZoneInfo # For timezone handling

# Macros and constants
DEFAULT_START = "2020-01-01T00:00:00Z" # Start date (ISO format)
DEFAULT_END = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") # End date (now in UTC)

USER_MAP = { # Dictionary mapping full names to all possible usernames
   "John Doe": [
      "John_Doe", # John Doe name but with underscore instead of space
      "j_doe" # John Doe github username
   ],
}

load_dotenv() # Load .env variables
TOKEN = os.getenv("GITHUB_CLASSIC_TOKEN") # Works only with the Classic GitHub API with repo scope (https://github.com/settings/tokens)
OWNER = "ORG_NAME_HERE"  # Replace with the GitHub organization or username
REPOS = {
   "PROJECT_NAME_HERE": [  # Replace with your project/group name. Each project can have one or more repositories, like backend/frontend/etc.
      "REPO_BACKEND_NAME",  # Replace with the backend repo name, for example
      "REPO_FRONTEND_NAME"  # Replace with the frontend repo name, for example
   ]
} # List of repositories to process
REPOS = {org: sorted(repos) for org, repos in sorted(REPOS.items())} # Sort repositories alphabetically within each organization
HEADERS = {"Authorization": f"token {TOKEN}"} # GitHub API headers (add preview Accept headers when needed)
VERBOSE = False # Set to True to print detailed messages

class BackgroundColors: # For colored terminal output
   CYAN = "\033[96m"
   GREEN = "\033[92m"
   YELLOW = "\033[93m"
   RED = "\033[91m"
   BOLD = "\033[1m"
   UNDERLINE = "\033[4m"
   CLEAR_TERMINAL = "\033[H\033[J"

SOUND_COMMANDS = {"Darwin": "afplay", "Linux": "aplay", "Windows": "start"} # Sound play commands per OS
SOUND_FILE = "./.assets/Sounds/NotificationSound.wav" # Path to sound file
RUN_FUNCTIONS = {"Play Sound": True} # Toggle functions on/off

# Function definitions

def parse_date_input(s: str, default_time_start: bool = True) -> dt.datetime:
   """
   Parse a date string in various common forms and return a datetime
   localized to the São Paulo timezone (America/Sao_Paulo):

   - 'YYYY-MM-DD'
   - 'YYYY-MM-DDTHH:MM:SS'
   - full ISO with timezone (Z or hh:mm)

   :param s: Date string to parse
   :param default_time_start: If True and only date is given, use 00:00:00, else 23:59:59
   :return: Parsed datetime object in São Paulo timezone
   """

   if s is None: # If the string is empty or None
      raise ValueError("Date string is required")

   s = s.strip() # Trim whitespace
   tz_sp = ZoneInfo("America/Sao_Paulo") # São Paulo timezone

   try: # Try parsing the string
      if len(s) == 10 and s.count("-") == 2: # If only date part is given
         d = dt.datetime.strptime(s, "%Y-%m-%d") # Parse date
         if default_time_start: # If start of day
            return dt.datetime.combine(d.date(), dt.time.min, tzinfo=tz_sp) # 00:00:00
         else: # If end of day
            return dt.datetime.combine(d.date(), dt.time.max, tzinfo=tz_sp) # 23:59:59

      if s.endswith("Z"): # If ends with Z (UTC)
         s2 = s[:-1] + "+00:00" # Replace Z with +00:00
         d = dt.datetime.fromisoformat(s2) # Parse ISO
         return d.astimezone(tz_sp) # Convert UTC to São Paulo

      d = dt.datetime.fromisoformat(s) # Try parsing full ISO
      if d.tzinfo is None: # If no timezone info
         return d.replace(tzinfo=tz_sp) # Assume São Paulo
      else: # If has timezone info
         return d.astimezone(tz_sp) # Convert to São Paulo

   except Exception as e: # On error
      raise ValueError(f"Unable to parse date string '{s}': {e}")

def to_github_time_string(d: dt.datetime) -> str:
   """
   Convert datetime to GitHub/RFC3339 style string in São Paulo timezone:
   YYYY-MM-DDTHH:MM:SS-03:00

   :param d: datetime object (naive or with tzinfo)
   :return: Formatted string
   """

   tz_sp = ZoneInfo("America/Sao_Paulo") # São Paulo timezone

   if d.tzinfo is None: # If naive datetime
      d = d.replace(tzinfo=tz_sp) # Assume naive datetime -> localize to São Paulo
   else: # If has timezone info
      d = d.astimezone(tz_sp) # Convert to São Paulo

   return d.isoformat(timespec="seconds") # Return ISO string without microseconds

def verbose_output(true_string="", false_string=""):
   """
   Outputs a message if the VERBOSE constant is True.

   :param true_string: Message to show if VERBOSE is True
   :param false_string: Message to show if VERBOSE is False
   :return: None
   """
   
   if VERBOSE and true_string != "": # If VERBOSE is True and message is not empty
      print(true_string) # Print the message
   elif false_string != "": # If VERBOSE is False and message is not empty
      print(false_string) # Print the message

def save_json(obj, path: str):
   """
   Save Python object as JSON file.
   Converts sets into lists to avoid serialization errors.
   Creates the parent directory if it does not exist.

   :param obj: Python object to save (dict, list, etc.)
   :param path: Full path to save the file
   :return: None
   """

   def default_serializer(o): # Custom serializer for non-serializable objects
      if isinstance(o, set): # Convert sets to lists
         return list(o) # Convert set to list
      if isinstance(o, (dt.datetime, dt.date)): # Convert datetime/date to ISO string
         return o.isoformat() # Return ISO string
      raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable") # Raise error for unsupported types

   os.makedirs(os.path.dirname(path), exist_ok=True) # Ensure directory exists

   with open(path, "w", encoding="utf-8") as f: # Write JSON with indentation
      json.dump(obj, f, ensure_ascii=False, indent=3, default=default_serializer) # Custom serializer

   verbose_output(f"Saved JSON → {path}")

def main():
   """"
   Main function to parse arguments, fetch data, and generate reports.
   Arguments:
   --since: Start date (YYYY-MM-DD or ISO)
   --until: End date (YYYY-MM-DD or ISO)

   :param: None
   :return: None
   """

   print(f"{BackgroundColors.CLEAR_TERMINAL}{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}GitHub Activity Reports Generator{BackgroundColors.GREEN}.{Style.RESET_ALL}\n")

   parser = argparse.ArgumentParser(description="GitHub Activity Reports Generator (date range).") # Argument parser
   parser.add_argument("--since", type=str, help="Start date (YYYY-MM-DD or ISO).") # Start date argument
   parser.add_argument("--until", type=str, help="End date (YYYY-MM-DD or ISO).") # End date argument
   args = parser.parse_args() # Parse arguments

   if args.since: # If --since provided
      since_dt = parse_date_input(args.since, default_time_start=True) # Parse start date
   else: # If not provided, use default
      since_dt = parse_date_input(DEFAULT_START, default_time_start=True) # Default start date

   if args.until: # If --until provided
      until_dt = parse_date_input(args.until, default_time_start=False) # Parse end date
   else: # If not provided, use default
      until_dt = parse_date_input(DEFAULT_END, default_time_start=False) # Default end date

   print(f"{BackgroundColors.GREEN}Fetching data from {BackgroundColors.CYAN}{since_dt} {BackgroundColors.GREEN}to {BackgroundColors.CYAN}{until_dt}{BackgroundColors.GREEN} for repositories: {BackgroundColors.CYAN}{', '.join([f'{org}/{repo}' for org, repos in REPOS.items() for repo in repos])}.{Style.RESET_ALL}\n")

   all_issues_info = [] # Collected issue info
   all_repo_commits = [] # Collected repo commits

   for org, repos in REPOS.items(): # Iterate over organizations and their repositories
      for idx, repo in enumerate(repos, start=1): # Enumerate repos per org
         print(f"{BackgroundColors.GREEN}Processing repository {BackgroundColors.CYAN}{idx}. https://github.com/{OWNER}/{repo}{BackgroundColors.GREEN}...{Style.RESET_ALL}")

         issues = fetch_issues_in_date_range(repo, since_dt, until_dt) # 1 - Fetch issues in date range

         for issue in issues: # 2 - Gather activity from each issue
            info = gather_activity_for_issue(repo, issue, since_dt, until_dt) # Gather activity
            all_issues_info.append(info) # Add to collected info

         repo_commits = fetch_repo_commits_in_range(repo, since_dt, until_dt) # 3 - Fetch repo commits in date range
         all_repo_commits.extend(repo_commits) # Add to collected commits

   generate_quarto_report_per_author(since_dt, until_dt, all_issues_info, all_repo_commits, output_formats=["pdf", "docx"]) # 4 - Generate Quarto reports
   
   print(f"{BackgroundColors.GREEN}Processing complete!{Style.RESET_ALL}\n")

   play_sound() if RUN_FUNCTIONS.get("Play Sound") else None

if __name__ == "__main__":
   """
   Standard boilerplate to call main().

   """

   main()
