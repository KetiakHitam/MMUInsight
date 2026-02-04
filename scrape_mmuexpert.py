"""
Scrape FCI lecturers from mmuexpert.mmu.edu.my and populate Lecturer table
Local-only script, not committed to git
"""
import requests
from bs4 import BeautifulSoup
from app import app, db
from models import Lecturer

faculties = ['FAC', 'FAIE', 'FOB', 'FCA', 'FCI', 'FCM', 'FET', 'FIST', 'FOL', 'FOM', 'LIFE']

print(f"Fetching lecturers from {len(faculties)} faculties...\n")

lecturers = []

for faculty in faculties:
    url = f"https://mmuexpert.mmu.edu.my/{faculty}"
    print(f"  Scraping {faculty}...", end=" ", flush=True)
    
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all lecturer cards (col-md-2 divs)
        cards = soup.find_all('div', class_='col-md-2')
        
        for card in cards:
            # Extract name from h2
            name_tag = card.find('h2')
            name = name_tag.text.strip() if name_tag else None
            
            # Extract email: look for text containing @mmu.edu.my and clean it
            email = None
            for text in card.stripped_strings:
                if '@mmu.edu.my' in text:
                    # Extract just the email part
                    parts = text.split()
                    for part in parts:
                        if '@mmu.edu.my' in part:
                            email = part.strip()
                            break
                    if email:
                        break
            
            if name and email:
                # Clean up email (remove trailing punctuation)
                email = email.rstrip(')')
                lecturers.append({'name': name, 'email': email, 'department': faculty})
        
        print(f"{len([l for l in lecturers if l['department'] == faculty])} found")
    
    except Exception as e:
        print(f"Error: {e}")

print(f"Found {len(lecturers)} lecturers\n")

# Save to file for easy viewing
with open('scraped_lecturers.txt', 'w', encoding='utf-8') as f:
    f.write("FCI LECTURERS SCRAPED FROM MMUEXPERT.MMU.EDU.MY\n")
    f.write("=" * 70 + "\n\n")
    for i, lect in enumerate(lecturers, 1):
        f.write(f"{i:3d}. {lect['name']:<40} | {lect['email']}\n")

print(f"✓ Saved list to scraped_lecturers.txt")

# Insert into DB
with app.app_context():
    added = 0
    for lect in lecturers:
        if not Lecturer.query.filter_by(email=lect['email']).first():
            new_lecturer = Lecturer(
                email=lect['email'],
                name=lect['name'],
                department=lect['department']
            )
            db.session.add(new_lecturer)
            added += 1
    
    db.session.commit()
    print(f"✓ Added {added} new lecturers to database")
    print(f"✓ Total lecturers in Lecturer table: {Lecturer.query.count()}")
