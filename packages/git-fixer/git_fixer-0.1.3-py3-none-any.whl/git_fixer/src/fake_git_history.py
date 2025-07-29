#!/usr/bin/env python3
"""
fake-git-history - Generate fake git commits to create GitHub activity graphs

This tool creates a git repository with commits dated strategically to make
it appear as if you've been coding regularly.
"""

import argparse
import os
import random
import subprocess
import sys
import json
import getpass
from pathlib import Path
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Tuple, Optional, Union, Any


class GitHistoryGenerator:
    """
    Class to generate fake git commit history.
    """
    
    def __init__(self, 
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 frequency: int = 80,
                 distribution: str = "uniform",
                 min_commits: int = 0,
                 max_commits: int = 4,
                 output_dir: str = "my-history",
                 github_username: Optional[str] = None,
                 github_token: Optional[str] = None,
                 auto_push: bool = False,
                 repo_private: bool = True):
        """
        Initialize the GitHistoryGenerator.
        
        Args:
            start_date: Start date for generating commits (default: 365 days ago)
            end_date: End date for generating commits (default: today)
            frequency: Percentage chance (0-100) of generating commits for each day
            distribution: Distribution pattern for commits ('uniform', 'workHours', or 'afterWork')
            min_commits: Minimum number of commits per day
            max_commits: Maximum number of commits per day
            output_dir: Output directory name
            github_username: GitHub username for remote repository
            github_token: GitHub personal access token for authentication
            auto_push: Whether to automatically push to GitHub after creating commits
            repo_private: Whether the GitHub repository should be private
        """
        # Set default dates if not provided
        today = datetime.now()
        self.start_date = start_date if start_date else today - timedelta(days=365)
        self.end_date = end_date if end_date else today
        
        # Validate dates
        if self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        
        # Validate frequency
        if frequency < 0 or frequency > 100:
            raise ValueError("Frequency must be between 0 and 100")
        self.frequency = frequency
        
        # Validate distribution
        valid_distributions = ["uniform", "workHours", "afterWork"]
        if distribution not in valid_distributions:
            raise ValueError(f"Distribution must be one of: {', '.join(valid_distributions)}")
        self.distribution = distribution
        
        # Validate commit range
        if min_commits < 0 or max_commits < min_commits:
            raise ValueError("min_commits must be >= 0 and max_commits must be >= min_commits")
        self.min_commits = min_commits
        self.max_commits = max_commits
        
        # Set output directory
        self.output_dir = output_dir
        
        # GitHub credentials
        self.github_username = github_username
        self.github_token = github_token
        self.auto_push = auto_push
        self.repo_private = repo_private
        
        # Initialize commit plan
        self.commit_plan = {}
        
    def get_commit_count(self, date: datetime) -> int:
        """
        Determine how many commits to create for a given date based on distribution.
        
        Args:
            date: The date to calculate commit count for
            
        Returns:
            Number of commits to create
        """
        # Check if we should skip this day based on frequency
        if random.randint(1, 100) > self.frequency:
            return 0
        
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        hour = date.hour
        
        # Adjust probability based on distribution pattern
        if self.distribution == "workHours":
            # Favor weekdays (especially Tue-Thu) during work hours
            if weekday >= 5:  # Weekend
                chance_multiplier = 0.3
            elif weekday in [1, 2, 3]:  # Tue-Thu
                chance_multiplier = 1.5
            else:  # Mon, Fri
                chance_multiplier = 1.0
                
            # Favor work hours (9am-5pm)
            if 9 <= hour <= 17:
                chance_multiplier *= 1.5
            else:
                chance_multiplier *= 0.6
        
        elif self.distribution == "afterWork":
            # Favor weekends and evenings
            if weekday >= 5:  # Weekend
                chance_multiplier = 2.0
            elif weekday == 4:  # Friday
                chance_multiplier = 1.3
            else:  # Mon-Thu
                chance_multiplier = 0.7
                
            # Favor evening hours (6pm-11pm)
            if 18 <= hour <= 23:
                chance_multiplier *= 1.5
            elif hour < 9:  # Early morning
                chance_multiplier *= 0.4
            else:
                chance_multiplier *= 0.8
        
        else:  # uniform distribution
            chance_multiplier = 1.0
        
        # Base number of commits from the min-max range
        base_commits = random.randint(self.min_commits, self.max_commits)
        
        # Apply the multiplier and ensure we stay within bounds
        adjusted_commits = round(base_commits * chance_multiplier)
        return max(self.min_commits, min(adjusted_commits, self.max_commits))

    def generate_commit_plan(self) -> Dict[datetime, int]:
        """
        Generate a plan of how many commits to make on each day.
        
        Returns:
            Dictionary mapping datetime objects to number of commits
        """
        current_date = self.start_date
        commit_plan = {}
        
        while current_date <= self.end_date:
            # For each day, decide how many commits to make for each hour
            for hour in range(24):
                date_with_hour = current_date.replace(hour=hour, minute=random.randint(0, 59))
                commits = self.get_commit_count(date_with_hour)
                
                if commits > 0:
                    commit_plan[date_with_hour] = commits
            
            current_date += timedelta(days=1)
        
        self.commit_plan = commit_plan
        return commit_plan
    
    def get_preview_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the commit plan.
        
        Returns:
            Dictionary with stats about the commits
        """
        if not self.commit_plan:
            self.generate_commit_plan()
            
        # Group commits by day for the preview
        days = {}
        for date, count in self.commit_plan.items():
            day = date.date()
            days[day] = days.get(day, 0) + count
        
        # Calculate stats
        stats = {
            'total_commits': sum(days.values()),
            'active_days': len(days),
            'date_range': (self.start_date.date(), self.end_date.date()),
            'daily_commits': days
        }
        
        return stats
    
    def print_preview(self) -> None:
        """Print an ASCII preview of the commit activity."""
        if not self.commit_plan:
            self.generate_commit_plan()
            
        if not self.commit_plan:
            print("No commits planned based on current settings.")
            return
        
        # Group commits by day for the preview
        days = {}
        for date, count in self.commit_plan.items():
            day = date.date()
            days[day] = days.get(day, 0) + count
        
        # Get the date range
        dates = sorted(days.keys())
        if not dates:
            return
        
        start_date = dates[0]
        end_date = dates[-1]
        
        # Find the first Monday to align the calendar
        current = start_date
        while current.weekday() != 0:  # 0 is Monday
            current -= timedelta(days=1)
        
        # Print headers
        print("\nActivity Preview:")
        print("  " + " ".join("MTWTFSS"))
        
        # Print the calendar with activity levels
        while current <= end_date:
            if current.weekday() == 0:  # Start of week (Monday)
                sys.stdout.write(f"{current.month:2d} ")
            
            if current < start_date or current > end_date or current not in days:
                sys.stdout.write("·")
            else:
                commit_count = days[current]
                if commit_count == 0:
                    sys.stdout.write("·")
                elif commit_count <= 2:
                    sys.stdout.write("▪")  # Light activity
                elif commit_count <= 5:
                    sys.stdout.write("▪")  # Medium activity
                else:
                    sys.stdout.write("▪")  # Heavy activity
            
            if current.weekday() == 6:  # End of week (Sunday)
                sys.stdout.write("\n")
            else:
                sys.stdout.write(" ")
            
            current += timedelta(days=1)
        
        print("\nTotal commits planned:", sum(days.values()))
        print("Across", len(days), "days")
        print(f"Date range: {start_date} to {end_date}")
    
    def create_git_repo(self, show_progress: bool = True) -> bool:
        """
        Create a git repository with the planned commits.
        
        Args:
            show_progress: Whether to show progress information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.commit_plan:
            self.generate_commit_plan()
            
        output_dir = self.output_dir
        if os.path.exists(output_dir):
            if show_progress:
                print(f"Error: Output directory '{output_dir}' already exists.")
            return False
        
        # Create the directory and initialize git repo
        os.makedirs(output_dir)
        os.chdir(output_dir)
        subprocess.run(["git", "init"], check=True, stdout=subprocess.DEVNULL if not show_progress else None)
        
        # Create a README file
        with open("README.md", "w") as f:
            f.write("# My Commit History\n\nThis repository was generated with fake-git-history.\n")
        
        # Initial commit
        subprocess.run(["git", "add", "README.md"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, 
                      stdout=subprocess.DEVNULL if not show_progress else None)
        
        # Create the commits according to the plan
        total_commits = sum(self.commit_plan.values())
        commit_count = 0
        
        for date, count in sorted(self.commit_plan.items()):
            for i in range(count):
                commit_count += 1
                if show_progress:
                    progress = (commit_count / total_commits) * 100
                    print(f"\rGenerating commits: {commit_count}/{total_commits} ({progress:.1f}%)", end="")
                
                # Update the README with a timestamp to make each commit unique
                with open("README.md", "a") as f:
                    f.write(f"\n\nCommit: {date.isoformat()}")
                
                # Stage and commit with the specified date
                subprocess.run(["git", "add", "README.md"], check=True, stdout=subprocess.DEVNULL)
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                subprocess.run([
                    "git", 
                    "commit", 
                    "-m", f"Update: {date_str}", 
                    "--date", date_str
                ], check=True, stdout=subprocess.DEVNULL if not show_progress else None)
        
        if show_progress:
            print("\nCommits generated successfully!")
        
        # Push to GitHub if credentials are provided
        if self.auto_push and self.github_username:
            return self.push_to_github(show_progress)
        elif show_progress:
            print(f"\nTo push to GitHub:")
            print(f"1. Create a private repository called '{self.output_dir}'")
            print(f"2. Run the following commands:")
            print(f"   cd {self.output_dir}")
            print(f"   git remote add origin git@github.com:{self.github_username or '<USERNAME>'}/{self.output_dir}.git")
            print(f"   git push -u origin master")
        
        return True
    
    def push_to_github(self, show_progress: bool = True) -> bool:
        """
        Push the repository to GitHub using the provided credentials.
        
        Args:
            show_progress: Whether to show progress information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.github_username:
            if show_progress:
                print("Error: GitHub username is required to push to GitHub.")
            return False
        
        try:
            # Configure remote origin
            if self.github_token:
                # Use HTTPS with token
                remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/{self.output_dir}.git"
            else:
                # Use SSH (requires SSH key to be set up)
                remote_url = f"git@github.com:{self.github_username}/{self.output_dir}.git"
            
            if show_progress:
                print(f"\nPushing to GitHub repository: {self.github_username}/{self.output_dir}")
            
            # Add remote
            subprocess.run(["git", "remote", "add", "origin", remote_url], 
                          check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Push to remote
            subprocess.run(["git", "push", "-u", "origin", "master"], 
                          check=True, stdout=subprocess.DEVNULL if not show_progress else None)
            
            if show_progress:
                print(f"Successfully pushed to GitHub: https://github.com/{self.github_username}/{self.output_dir}")
            
            return True
        
        except subprocess.CalledProcessError as e:
            if show_progress:
                print(f"Error pushing to GitHub: {e}")
                print("Make sure you have created a repository with the same name on GitHub and have proper permissions.")
                print("You may need to push manually:")
                print(f"   cd {self.output_dir}")
                print(f"   git remote add origin git@github.com:{self.github_username}/{self.output_dir}.git")
                print(f"   git push -u origin master")
            return False
    
    def save_credentials(self, credentials_file: str = "~/.git_fixer_credentials") -> bool:
        """
        Save GitHub credentials to a file for future use.
        
        Args:
            credentials_file: Path to the credentials file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.github_username:
            print("Error: No GitHub username to save.")
            return False
        
        try:
            credentials = {
                "github_username": self.github_username,
                "github_token": self.github_token if self.github_token else ""
            }
            
            # Expand the path
            file_path = os.path.expanduser(credentials_file)
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the credentials
            with open(file_path, "w") as f:
                json.dump(credentials, f)
            
            # Set permissions to user-only
            os.chmod(file_path, 0o600)
            
            print(f"Credentials saved to {file_path}")
            return True
        
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    @staticmethod
    def load_credentials(credentials_file: str = "~/.git_fixer_credentials") -> Dict[str, str]:
        """
        Load GitHub credentials from a file.
        
        Args:
            credentials_file: Path to the credentials file
            
        Returns:
            Dictionary with GitHub username and token
        """
        try:
            # Expand the path
            file_path = os.path.expanduser(credentials_file)
            
            # Check if the file exists
            if not os.path.exists(file_path):
                return {}
            
            # Load the credentials
            with open(file_path, "r") as f:
                credentials = json.load(f)
            
            return credentials
        
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {}


# Command-line interface
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate fake git commits to create GitHub activity"
    )
    parser.add_argument(
        "--preview", 
        action="store_true", 
        help="Preview the activity graph without creating commits"
    )
    parser.add_argument(
        "--frequency", 
        type=int, 
        default=80, 
        help="Percentage chance (0-100) of generating commits for each day (default: 80)"
    )
    parser.add_argument(
        "--distribution", 
        choices=["uniform", "workHours", "afterWork"], 
        default="uniform", 
        help="Distribution pattern for commits (default: uniform)"
    )
    parser.add_argument(
        "--startDate", 
        type=str, 
        help="Start date in YYYY/MM/DD format (default: 365 days ago)"
    )
    parser.add_argument(
        "--endDate", 
        type=str, 
        help="End date in YYYY/MM/DD format (default: today)"
    )
    parser.add_argument(
        "--commitsPerDay", 
        type=str, 
        default="0,4", 
        help="Range of commits per day as min,max (default: 0,4)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="my-history", 
        help="Output directory name (default: my-history)"
    )
    parser.add_argument(
        "--github-username", 
        type=str, 
        help="GitHub username for repository creation/pushing"
    )
    parser.add_argument(
        "--github-token", 
        type=str, 
        help="GitHub personal access token for authentication"
    )
    parser.add_argument(
        "--auto-push", 
        action="store_true", 
        help="Automatically push to GitHub after creating commits"
    )
    parser.add_argument(
        "--repo-private", 
        action="store_true", 
        default=True, 
        help="Make the GitHub repository private (default: True)"
    )
    parser.add_argument(
        "--save-credentials", 
        action="store_true", 
        help="Save GitHub credentials for future use"
    )
    parser.add_argument(
        "--use-saved-credentials", 
        action="store_true", 
        help="Use saved GitHub credentials"
    )
    
    args = parser.parse_args()
    
    # Parse commits per day
    try:
        min_commits, max_commits = map(int, args.commitsPerDay.split(","))
        args.min_commits = min_commits
        args.max_commits = max_commits
    except ValueError:
        parser.error("commitsPerDay must be in format min,max where 0 <= min <= max")
    
    # Parse dates
    if args.startDate:
        try:
            args.start_date = datetime.strptime(args.startDate, "%Y/%m/%d")
        except ValueError:
            parser.error("startDate must be in YYYY/MM/DD format")
    else:
        args.start_date = None
    
    if args.endDate:
        try:
            args.end_date = datetime.strptime(args.endDate, "%Y/%m/%d")
        except ValueError:
            parser.error("endDate must be in YYYY/MM/DD format")
    else:
        args.end_date = None
    
    # Load saved credentials if requested
    if args.use_saved_credentials:
        credentials = GitHistoryGenerator.load_credentials()
        if not args.github_username and "github_username" in credentials:
            args.github_username = credentials["github_username"]
        if not args.github_token and "github_token" in credentials:
            args.github_token = credentials["github_token"]
    
    # Prompt for GitHub credentials if auto-push is enabled but credentials are missing
    if args.auto_push and not args.github_username:
        args.github_username = input("GitHub username: ")
        if not args.github_token:
            args.github_token = getpass.getpass("GitHub personal access token (leave blank to use SSH): ")
            if not args.github_token:
                args.github_token = None
    
    return args


def main():
    """Main function for command-line usage."""
    args = parse_args()
    
    # Create generator with command line arguments
    try:
        generator = GitHistoryGenerator(
            start_date=args.start_date,
            end_date=args.end_date,
            frequency=args.frequency,
            distribution=args.distribution,
            min_commits=args.min_commits,
            max_commits=args.max_commits,
            output_dir=args.output,
            github_username=args.github_username,
            github_token=args.github_token,
            auto_push=args.auto_push,
            repo_private=args.repo_private
        )
        
        print(f"Fake Git History Generator")
        print(f"-------------------------")
        print(f"Date Range: {generator.start_date.date()} to {generator.end_date.date()}")
        print(f"Frequency: {generator.frequency}%")
        print(f"Distribution: {generator.distribution}")
        print(f"Commits per day: {generator.min_commits}-{generator.max_commits}")
        
        if generator.github_username:
            print(f"GitHub Username: {generator.github_username}")
            if generator.auto_push:
                print(f"Auto-push to GitHub: Enabled")
        
        # Generate commit plan
        generator.generate_commit_plan()
        
        # Preview mode
        if args.preview:
            generator.print_preview()
            return
        
        # Create git repository with commits
        success = generator.create_git_repo()
        
        # Save credentials if requested
        if success and args.save_credentials and args.github_username:
            generator.save_credentials()
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 