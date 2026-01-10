from app import app, db
from models import User, Subject, Review, Reply
from extensions import bcrypt
from datetime import datetime, timedelta
import random

with app.app_context():
    # Create base test accounts (from init_db)
    base_accounts = [
        ("owner@mmu.edu.my", "lecturer", "OWNER", "owner"),
        ("admin@mmu.edu.my", "lecturer", "ADMIN", "admin"),
        ("lecturer@mmu.edu.my", "lecturer", None, "lecturer"),
        ("student@student.mmu.edu.my", "student", None, "student"),
    ]
    
    for email, user_type, role, password in base_accounts:
        existing = User.query.filter_by(email=email).first()
        if not existing:
            user = User(
                email=email,
                user_type=user_type,
                role=role,
                is_verified=True,
                is_claimed=(user_type == "lecturer")
            )
            user.password_hash = bcrypt.generate_password_hash(password)
            db.session.add(user)
    
    # Add more lecturers
    for i in range(1, 8):
        email = f"lecturer{i}@mmu.edu.my"
        existing = User.query.filter_by(email=email).first()
        if not existing:
            user = User(
                email=email,
                user_type="lecturer",
                is_verified=True,
                is_claimed=True,
                bio=f"I am Lecturer {i}. I teach with passion and dedication."
            )
            user.password_hash = bcrypt.generate_password_hash(f"lecturer{i}")
            db.session.add(user)
    
    # Add more students
    for i in range(1, 16):
        email = f"student{i}@student.mmu.edu.my"
        existing = User.query.filter_by(email=email).first()
        if not existing:
            user = User(
                email=email,
                user_type="student",
                is_verified=True
            )
            user.password_hash = bcrypt.generate_password_hash(f"student{i}")
            db.session.add(user)
    
    db.session.commit()
    
    # Add subjects
    subjects_data = [
        ("CS101", "Introduction to Computer Science"),
        ("CS201", "Data Structures"),
        ("CS301", "Algorithms"),
        ("MATH101", "Calculus I"),
        ("MATH201", "Linear Algebra"),
    ]
    
    for code, name in subjects_data:
        existing = Subject.query.filter_by(subject_code=code).first()
        if not existing:
            subject = Subject(subject_code=code, subject_name=name)
            db.session.add(subject)
    
    db.session.commit()
    
    # Add reviews
    lecturers = User.query.filter_by(user_type="lecturer").all()
    students = User.query.filter_by(user_type="student").all()
    subjects = Subject.query.all()
    
    review_texts = [
        "Great teacher! Very clear explanations and patient.",
        "Hard class but learned a lot. Highly recommend.",
        "Could improve on providing more examples.",
        "Best professor I've had. Really cares about students.",
        "Fast paced but enjoyable. Keep up the good work!",
        "Needs to slow down a bit, hard to follow.",
        "Excellent teaching style, very engaging.",
        "Feedback on assignments could be more detailed.",
        "Amazing! One of the best classes I've taken.",
        "Good material but exams are very difficult.",
    ]
    
    review_count = 0
    for lecturer in lecturers[1:]:  # Skip first lecturer
        for student in students[:random.randint(2, 5)]:  # Each student reviews 2-5 lecturers
            existing = Review.query.filter_by(user_id=student.id, lecturer_id=lecturer.id).first()
            if not existing:
                review = Review(
                    review_text=random.choice(review_texts),
                    rating_clarity=random.randint(3, 5),
                    rating_engagement=random.randint(3, 5),
                    rating_punctuality=random.randint(2, 5),
                    rating_responsiveness=random.randint(2, 5),
                    rating_fairness=random.randint(3, 5),
                    recommend=random.choice([True, True, True, False]),
                    user_id=student.id,
                    lecturer_id=lecturer.id,
                    subject_id=random.choice(subjects).id if subjects else None,
                    subject_code=random.choice([s.subject_code for s in subjects]) if subjects else None,
                    is_anonymous=random.choice([True, False, False, False]),
                    review_date=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(review)
                review_count += 1
    
    db.session.commit()
    
    # Add some replies to reviews
    reviews = Review.query.all()
    for review in reviews[:int(len(reviews) * 0.4)]:  # 40% of reviews get replies
        lecturer = User.query.get(review.lecturer_id)
        reply_texts = [
            "Thank you for the feedback!",
            "I appreciate your comments and will work on improvement.",
            "Glad you enjoyed the class!",
            "Will consider your suggestions for next semester.",
            "Thanks for taking the time to review!",
        ]
        reply = Reply(
            reply_text=random.choice(reply_texts),
            user_id=lecturer.id,
            review_id=review.id,
            is_admin=False
        )
        db.session.add(reply)
    
    db.session.commit()
    
    print("✓ Database seeded with realistic data!")
    print(f"\nData created:")
    print(f"  - {User.query.filter_by(user_type='lecturer').count()} lecturers")
    print(f"  - {User.query.filter_by(user_type='student').count()} students")
    print(f"  - {Subject.query.count()} subjects")
    print(f"  - {Review.query.count()} reviews")
    print(f"  - {Reply.query.count()} replies")
