import asyncio
import sys
import traceback
from scrapers import gupy, catho, vagas_com, infojobs, workana

# Reconfigure stdout/stderr to UTF-8 to handle Portuguese accents/characters on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

async def test_scraper(name, scraper_func, keyword="Python"):
    print(f"\n--- Testing Scraper: {name} ---")
    try:
        print(f"Calling {name}.scrape(keyword='{keyword}', level='Todos', max_pages=1)...")
        jobs = await scraper_func(keyword=keyword, level="Todos", max_pages=1)
        
        print(f"Scraper {name} returned {len(jobs)} jobs.")
        
        if not isinstance(jobs, list):
            print(f"[FAIL] {name}: Return value is not a list. Type: {type(jobs)}")
            return False, []
            
        if len(jobs) == 0:
            print(f"[FAIL] {name}: No jobs returned (list is empty).")
            return False, []
            
        schema_keys = {
            "platform", "title", "company", "budget", "link", 
            "job_type", "profession", "level", "requirements"
        }
        
        for idx, job in enumerate(jobs):
            if not isinstance(job, dict):
                print(f"[FAIL] {name} job #{idx} is not a dict. Type: {type(job)}")
                return False, jobs
                
            missing_keys = schema_keys - set(job.keys())
            if missing_keys:
                print(f"[FAIL] {name} job #{idx} is missing keys: {missing_keys}")
                print(f"Job dict keys: {list(job.keys())}")
                return False, jobs
                
            # Verify string values for critical fields
            for key in ["platform", "title", "company", "link", "requirements"]:
                val = job.get(key)
                if not val or not isinstance(val, str) or len(val.strip()) == 0:
                    print(f"[FAIL] {name} job #{idx} key '{key}' has empty or invalid value: {repr(val)}")
                    return False, jobs
                    
        print(f"[PASS] {name} successfully passed verification with {len(jobs)} jobs.")
        # Print sample job safely
        sample = jobs[0]
        print(f"Sample Job from {name}:")
        for k, v in sample.items():
            val_str = str(v)[:150] + ("..." if len(str(v)) > 150 else "")
            # Safe print encoding representation
            safe_val_str = val_str.encode('utf-8', errors='replace').decode('utf-8')
            print(f"  - {k}: {repr(safe_val_str)}")
        return True, jobs
        
    except Exception as e:
        print(f"[FAIL] {name} scraper failed with an exception:")
        traceback.print_exc()
        return False, []

async def main():
    print("==================================================")
    print("Starting Live CLT & Workana Scrapers Verification")
    print("==================================================")
    
    scrapers_to_test = {
        "Gupy": gupy.scrape,
        "Catho": catho.scrape,
        "Vagas.com": vagas_com.scrape,
        "InfoJobs": infojobs.scrape,
        "Workana": workana.scrape
    }
    
    # Run all scrapers concurrently (asynchronously) as requested
    tasks = {name: asyncio.create_task(test_scraper(name, func)) for name, func in scrapers_to_test.items()}
    
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    print("\n==================================================")
    print("Live Scraper Verification Summary")
    print("==================================================")
    
    success = True
    for name, res in zip(tasks.keys(), results):
        if isinstance(res, Exception):
            print(f"- {name}: FAILED with unhandled task exception: {res}")
            success = False
        else:
            status, jobs = res
            if status:
                print(f"- {name}: PASSED (Found {len(jobs)} vacancies)")
            else:
                print(f"- {name}: FAILED validation or returned 0 vacancies")
                success = False
                
    if success:
        print("\nAll scrapers verified successfully against live endpoints!")
        sys.exit(0)
    else:
        print("\nOne or more scrapers failed live verification.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
