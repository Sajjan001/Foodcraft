import os
import re
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, session
from werkzeug.utils import secure_filename

from app import db
from app.models import Admission, ContactMessage
from app.i18n import translate
from app.data import (
    get_courses, get_course, get_why_choose_us, get_quick_info, get_gallery, get_gallery_categories,
    get_notices, get_notice_categories, get_facilities, get_achievements, get_states,
)

main_bp = Blueprint("main", __name__)

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp"}
ALLOWED_DOC_EXT = {"pdf", "png", "jpg", "jpeg"}
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _lang():
    return session.get("lang", "en")


def _t(key):
    return translate(key, _lang())


def _allowed_file(filename, allowed_ext):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext


def _save_upload(file_storage, allowed_ext):
    if not file_storage or file_storage.filename == "":
        return None
    if not _allowed_file(file_storage.filename, allowed_ext):
        return None
    filename = secure_filename(file_storage.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    stored_name = f"{timestamp}_{filename}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name))
    return stored_name


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in ("en", "hi"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.home"))


@main_bp.route("/")
def home():
    lang = _lang()
    return render_template(
        "index.html",
        courses=get_courses(lang),
        why_choose_us=get_why_choose_us(lang),
        quick_info=get_quick_info(lang),
        gallery=get_gallery(lang)[:6],
        notices=get_notices(lang)[:4],
        active_page="home",
    )


@main_bp.route("/about-institute")
def about():
    return render_template("about.html", achievements=get_achievements(_lang()), active_page="about")


@main_bp.route("/courses")
def courses():
    return render_template("courses.html", courses=get_courses(_lang()), active_page="courses")


@main_bp.route("/courses/<slug>")
def course_detail(slug):
    lang = _lang()
    course = get_course(slug, lang)
    if not course:
        abort(404)
    other_courses = [c for c in get_courses(lang) if c["slug"] != slug]
    return render_template(
        "course_detail.html", course=course, other_courses=other_courses, active_page="courses"
    )


@main_bp.route("/admissions", methods=["GET", "POST"])
def admissions():
    lang = _lang()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()

        required_fields = {
            "full_name": "err_full_name",
            "parent_name": "err_parent_name",
            "dob": "err_dob",
            "gender": "err_gender",
            "mobile": "err_mobile_required",
            "email": "err_email_required",
            "address": "err_address",
            "district": "err_district",
            "state": "err_state",
            "qualification": "err_qualification",
            "course": "err_course",
        }
        for field, key in required_fields.items():
            if not form_data.get(field, "").strip():
                errors[field] = translate(key, lang)

        mobile = form_data.get("mobile", "").strip()
        if mobile and not MOBILE_RE.match(mobile):
            errors["mobile"] = translate("err_mobile_invalid", lang)

        email = form_data.get("email", "").strip()
        if email and not EMAIL_RE.match(email):
            errors["email"] = translate("err_email_invalid", lang)

        course_slug = form_data.get("course", "")
        if course_slug and not get_course(course_slug, lang):
            errors["course"] = translate("err_course_invalid", lang)

        photo_file = request.files.get("photograph")
        document_file = request.files.get("documents")

        if photo_file and photo_file.filename and not _allowed_file(photo_file.filename, ALLOWED_IMAGE_EXT):
            errors["photograph"] = translate("err_photograph", lang)

        if document_file and document_file.filename and not _allowed_file(document_file.filename, ALLOWED_DOC_EXT):
            errors["documents"] = translate("err_documents", lang)

        if not errors:
            photo_filename = _save_upload(photo_file, ALLOWED_IMAGE_EXT)
            document_filename = _save_upload(document_file, ALLOWED_DOC_EXT)

            admission = Admission(
                full_name=form_data["full_name"].strip(),
                parent_name=form_data["parent_name"].strip(),
                dob=form_data["dob"].strip(),
                gender=form_data["gender"].strip(),
                mobile=mobile,
                email=email,
                address=form_data["address"].strip(),
                district=form_data["district"].strip(),
                state=form_data["state"].strip(),
                qualification=form_data["qualification"].strip(),
                course=get_course(course_slug, lang)["title"],
                photo_filename=photo_filename,
                document_filename=document_filename,
            )
            db.session.add(admission)
            db.session.commit()

            flash(translate("admissions_submitted_alert", lang), "success")
            return redirect(url_for("main.admissions", submitted=1))

        flash(translate("err_form_general", lang), "danger")

    submitted = request.args.get("submitted") == "1"
    return render_template(
        "admissions.html",
        courses=get_courses(lang),
        states=get_states(lang),
        errors=errors,
        form_data=form_data,
        submitted=submitted,
        active_page="admissions",
    )


@main_bp.route("/placement")
def placement():
    return render_template("placement.html", active_page="placement")


@main_bp.route("/facilities")
def facilities():
    return render_template("facilities.html", facilities=get_facilities(_lang()), active_page="facilities")


@main_bp.route("/gallery")
def gallery():
    lang = _lang()
    return render_template(
        "gallery.html", gallery=get_gallery(lang), categories=get_gallery_categories(lang), active_page="gallery"
    )


@main_bp.route("/notices")
def notices():
    lang = _lang()
    all_categories = get_notice_categories(lang)
    category = request.args.get("category", all_categories[0])
    query = request.args.get("q", "").strip().lower()

    filtered = get_notices(lang)
    if category and category != all_categories[0]:
        filtered = [n for n in filtered if n["category"] == category]
    if query:
        filtered = [n for n in filtered if query in n["title"].lower() or query in n["description"].lower()]

    return render_template(
        "notices.html",
        notices=filtered,
        categories=all_categories,
        selected_category=category,
        query=query,
        active_page="notices",
    )


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    lang = _lang()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()

        if not form_data.get("name", "").strip():
            errors["name"] = translate("err_name", lang)
        email = form_data.get("email", "").strip()
        if not email:
            errors["email"] = translate("err_email_required", lang)
        elif not EMAIL_RE.match(email):
            errors["email"] = translate("err_email_invalid", lang)
        if not form_data.get("message", "").strip():
            errors["message"] = translate("err_message", lang)

        if not errors:
            msg = ContactMessage(
                name=form_data["name"].strip(),
                email=email,
                phone=form_data.get("phone", "").strip(),
                subject=form_data.get("subject", "").strip(),
                message=form_data["message"].strip(),
            )
            db.session.add(msg)
            db.session.commit()
            flash(translate("contact_submitted_alert", lang), "success")
            return redirect(url_for("main.contact", submitted=1))

        flash(translate("err_form_general", lang), "danger")

    submitted = request.args.get("submitted") == "1"
    return render_template(
        "contact.html", errors=errors, form_data=form_data, submitted=submitted, active_page="contact"
    )


@main_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("legal/privacy_policy.html", active_page="")


@main_bp.route("/terms-conditions")
def terms_conditions():
    return render_template("legal/terms_conditions.html", active_page="")


@main_bp.route("/disclaimer")
def disclaimer():
    return render_template("legal/disclaimer.html", active_page="")


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html", active_page=""), 404
