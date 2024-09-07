import os

CACHE_FILE = os.getenv('CACHE_FILE')

async def update_cache(to_email):
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'w') as f:
            f.write(to_email + '\n')
    else:
        with open(CACHE_FILE, 'r') as f:
            emails = f.read().splitlines()

        if to_email not in emails:
            with open(CACHE_FILE, 'a') as f:
                f.write(to_email + '\n')
                
async def load_cache():
    if not os.path.exists(CACHE_FILE):
        return []
    
    with open(CACHE_FILE, 'r') as f:
        return f.read().splitlines()
    
async def remove_from_cache(email):
    if not os.path.exists(CACHE_FILE):
        return
    
    with open(CACHE_FILE, 'r') as f:
        emails = f.read().splitlines()

    if email in emails:
        emails.remove(email)
        with open(CACHE_FILE, 'w') as f:
            f.write('\n'.join(emails) + '\n')