"""
GitHub activity scraper (date range)
Collects issues, sub-issues, PRs and commits for a repository within a date range,
saves raw JSON responses to ./responses/, and generates a markdown report.
Follows the style and structure of the provided template.

@TODO: Make the responses directory have subdirectories per repo, as well as each issue have a dir to it with the content related to it.
@TODO: Not re-do requests every time, but incremental ones.
@TODO: GraphQL for /Projects content
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

# Execution Constants
SAVE_JSONS = False # Set to False to skip saving JSON responses
VERBOSE = False # Set to True to print detailed messages

# Environment variables
load_dotenv() # Load .env variables
OWNER = os.getenv("OWNER", "") # GitHub organization or user
REPOS = json.loads(os.getenv("REPOS", "{}")) # Example: {"org1": ["repo1", "repo2"], "org2": ["repo3"]}
TOKEN = os.getenv("GITHUB_CLASSIC_TOKEN") # Works only with the Classic GitHub API with repo scope (https://github.com/settings/tokens)
REPOS = {org: sorted(repos) for org, repos in sorted(REPOS.items())} # Sort repositories alphabetically within each organization
USER_MAP_ONLY = os.getenv("USER_MAP_ONLY", "false").lower() == "true"
USER_MAP = json.loads(os.getenv("USER_MAP", "{}")) # Example: {"Full Name": ["github_username1", "full_name_with_underscores"]}
HEADERS = {"Authorization": f"token {TOKEN}"} # GitHub API headers (add preview Accept headers when needed)

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

def search_issues_by_field(repo: str, field: str, since_str: str, until_str: str):
   """
   Helper to search issues by a field (created or updated) in a date range.
   Returns list of issue items (search result objects).

   :param repo: Repository name
   :param field: Field to filter by ("created" or "updated")
   :param since_str: Start date string (GitHub format)
   :param until_str: End date string (GitHub format)
   :return: List of issue items (dicts)
   """

   items = [] # Collected items
   per_page = 100 # Max items per page
   page = 1 # Start at page 1

   while True: # Loop through pages
      query = f"repo:{OWNER}/{repo}+type:issue+{field}:{since_str}..{until_str}" # Search query
      url = f"https://api.github.com/search/issues?q={query}&per_page={per_page}&page={page}" # Search URL

      response = requests.get(url, headers=HEADERS) # Make request
      response.raise_for_status() # Raise error if bad response

      data = response.json() # Parse JSON
      save_json(data, f"./responses/search_issues_{field}_{page}.json") if SAVE_JSONS else None # Save search page if enabled

      page_items = data.get("items", []) # Get items

      if not page_items: # If no items, we're done
         break # Exit loop

      items.extend(page_items) # Add to collected items

      if len(page_items) < per_page: # If fewer than per_page, last page
         break # Exit loop

      page += 1 # Next page
   
   return items # Return collected items

def fetch_issue(repo: str, issue_number: int):
   """
   Fetch details for a specific GitHub issue and save JSON.

   :param repo: Repository name
   :param issue_number: Issue number
   :return: JSON data of the issue
   """

   url = f"https://api.github.com/repos/{OWNER}/{repo}/issues/{issue_number}" # Issue URL
   response = requests.get(url, headers=HEADERS) # Make request
   response.raise_for_status() # Raise error if bad response

   data = response.json() # Parse JSON
   save_json(data, f"./responses/issue_{issue_number}.json") if SAVE_JSONS else None # Save issue data if enabled

   return data # Return issue data

def fetch_issues_in_date_range(repo: str, start: dt.datetime, end: dt.datetime):
   """
   Fetch all issues created OR updated in the date range.
   Saves search pages and returns unique issue numbers found.

   :param repo: Repository name
   :param start: Start datetime
   :param end: End datetime
   :return: List of detailed issue JSON objects
   """

   since_str = to_github_time_string(start) # Convert start to GitHub string
   until_str = to_github_time_string(end) # Convert end to GitHub string

   created_items = search_issues_by_field(repo, "created", since_str, until_str) # Search created issues
   updated_items = search_issues_by_field(repo, "updated", since_str, until_str) # Search updated issues

   numbers = {item["number"] for item in created_items + updated_items} # Unique issue numbers
   issues = [] # Detailed issues

   for num in sorted(numbers): # Fetch each issue
      issues.append(fetch_issue(repo, num)) # Fetch and add to list

   return issues # Return detailed issues

def fetch_sub_issues(repo: str, issue_number: int):
   """
   Fetch sub-issues tracked by an epic (trackedIssues via GraphQL), save responses,
   and fetch each sub-issue details as well.

   :param repo: Repository name
   :param issue_number: Epic issue number
   :return: List of detailed sub-issue JSON objects
   """

   url = "https://api.github.com/graphql" # GraphQL endpoint

   query = """
   query($owner:String!, $repo:String!, $num:Int!) {
      repository(owner:$owner, name:$repo) {
         issue(number:$num) {
            id
            title
            number
            trackedIssues(first:100) {
               nodes {
                  number
                  title
                  state
                  url
               }
            }
         }
      }
   }
   """

   variables = {"owner": OWNER, "repo": repo, "num": issue_number} # GraphQL variables
   response = requests.post(url, headers=HEADERS, json={"query": query, "variables": variables}) # Make request
   response.raise_for_status() # Raise error if bad response
   data = response.json() # Parse JSON
   save_json(data, f"./responses/sub_issues_{issue_number}.json") if SAVE_JSONS else None # Save sub-issues data if enabled

   nodes = data.get("data", {}).get("repository", {}).get("issue", {}).get("trackedIssues", {}).get("nodes", []) or [] # Get sub-issue nodes
   detailed = [] # Detailed sub-issues

   for n in nodes: # Iterate over sub-issue nodes
      si_num = n.get("number") # Get sub-issue number
      if si_num: # If valid number
         si_data = fetch_issue(repo, si_num) # Fetch detailed sub-issue
         detailed.append(si_data) # Add to list
   
   return detailed # Return detailed sub-issues

def fetch_prs_from_timeline(repo: str, issue_number: int):
   """
   Fetch timeline events for the issue and collect PRs that cross-reference it.
   Saves timeline JSON as well.

   :param repo: Repository name
   :param issue_number: Issue number
   :return: List of PR numbers that reference the issue
   """

   url = f"https://api.github.com/repos/{OWNER}/{repo}/issues/{issue_number}/timeline" # Timeline URL
   headers = {**HEADERS, "Accept": "application/vnd.github.mockingbird-preview"} # Add preview Accept header

   response = requests.get(url, headers=headers) # Make request
   response.raise_for_status() # Raise error if bad response
   data = response.json() # Parse JSON
   save_json(data, f"./responses/issue_{issue_number}_timeline.json") if SAVE_JSONS else None # Save timeline data if enabled

   prs = [] # Collected PR numbers
   for e in data: # Iterate over timeline events
      if e.get("event") == "cross-referenced" and "source" in e: # If cross-referenced event
         src = e["source"] # Get source
         if src.get("type") == "pull_request": # If source is a PR
            pr_num = src.get("issue", {}).get("number") # Get PR number
            if pr_num: # If valid number
               prs.append(pr_num) # Add to list
   
   return prs # Return PR numbers

def fetch_commits_from_pr(repo: str, pr_number: int):
   """
   Fetch commits associated with a PR and save JSON.

   :param repo: Repository name
   :param pr_number: PR number
   :return: List of commit objects with sha, msg, date, author, url
   """

   url = f"https://api.github.com/repos/{OWNER}/{repo}/pulls/{pr_number}/commits" # PR commits URL

   response = requests.get(url, headers=HEADERS) # Make request
   response.raise_for_status() # Raise error if bad response
   data = response.json() # Parse JSON
   save_json(data, f"./responses/pr_{pr_number}_commits.json") if SAVE_JSONS else None # Save PR commits data if enabled
   commits = [] # Collected commits

   for commit in data: # Iterate over commits
      commit_obj = { # Extract relevant fields
         "sha": commit.get("sha"),
         "msg": commit.get("commit", {}).get("message", "")[:200],
         "date": commit.get("commit", {}).get("author", {}).get("date"),
         "author": commit.get("commit", {}).get("author", {}).get("name"),
         "url": commit.get("html_url")
      }
      commits.append(commit_obj) # Add to list
   
   return commits # Return commits

def fetch_prs_from_search(repo: str, issue_number: int):
   """
   Search PRs that mention the issue (in title/body). Saves search JSON pages.

   :param repo: Repository name
   :param issue_number: Issue number
   :return: List of PR numbers that mention the issue
   """

   prs = [] # Collected PR numbers
   per_page = 100 # Max items per page
   page = 1 # Start at page 1

   while True: # Loop through pages
      query = f"repo:{OWNER}/{repo}+type:pr+%23{issue_number}" # Search query (issue number with #)
      url = f"https://api.github.com/search/issues?q={query}&per_page={per_page}&page={page}" # Search URL

      response = requests.get(url, headers=HEADERS) # Make request
      response.raise_for_status() # Raise error if bad response
      data = response.json() # Parse JSON
      save_json(data, f"./responses/issue_{issue_number}_prs_search_page_{page}.json") if SAVE_JSONS else None # Save search page if enabled

      items = data.get("items", []) # Get items
      for item in items: # Iterate over items
         prs.append(item["number"]) # Add PR number to list

      if len(items) < per_page: # If fewer than per_page, last page
         break # Exit loop
      page += 1 # Next page

   return prs # Return PR numbers

def fetch_repo_commits_in_range(repo: str, start: dt.datetime, end: dt.datetime):
   """
   Fetch repository commits in a date range using the commits endpoint with since/until.
   Saves pages as separate files.

   :param repo: Repository name
   :param start: Start datetime
   :param end: End datetime
   :return: List of commit objects with sha, msg, date, author, url
   """

   since = to_github_time_string(start) # Convert start to GitHub string
   until = to_github_time_string(end) # Convert end to GitHub string
   per_page = 100 # Max items per page
   page = 1 # Start at page 1
   commits = [] # Collected commits

   while True: # Loop through pages
      url = f"https://api.github.com/repos/{OWNER}/{repo}/commits?since={since}&until={until}&per_page={per_page}&page={page}" # Commits URL
      response = requests.get(url, headers=HEADERS) # Make request
      response.raise_for_status() # Raise error if bad response
      data = response.json() # Parse JSON
      save_json(data, f"./responses/repo_commits_page_{page}.json") if SAVE_JSONS else None # Save commits page if enabled

      if not data: # If no data, we're done
         break # Exit loop

      for commit in data: # Iterate over commits
         commits.append({ # Extract relevant fields
            "sha": commit.get("sha"),
            "msg": commit.get("commit", {}).get("message", "")[:200],
            "date": commit.get("commit", {}).get("author", {}).get("date"),
            "author": commit.get("commit", {}).get("author", {}).get("name"),
            "url": commit.get("html_url")
         })

      if len(data) < per_page: # If fewer than per_page, last page
         break # Exit loop

      page += 1 # Next page
   
   return commits # Return commits

def fetch_commits_search(repo: str, issue_number: int, start: dt.datetime, end: dt.datetime):
   """
   Fetch commits in the repo within the date range and filter those that
   mention the issue number in the commit message. Works with private repos.

   :param repo: Repository name
   :param issue_number: Issue number to filter by
   :param start: Start datetime
   :param end: End datetime
   :return: List of commit objects with sha, msg, date, author, url
   """

   all_commits = fetch_repo_commits_in_range(repo, start, end) # Get all commits in date range

   commits = [ # Filter commits that mention the issue number
      commit for commit in all_commits # Iterate over all commits
      if f"#{issue_number}" in (commit.get("msg") or "") # Verify if issue number is in message
   ]

   save_json(commits, f"./responses/issue_{issue_number}_commits_filtered.json") if SAVE_JSONS else None # Save filtered commits if enabled

   return commits # Return filtered commits

def gather_activity_for_issue(repo: str, issue_json, start: dt.datetime, end: dt.datetime):
   """
   For a single issue JSON, gather:
   - sub-issues (trackedIssues)
   - PRs strictly linked via timeline
   - commits from PRs
   - commits via commit search
   Saves all JSON responses along the way.
   
   :param repo: Repository name
   :param issue_json: Issue JSON object
   :param start: Start datetime
   :param end: End datetime
   :return: Dict with issue, sub_issues, pr_numbers, commits
   """

   num = issue_json.get("number") # Issue number
   info = { # Collected info
      "issue": issue_json,
      "sub_issues": [],
      "pr_numbers": set(),
      "commits": []
   }

   sub_issues = fetch_sub_issues(repo, num) # Fetch sub-issues
   info["sub_issues"] = sub_issues # Store sub-issues

   timeline_prs = fetch_prs_from_timeline(repo, num) # Timeline PRs for main issue
   for prn in timeline_prs: # Iterate over PR numbers
      if prn not in info["pr_numbers"]: # If not already added
         info["pr_numbers"].add(prn) # Only add unique PR
         pr_commits = fetch_commits_from_pr(repo, prn) # Fetch commits from PR
         info["commits"].extend(pr_commits) # Add commits

   search_commits = fetch_commits_search(repo, num, start, end) # Commits mentioning the issue number
   info["commits"].extend(search_commits) # Add commits

   for si in sub_issues: # Repeat for each sub-issue
      si_num = si.get("number") # Sub-issue number
      if not si_num: continue # Skip invalid

      # PRs strictly linked in timeline for sub-issue
      timeline_prs = fetch_prs_from_timeline(repo, si_num)
      for prn in timeline_prs:
         if prn not in info["pr_numbers"]:
            info["pr_numbers"].add(prn)
            info["commits"].extend(fetch_commits_from_pr(repo, prn))

      info["commits"].extend(fetch_commits_search(repo, si_num, start, end)) # Commits mentioning sub-issue number

   return info # Return collected info

def get_full_name_from_username(username: str) -> str: 
   """
   Map a GitHub username to a full name using USER_MAP.

   :param username: GitHub username
   :return: Full name if found, else original username
   """

   for full_name, usernames in USER_MAP.items(): # Iterate over USER_MAP
      if username in usernames: # If username matches
         return full_name # Return full name
   return username # Fallback if not found

def get_author_name(obj):
   """
   Extract author name from issue or commit object.

   :param obj: Issue or commit JSON object
   :return: Author full name or "unknown"
   """

   if not obj: # If object is None or empty
      return "unknown"
   if "user" in obj: # If issue object
      return get_full_name_from_username(obj["user"].get("login") or "unknown") # Get username
   if "author" in obj: # If commit object
      return get_full_name_from_username(obj.get("author") or "unknown") # Get author name
   
   return "unknown" # Fallback

def dedupe_commits(commits_list):
   """
   Deduplicate commits by SHA (preserve first occurrence).

   :param commits_list: List of commit objects
   :return: Deduplicated list of commit objects
   """

   seen = set() # Seen SHAs
   deduped = [] # Deduplicated commits

   for commit in commits_list: # Iterate over commits
      sha = commit.get("sha") # Get SHA
      
      if not sha: # If no SHA (rare), stringify entire commit
         text = json.dumps(commit, sort_keys=True) # Stringify commit
         if text in seen: # If already seen, skip
            continue # Skip duplicate
         seen.add(text) # Add to seen
         deduped.append(commit) # Add to deduped
         continue # Continue to next commit

      if sha not in seen: # If SHA not seen
         seen.add(sha) # Add SHA to seen
         deduped.append(commit) # Add to deduped
      
   return deduped # Return deduplicated commits

def save_quarto_markdown_content(content: str, path: str):
   """
   Save markdown content to a .qmd file.

   :param content: Markdown content as string
   :param path: Full path to save the .qmd file
   :return: None
   """

   os.makedirs(os.path.dirname(path), exist_ok=True) # Ensure directory exists

   with open(path, "w", encoding="utf-8") as f: # Write content to file
      f.write(content) # Write content

   verbose_output(f"Saved Quarto markdown → {path}")

def render_quarto_report(input_file: str, output_formats=["pdf", "docx"]):
   """
   Render a Quarto markdown file to specified output formats using Quarto CLI.

   :param input_file: Path to the input .qmd file
   :param output_formats: List of output formats (e.g. ["pdf", "docx"])
   :return: None
   """

   if not shutil.which("quarto"): # Verify Quarto CLI is available
      print(f"{BackgroundColors.RED}Error: Quarto CLI not found. Please install Quarto to generate reports.{Style.RESET_ALL}")
      return

   for file_format in output_formats: # Iterate over formats
      cmd = ["quarto", "render", input_file, "--to", file_format] # Build command
      verbose_output(f"Running command: {' '.join(cmd)}") # Verbose output

      try: # Run the command
         result = subprocess.run(cmd, capture_output=True, text=True) # Run command
         if result.returncode != 0: # If error occurred
            print(f"{BackgroundColors.RED}Error: Quarto rendering failed ({file_format})\n{result.stderr}{Style.RESET_ALL}") # Print error
         else: # If successful
            verbose_output(f"{BackgroundColors.GREEN}Quarto rendering succeeded ({file_format}){Style.RESET_ALL}") # Success message
      except Exception as e: # On exception
         print(f"{BackgroundColors.RED}Error running Quarto ({file_format}): {e}{Style.RESET_ALL}")

def generate_quarto_report_per_author(start, end, issues_info, repo_commits, output_formats=["pdf", "docx"]):
   """
   Generate one Quarto markdown report per author, grouping issues and commits.
   Saves files like report_<author>.qmd

   :param start: Start datetime
   :param end: End datetime
   :param issues_info: List of issue info dicts (from gather_activity_for_issue)
   :param repo_commits: List of repo commit objects (from fetch_repo_commits_in_range)
   :param output_formats: List of output formats for Quarto (e.g. ["pdf", "docx"])
   :return: Dict mapping author to report content
   """

   start_s = start.strftime("%Y-%m-%d") # Format start date
   end_s = end.strftime("%Y-%m-%d") # Format end date

   author_data = {} # Data grouped by author

   for info in issues_info: # Iterate over issues
      issue_author = get_author_name(info["issue"]) # Get issue author
      author_data.setdefault(issue_author, {"issues": [], "commits": []}) # Initialize if not present
      author_data[issue_author]["issues"].append(info) # Add issue to author's list

      for commit in info.get("commits", []): # Iterate over commits linked to the issue
         if get_author_name(commit) == issue_author: # If commit author matches issue author
            author_data[issue_author]["commits"].append(commit) # Add commit to author's list

   for commit in repo_commits: # Iterate over standalone repo commits
      author = get_author_name(commit) # Get commit author
      author_data.setdefault(author, {"issues": [], "commits": []}) # Initialize if not present
      author_data[author]["commits"].append(commit) # Add commit to author's list

   reports = {} # Collected reports

   for author, data in author_data.items(): # Iterate over authors
      if USER_MAP_ONLY and author not in USER_MAP: # If filtering by USER_MAP_ONLY
         continue # Skip this author

      md = "" # Start of markdown content

      md += "---\n" # YAML front matter start
      md += f"title: \"Relatório de {OWNER}\"\n" # Title
      md += f"author: \"{author}\"\n" # Author
      md += f"date: {end_s}\n" # Only one valid date for Pandoc
      md += f"period: \"{start_s} → {end_s}\"\n" # Custom field
      md += "format:\n" # Output formats
      for fmt in output_formats: # Iterate over formats
         md += f"   {fmt}: default\n" # Default format
      md += "---\n\n" # YAML front matter end

      md += f"**Período:** {start_s} → {end_s}\n\n" # Date range

      md += "**Repositórios:** " + ", ".join([f"[{repo}](https://github.com/{OWNER}/{repo})" for org, repos in REPOS.items() for repo in repos]) + "\n\n" # Repositories with markdown links

      md += f"- Issues do autor: {len(data['issues'])}\n" # Number of issues
      md += f"- Commits do autor: {len(data['commits'])}\n\n" # Number of commits

      for info in data["issues"]: # Iterate over issues
         issue = info["issue"] # Issue object
         md += f"## Issue #{issue['number']}: [{issue.get('title','(no title)')}]({issue.get('html_url')})\n" # Issue header
         md += f"- Estado: {issue.get('state')}\n" # Issue state
         md += f"- Criado: {issue.get('created_at')}\n" # Created at
         md += f"- Atualizado: {issue.get('updated_at')}\n" # Updated at
         md += f"- URL: [{issue.get('html_url')}]({issue.get('html_url')})\n\n" # Issue URL

         if info.get("pr_numbers"): # If there are PRs
            md += "### PRs Relacionados\n" # PRs header
            repo_url = issue.get("repository_url", "") # Repository URL
            repo_name = repo_url.split("/")[-1] if repo_url else repo_url # Extract repo name
            for prn in sorted(info["pr_numbers"]): # Iterate over PR numbers
               md += f"- [PR #{prn}](https://github.com/{OWNER}/{repo_name}/pull/{prn})\n" # PR link
            md += "\n" # Newline

         commits = [c for c in dedupe_commits(info.get("commits", [])) if get_author_name(c) == author] # Commits by this author
         if commits: # If there are commits
            md += "### Commits relacionados a esta issue\n" # Commits header
            for commit in commits: # Iterate over commits
               sha = commit.get("sha", "")[:7] # Short SHA
               msg = (commit.get("msg") or "").splitlines()[0] # First line of message
               date = commit.get("date", "unknown") # Commit date
               url = commit.get("url", "") # Commit URL
               md += f"- `{sha}` {msg} ({date}) [{url}]({url})\n" # Commit line
            md += "\n" # Newline

      if data["commits"]: # If there are standalone commits
         md += "## Commits no intervalo (não necessariamente vinculados a issues)\n" # Commits header
         rc_dedup = dedupe_commits(data["commits"]) # Deduplicate commits
         for commit in rc_dedup: # Iterate over commits
            sha = commit.get("sha", "")[:7] # Short SHA
            msg = (commit.get("msg") or "").splitlines()[0] # First line of message
            date = commit.get("date", "unknown") # Commit date
            url = commit.get("url", "") # Commit URL
            md += f"- `{sha}` {msg} ({date}) [{url}]({url})\n" # Commit line
         md += "\n" # Newline

      reports[author] = md # Store report content

      safe_author = author.replace("/", "_").replace(" ", "_") # Safe filename
      reports_dir = f"./reports/{start_s}_{end_s}/{safe_author}/" # Reports directory
      os.makedirs(reports_dir, exist_ok=True) # Ensure directory exists
      filename = f"{safe_author}_{start_s}_{end_s}.qmd".replace(":", "-") # Filename
      save_quarto_markdown_content(md, os.path.join(reports_dir, filename)) # Save markdown

      render_quarto_report(os.path.join(reports_dir, filename), output_formats) if output_formats else None # Render report if formats specified

      verbose_output(f"Generated Quarto report for {author} → {os.path.join(reports_dir, filename)}")

   return reports # Return dict of reports

def verify_filepath_exists(filepath):
   """
   Verify if a file or folder exists at the specified path.

   :param filepath: Path to the file or folder
   :return: True if the file or folder exists, False otherwise
   """

   verbose_output(f"{BackgroundColors.GREEN}Verifying path: {BackgroundColors.CYAN}{filepath}{Style.RESET_ALL}")
   
   return os.path.exists(filepath) # Return if path exists

def play_sound():
   """
   Plays a sound when the program finishes (skips if Windows).

   :return: None
   """

   current_os = platform.system() # Get current OS

   if current_os == "Windows": # Skip sound on Windows
      return # Skip sound on Windows
   
   if verify_filepath_exists(SOUND_FILE): # Verify if sound file exists
      if current_os in SOUND_COMMANDS: # If OS is supported
         os.system(f"{SOUND_COMMANDS[current_os]} {SOUND_FILE}") # Play sound
      else: # If OS not supported
         print(f"{BackgroundColors.RED}OS {BackgroundColors.CYAN}{current_os}{BackgroundColors.RED} not in SOUND_COMMANDS.{Style.RESET_ALL}")
   else: # If sound file not found
      print(f"{BackgroundColors.RED}Sound file {BackgroundColors.CYAN}{SOUND_FILE}{BackgroundColors.RED} not found.{Style.RESET_ALL}")

def main():
   """
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
