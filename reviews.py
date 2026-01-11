from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from extensions import db, limiter
from models import Review, User, Reply, Report, Subject
from datetime import datetime
from sqlalchemy import func

reviews_bp = Blueprint('reviews', __name__)

def validate_rating(value):
    """Validate that rating is an integer between 1 and 5"""
    try:
        rating = int(value)
        return 1 <= rating <= 5
    except (ValueError, TypeError):
        return False

@reviews_bp.route('/create_review/<int:lecturer_id>', methods=['GET', 'POST'])
@login_required
# @limiter.limit("10 per hour")  # Disabled for development
def create_review(lecturer_id):
    if current_user.user_type != 'student':
        flash(_("Only students can write reviews"), "error")
        return redirect(url_for('index'))
    
    lecturer = User.query.get_or_404(lecturer_id)
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid lecturer"), "error")
        return redirect(url_for('index'))
    
    existing_review = Review.query.filter_by(user_id=current_user.id, lecturer_id=lecturer_id).first()
    if existing_review:
        flash("You have already written a review for this lecturer. You can only write one review per lecturer.", "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    if request.method == 'GET':
        return render_template('create_review.html', lecturer=lecturer)
    
    review_text = request.form.get('review_text', '').strip()
    
    try:
        rating_clarity = int(request.form.get('rating_clarity', 0))
        rating_engagement = int(request.form.get('rating_engagement', 0))
        rating_punctuality = int(request.form.get('rating_punctuality', 0))
        rating_responsiveness = int(request.form.get('rating_responsiveness', 0))
        rating_fairness = int(request.form.get('rating_fairness', 0))
    except (ValueError, TypeError):
        flash(_("Invalid rating value. Ratings must be numbers."), "error")
        return redirect(url_for('reviews.create_review', lecturer_id=lecturer_id))
    
    if not all([validate_rating(rating_clarity), validate_rating(rating_engagement), 
                validate_rating(rating_punctuality), validate_rating(rating_responsiveness),
                validate_rating(rating_fairness)]):
        flash(_("All ratings must be between 1 and 5."), "error")
        return redirect(url_for('reviews.create_review', lecturer_id=lecturer_id))
    
    recommend = request.form.get('recommend')
    subject_input = request.form.get('subject_input', '').strip()
    is_anonymous = request.form.get('is_anonymous') == 'on'
    
    if not review_text or not recommend:
        flash(_("Please fill all fields"), "error")
        return redirect(url_for('reviews.create_review', lecturer_id=lecturer_id))
    
    recommend = recommend.lower() == 'yes'
    
    # Handle subject selection/creation
    subject_id = None
    if subject_input:
        # Check if subject exists by code or name
        subject = Subject.query.filter(
            db.or_(
                Subject.subject_code.ilike(subject_input),
                Subject.subject_name.ilike(subject_input)
            )
        ).first()
        
        if subject:
            subject_id = subject.id
            subject.usage_count += 1
        else:
            # Create new subject from input (format: "CODE - NAME" or just "NAME")
            if ' - ' in subject_input:
                code, name = subject_input.split(' - ', 1)
                code = code.strip()
                name = name.strip()
            else:
                code = None
                name = subject_input
            
            new_subject = Subject(
                subject_code=code,
                subject_name=name,
                usage_count=1
            )
            db.session.add(new_subject)
            db.session.flush()  # Get the ID before commit
            subject_id = new_subject.id
    
    review = Review(
        review_text=review_text,
        rating_clarity=rating_clarity,
        rating_engagement=rating_engagement,
        rating_punctuality=rating_punctuality,
        rating_responsiveness=rating_responsiveness,
        rating_fairness=rating_fairness,
        recommend=recommend,
        user_id=current_user.id,
        lecturer_id=lecturer_id,
        subject_id=subject_id,
        is_anonymous=is_anonymous,
        subject_code=subject_input
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash(_("Review submitted successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))

@reviews_bp.route('/lecturer/<int:lecturer_id>')
@login_required
def lecturer_profile(lecturer_id):
    lecturer = User.query.get_or_404(lecturer_id)
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid lecturer"), "error")
        return redirect(url_for('index'))
    
    reviews = Review.query.filter_by(lecturer_id=lecturer_id).order_by(Review.is_pinned.desc(), Review.review_date.desc()).all()
    
    user_review = None
    student_has_review = False
    if current_user.user_type == 'student':
        user_review = Review.query.filter_by(user_id=current_user.id, lecturer_id=lecturer_id).first()
        student_has_review = user_review is not None
    
    if user_review and user_review in reviews:
        reviews.remove(user_review)
        pinned_count = sum(1 for r in reviews if r.is_pinned)
        reviews.insert(pinned_count, user_review)
    
    reported_review_ids = []
    if current_user.user_type == 'student':
        reported_reports = Report.query.filter_by(reporter_id=current_user.id).all()
        reported_review_ids = [report.review_id for report in reported_reports]
    
    if reviews:
        avg_clarity = db.session.query(func.avg(Review.rating_clarity)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_engagement = db.session.query(func.avg(Review.rating_engagement)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_punctuality = db.session.query(func.avg(Review.rating_punctuality)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_responsiveness = db.session.query(func.avg(Review.rating_responsiveness)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_fairness = db.session.query(func.avg(Review.rating_fairness)).filter_by(lecturer_id=lecturer_id).scalar()
        
        averages = {
            'clarity': round(avg_clarity, 1) if avg_clarity else 0,
            'engagement': round(avg_engagement, 1) if avg_engagement else 0,
            'punctuality': round(avg_punctuality, 1) if avg_punctuality else 0,
            'responsiveness': round(avg_responsiveness, 1) if avg_responsiveness else 0,
            'fairness': round(avg_fairness, 1) if avg_fairness else 0,
        }
        
        recommend_count = Review.query.filter_by(lecturer_id=lecturer_id, recommend=True).count()
        recommend_percentage = round((recommend_count / len(reviews)) * 100) if reviews else None
    else:
        averages = None
        recommend_percentage = None
    
    return render_template('lecturer_profile.html', lecturer=lecturer, reviews=reviews, averages=averages, recommend_percentage=recommend_percentage, reported_review_ids=reported_review_ids, student_has_review=student_has_review, user_review_id=user_review.id if user_review else None, now=datetime.utcnow())

@reviews_bp.route('/claim_profile/<int:lecturer_id>', methods=['POST'])
@login_required
def claim_profile(lecturer_id):

    if current_user.user_type != 'lecturer':
        flash(_("Only lecturers can claim profiles"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    if current_user.is_claimed:
        flash(_("You have already claimed a profile"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    if not current_user.email.endswith('@mmu.edu.my'):
        flash(_("Only official MMU email addresses (@mmu.edu.my) can claim profiles"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    lecturer = User.query.get_or_404(lecturer_id)
    
    if current_user.email != lecturer.email:
        flash(_("You can only claim your own profile"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid profile"), "error")
        return redirect(url_for('index'))
    
    if lecturer.is_claimed:
        flash(_("This profile has already been claimed"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))
    
    lecturer.is_claimed = True
    db.session.commit()
    
    flash(_("Profile claimed successfully! You are now verified."), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))

@reviews_bp.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if review.author != current_user:
        flash(_("You can only edit your own reviews"), "error")
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('edit_review.html', review=review)
    
    review_text = request.form.get('review_text', '').strip()
    rating_clarity = int(request.form.get('rating_clarity', 0))
    rating_engagement = int(request.form.get('rating_engagement', 0))
    rating_punctuality = int(request.form.get('rating_punctuality', 0))
    rating_responsiveness = int(request.form.get('rating_responsiveness', 0))
    rating_fairness = int(request.form.get('rating_fairness', 0))
    is_anonymous = request.form.get('is_anonymous') == 'on'
    recommend = request.form.get('recommend')
    subject_input = request.form.get('subject_input', '').strip()
    
    if not review_text or not all([rating_clarity, rating_engagement, rating_punctuality, rating_responsiveness, rating_fairness]) or not recommend:
        flash(_("Please fill all fields"), "error")
        return redirect(url_for('reviews.edit_review', review_id=review_id))
    
    recommend = recommend.lower() == 'yes'
    
    # Handle subject selection/creation for edit
    subject_id = None
    if subject_input:
        subject = Subject.query.filter(
            db.or_(
                Subject.subject_code.ilike(subject_input),
                Subject.subject_name.ilike(subject_input)
            )
        ).first()
        
        if subject:
            subject_id = subject.id
            if review.subject_id != subject.id:
                subject.usage_count += 1
        else:
            # Create new subject
            if ' - ' in subject_input:
                code, name = subject_input.split(' - ', 1)
                code = code.strip()
                name = name.strip()
            else:
                code = None
                name = subject_input
            
            new_subject = Subject(
                subject_code=code,
                subject_name=name,
                usage_count=1
            )
            db.session.add(new_subject)
            db.session.flush()
            subject_id = new_subject.id
    
    review.review_text = review_text
    review.rating_clarity = rating_clarity
    review.rating_engagement = rating_engagement
    review.rating_punctuality = rating_punctuality
    review.rating_responsiveness = rating_responsiveness
    review.rating_fairness = rating_fairness
    review.is_anonymous = is_anonymous
    review.recommend = recommend
    review.subject_id = subject_id
    review.subject_code = subject_input
    
    db.session.commit()
    
    flash(_("Review updated successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))

@reviews_bp.route('/review/<int:review_id>/delete', methods=['GET'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if review.author != current_user:
        flash(_("You can only delete your own reviews"), "error")
        return redirect(url_for('index'))

    lecturer_id = review.lecturer_id
    
    db.session.delete(review)
    db.session.commit()
    
    flash(_("Review deleted successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))

@reviews_bp.route('/review/<int:review_id>/reply', methods=['POST'])
@login_required
# @limiter.limit("20 per hour")  # Disabled for development
def add_reply(review_id):
    review = Review.query.get_or_404(review_id)
    
    if current_user.user_type not in ['student', 'lecturer'] and not current_user.is_mod():
        flash(_("Only students, lecturers, and admins can reply"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
    
    reply_text = request.form.get('reply_text', '').strip()
    
    if not reply_text:
        flash(_("Reply cannot be empty"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
    
    reply = Reply(
        reply_text=reply_text,
        user_id=current_user.id,
        review_id=review_id,
        is_admin=current_user.is_mod()
    )
    
    db.session.add(reply)
    db.session.commit()
    
    flash(_("Reply posted successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))

@reviews_bp.route('/review/<int:review_id>/report', methods=['POST'])
@login_required
# @limiter.limit("5 per hour")  # Disabled for development
def report_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if current_user.user_type != 'student':
        flash(_("Only students can report reviews"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
    
    existing_report = Report.query.filter_by(review_id=review_id, reporter_id=current_user.id).first()
    if existing_report:
        flash(_("You have already reported this review"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
    
    reason = request.form.get('reason', '').strip()
    
    if not reason:
        flash(_("Please provide a reason for reporting"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
    
    report = Report(
        review_id=review_id,
        reporter_id=current_user.id,
        reason=reason
    )
    
    db.session.add(report)
    db.session.commit()
    
    flash(_("Review reported successfully. Admins will review it."), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))

@reviews_bp.route('/analytics/<int:lecturer_id>')
@login_required
def analytics(lecturer_id):
    lecturer = User.query.get_or_404(lecturer_id)
    
    if current_user.id != lecturer_id and not current_user.is_admin():
        flash(_("You don't have permission to view this analytics page"), "error")
        return redirect(url_for('index'))
    
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid lecturer"), "error")
        return redirect(url_for('index'))
    
    reviews = Review.query.filter_by(lecturer_id=lecturer_id).all()
    total_reviews = len(reviews)
    
    if reviews:
        avg_clarity = db.session.query(func.avg(Review.rating_clarity)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_engagement = db.session.query(func.avg(Review.rating_engagement)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_punctuality = db.session.query(func.avg(Review.rating_punctuality)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_responsiveness = db.session.query(func.avg(Review.rating_responsiveness)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_fairness = db.session.query(func.avg(Review.rating_fairness)).filter_by(lecturer_id=lecturer_id).scalar()
        
        averages = {
            'clarity': round(avg_clarity, 1) if avg_clarity else 0,
            'engagement': round(avg_engagement, 1) if avg_engagement else 0,
            'punctuality': round(avg_punctuality, 1) if avg_punctuality else 0,
            'responsiveness': round(avg_responsiveness, 1) if avg_responsiveness else 0,
            'fairness': round(avg_fairness, 1) if avg_fairness else 0,
        }
        
        overall_rating = round((averages['clarity'] + averages['engagement'] + averages['punctuality'] + averages['responsiveness'] + averages['fairness']) / 5, 1)
        
        strongest = max(averages, key=averages.get)
        weakest = min(averages, key=averages.get)
    else:
        averages = None
        overall_rating = 0
        strongest = None
        weakest = None
    
    if current_user.is_admin():
        all_lecturers = User.query.filter_by(user_type='lecturer').all()
        lecturer_stats = []
        
        for lect in all_lecturers:
            lect_reviews = Review.query.filter_by(lecturer_id=lect.id).all()
            if lect_reviews:
                lect_avg = db.session.query(
                    func.avg(Review.rating_clarity + Review.rating_engagement + Review.rating_punctuality + Review.rating_responsiveness + Review.rating_fairness) / 5
                ).filter_by(lecturer_id=lect.id).scalar()
                
                lecturer_stats.append({
                    'id': lect.id,
                    'email': lect.email,
                    'overall': round(lect_avg, 1) if lect_avg else 0,
                    'total_reviews': len(lect_reviews)
                })
        
        lecturer_stats.sort(key=lambda x: x['overall'], reverse=True)
    else:
        lecturer_stats = None
    
    return render_template('analytics.html', 
                         lecturer=lecturer, 
                         total_reviews=total_reviews, 
                         averages=averages,
                         overall_rating=overall_rating,
                         strongest=strongest,
                         weakest=weakest,
                         lecturer_stats=lecturer_stats)

@reviews_bp.route('/student-analytics/<int:lecturer_id>')
@login_required
def student_analytics(lecturer_id):
    lecturer = User.query.get_or_404(lecturer_id)
    
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid lecturer"), "error")
        return redirect(url_for('index'))
    
    reviews = Review.query.filter_by(lecturer_id=lecturer_id).all()
    total_reviews = len(reviews)
    
    if reviews:
        avg_clarity = db.session.query(func.avg(Review.rating_clarity)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_engagement = db.session.query(func.avg(Review.rating_engagement)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_punctuality = db.session.query(func.avg(Review.rating_punctuality)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_responsiveness = db.session.query(func.avg(Review.rating_responsiveness)).filter_by(lecturer_id=lecturer_id).scalar()
        avg_fairness = db.session.query(func.avg(Review.rating_fairness)).filter_by(lecturer_id=lecturer_id).scalar()
        
        averages = {
            'clarity': round(avg_clarity, 1) if avg_clarity else 0,
            'engagement': round(avg_engagement, 1) if avg_engagement else 0,
            'punctuality': round(avg_punctuality, 1) if avg_punctuality else 0,
            'responsiveness': round(avg_responsiveness, 1) if avg_responsiveness else 0,
            'fairness': round(avg_fairness, 1) if avg_fairness else 0,
        }
        
        overall_rating = round((averages['clarity'] + averages['engagement'] + averages['punctuality'] + averages['responsiveness'] + averages['fairness']) / 5, 1)
    else:
        averages = None
        overall_rating = 0
    
    user_review = None
    if current_user.user_type == 'student':
        user_review = Review.query.filter_by(user_id=current_user.id, lecturer_id=lecturer_id).first()
    
    distribution = None
    if reviews:
        distribution = {
            'clarity': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'engagement': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'punctuality': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'responsiveness': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'fairness': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }
        
        for review in reviews:
            distribution['clarity'][review.rating_clarity] += 1
            distribution['engagement'][review.rating_engagement] += 1
            distribution['punctuality'][review.rating_punctuality] += 1
            distribution['responsiveness'][review.rating_responsiveness] += 1
            distribution['fairness'][review.rating_fairness] += 1
    
    all_lecturers_avg = None
    comparison_text = None
    if reviews:
        all_lecturers = User.query.filter_by(user_type='lecturer').all()
        all_ratings = []
        
        for lect in all_lecturers:
            lect_reviews = Review.query.filter_by(lecturer_id=lect.id).all()
            if lect_reviews:
                lect_avg = sum([
                    (r.rating_clarity + r.rating_engagement + r.rating_punctuality + r.rating_responsiveness + r.rating_fairness) / 5
                    for r in lect_reviews
                ]) / len(lect_reviews)
                all_ratings.append(lect_avg)
        
        if all_ratings:
            all_lecturers_avg = round(sum(all_ratings) / len(all_ratings), 1)
            diff = overall_rating - all_lecturers_avg
            if diff > 0.5:
                comparison_text = f"{diff:.1f} points ABOVE AVERAGE"
            elif diff < -0.5:
                comparison_text = f"{abs(diff):.1f} points BELOW AVERAGE"
            else:
                comparison_text = "AT AVERAGE LEVEL"
    
    return render_template('student_analytics.html', 
                         lecturer=lecturer, 
                         total_reviews=total_reviews, 
                         averages=averages,
                         overall_rating=overall_rating,
                         user_review=user_review,
                         distribution=distribution,
                         all_lecturers_avg=all_lecturers_avg,
                         comparison_text=comparison_text)

@reviews_bp.route('/reply/<int:reply_id>/edit', methods=['POST'])
@login_required
def edit_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    
    
    if reply.author != current_user:
        flash(_("You can only edit your own replies"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=reply.review.lecturer_id))
    
    new_text = request.form.get('reply_text', '').strip()
    
    if not new_text:
        flash(_("Reply cannot be empty"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=reply.review.lecturer_id))
    
    reply.reply_text = new_text
    reply.is_edited = True
    db.session.commit()
    
    flash(_("Reply updated successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=reply.review.lecturer_id))

@reviews_bp.route('/reply/<int:reply_id>/delete', methods=['GET'])
@login_required
def delete_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    
    if reply.author != current_user:
        flash(_("You can only delete your own replies"), "error")
        return redirect(url_for('reviews.lecturer_profile', lecturer_id=reply.review.lecturer_id))
    
    lecturer_id = reply.review.lecturer_id
    
    db.session.delete(reply)
    db.session.commit()
    
    flash(_("Reply deleted successfully!"), "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=lecturer_id))

@reviews_bp.route('/lecturer/<int:lecturer_id>/bio', methods=['GET', 'POST'])
@login_required
def lecturer_bio(lecturer_id):
    lecturer = User.query.get_or_404(lecturer_id)
    
    if lecturer.user_type != 'lecturer':
        flash(_("Invalid lecturer"), "error")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if current_user.id != lecturer_id:
            flash(_("You can only edit your own bio"), "error")
            return redirect(url_for('reviews.lecturer_bio', lecturer_id=lecturer_id))
        
        if current_user.user_type != 'lecturer':
            flash(_("Only lecturers can edit bios"), "error")
            return redirect(url_for('reviews.lecturer_bio', lecturer_id=lecturer_id))
        
        bio_text = request.form.get('bio', '').strip()
        
        lecturer.bio = bio_text if bio_text else None
        db.session.commit()
        
        flash(_("Bio updated successfully!"), "success")
        return redirect(url_for('reviews.lecturer_bio', lecturer_id=lecturer_id))
    
    can_edit = current_user.id == lecturer_id and current_user.user_type == 'lecturer'
    
    return render_template('lecturer_bio.html', lecturer=lecturer, can_edit=can_edit)

@reviews_bp.route('/review/<int:review_id>/pin', methods=['GET', 'POST'])
@login_required
def pin_review(review_id):
    if not current_user.is_mod():
        flash("Only admins can pin reviews", "error")
        return redirect(request.referrer or url_for('index'))
    
    review = Review.query.get_or_404(review_id)
    review.is_pinned = True
    db.session.commit()
    
    flash("Review pinned to top", "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))

@reviews_bp.route('/review/<int:review_id>/unpin', methods=['GET', 'POST'])
@login_required
def unpin_review(review_id):
    if not current_user.is_mod():
        flash("Only admins can unpin reviews", "error")
        return redirect(request.referrer or url_for('index'))
    
    review = Review.query.get_or_404(review_id)
    review.is_pinned = False
    db.session.commit()
    
    flash("Review unpinned", "success")
    return redirect(url_for('reviews.lecturer_profile', lecturer_id=review.lecturer_id))
