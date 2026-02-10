"""
Scrape MMUExpert lecturers and bios from mmuexpert.mmu.edu.my
Local-only script, not committed to git
"""
import requests
from bs4 import BeautifulSoup
from app import app, db
from models import Lecturer

FACULTIES = ['FAC', 'FAIE', 'FOB', 'FCA', 'FCI', 'FCM', 'FET', 'FIST', 'FOL', 'FOM', 'LIFE']
BASE_URL = "https://mmuexpert.mmu.edu.my"

def extract_lecturer_data_from_page(faculty_url):
    """
    Extract lecturer links from faculty listing page.
    Returns list of dicts: {'name': str, 'email': str, 'profile_url': str}
    """
    lecturers = []
    
    try:
        response = requests.get(faculty_url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all lecturer cards (col-md-2 divs)
        cards = soup.find_all('div', class_='col-md-2')
        
        for card in cards:
            # Extract name from h2
            name_tag = card.find('h2')
            if not name_tag:
                continue
            name = name_tag.text.strip()
            
            # Extract email
            email = None
            for text in card.stripped_strings:
                if '@mmu.edu.my' in text:
                    parts = text.split()
                    for part in parts:
                        if '@mmu.edu.my' in part:
                            email = part.strip().rstrip(')')
                            break
                    if email:
                        break
            
            if not email:
                continue
            
            # Extract profile URL from link
            profile_url = None
            link = card.find('a', href=True)
            if link and link.get('href'):
                href = link['href']
                # Ensure it's a full URL
                if href.startswith('http'):
                    profile_url = href
                elif href.startswith('/'):
                    profile_url = BASE_URL + href
                else:
                    profile_url = BASE_URL + '/' + href
            
            if name and email:
                lecturers.append({
                    'name': name,
                    'email': email,
                    'profile_url': profile_url
                })
        
        return lecturers
    except Exception as e:
        print(f"    Error: {e}")
        return []

def fetch_bio_from_profile(profile_url):
    """
    Fetch bio from lecturer's profile page.
    Returns bio text or None if not found
    """
    if not profile_url:
        return None
    
    try:
        response = requests.get(profile_url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for bs-callout div (the biography section)
            bio_section = soup.find('div', class_='bs-callout')
            if bio_section:
                # Get all <p> tags inside the bs-callout div
                paragraphs = bio_section.find_all('p')
                if paragraphs:
                    # Combine all paragraph text
                    bio_parts = [p.get_text(strip=True) for p in paragraphs]
                    bio_text = ' '.join(bio_parts)
                    if bio_text:
                        return bio_text
    except Exception:
        pass
    
    return None

print(f"Fetching lecturers from {len(FACULTIES)} faculties...\n")

all_lecturers = []

# Step 1: Extract lecturer data from faculty listing pages
for faculty in FACULTIES:
    faculty_url = f"{BASE_URL}/{faculty}"
    print(f"  Scraping {faculty}...", end=" ", flush=True)
    
    lecturers = extract_lecturer_data_from_page(faculty_url)
    for lect in lecturers:
        lect['department'] = faculty
    
    all_lecturers.extend(lecturers)
    print(f"{len(lecturers)} found")

print(f"\nTotal lecturers found: {len(all_lecturers)}\n")

# Step 2: Save to file for reference
with open('scraped_lecturers.txt', 'w', encoding='utf-8') as f:
    f.write("LECTURERS SCRAPED FROM MMUEXPERT.MMU.EDU.MY\n")
    f.write("=" * 80 + "\n\n")
    for i, lect in enumerate(all_lecturers, 1):
        f.write(f"{i:3d}. {lect['name']:<40} | {lect['email']:<25} | {lect['department']}\n")

print("✓ Saved list to scraped_lecturers.txt")

# Step 3: Fetch bios and insert/update in database
with app.app_context():
    added = 0
    updated = 0
    bio_found = 0
    
    print("\nFetching bios and updating database...")
    total = len(all_lecturers)
    
    for idx, lect in enumerate(all_lecturers, 1):
        # Check if lecturer exists
        existing = Lecturer.query.filter_by(email=lect['email']).first()
        
        # Fetch bio from profile URL
        bio = fetch_bio_from_profile(lect['profile_url'])
        if bio:
            bio_found += 1
        
        if existing:
            # Update existing lecturer with bio
            existing.bio = bio
            db.session.add(existing)
            updated += 1
        else:
            # Create new lecturer entry
            new_lecturer = Lecturer(
                email=lect['email'],
                name=lect['name'],
                department=lect['department'],
                bio=bio
            )
            db.session.add(new_lecturer)
            added += 1
        
        # Progress indicator every 10 lecturers
        if idx % 10 == 0:
            print(f"  Processed {idx}/{total}...")
    
    db.session.commit()
    
    print(f"\n✓ Added {added} new lecturers to database")
    print(f"✓ Updated {updated} existing lecturers with bios")
    print(f"✓ Fetched {bio_found} bios from MMUExpert")
    print(f"✓ Total lecturers in database: {Lecturer.query.count()}")
