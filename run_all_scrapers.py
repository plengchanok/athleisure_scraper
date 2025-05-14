import subprocess
import time
import os
import sys

def run_script(script_name):
    """Run a Python script and capture its output"""
    print(f"\n{'='*80}")
    print(f"Running {script_name}...")
    print(f"{'='*80}\n")
    
    try:
        # Run the script and capture output
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            print(f"\n✅ {script_name} completed successfully.\n")
        else:
            print(f"\n❌ {script_name} failed with return code {process.returncode}.\n")
            
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}\n")

def main():
    # List of all scraper scripts
    scrapers = [
        "scraper_vuori.py",
        "scraper_alo_new.py",
        "scraper_lululemon_new.py",
        "scraper_beyond_yoga.py",
        "scraper_athleta.py"
    ]
    
    # Run each scraper with a delay between them
    for scraper in scrapers:
        run_script(scraper)
        print("Waiting 30 seconds before running the next scraper...")
        time.sleep(30)
    
    print("\nAll scrapers have been executed!")

if __name__ == "__main__":
    main()