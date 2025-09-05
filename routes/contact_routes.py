from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required
from models import db, ContactMessage

contact_bp = Blueprint("contact", __name__)

@contact_bp.route('/admin/contacts/mark_reviewed/<int:id>', methods=['POST'])
@login_required
def mark_contact_reviewed(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.reviewed = True
    db.session.commit()
    flash("Message marked as reviewed.", "success")
    return redirect(url_for('dashboard.admin_dashboard'))


@contact_bp.route('/admin/contacts/<int:id>/review', methods=['POST'])
@login_required
def admin_review_contact(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.reviewed = True
    db.session.delete(msg)
    db.session.commit()
    flash("Contact message reviewed and cleared.", "success")
    return redirect(url_for('dashboard.admin_dashboard'))


@contact_bp.route('/admin/contacts/clear_all', methods=['POST'])
@login_required
def admin_clear_all_contacts():
    messages = ContactMessage.query.filter_by(reviewed=False).all()
    for msg in messages:
        msg.reviewed = True
        db.session.delete(msg)
    db.session.commit()
    flash("All contact messages reviewed and cleared.", "success")
    return redirect(url_for('dashboard.admin_dashboard'))

