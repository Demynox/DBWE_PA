from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from ..extensions import db
from ..models.user import User
from ..services.auth import create_api_token_for_user

bp = Blueprint("auth", __name__)
PAYMENT_METHOD_OPTIONS = {"Mastercard", "Visa", "Twint", "PayPal"}


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        role = request.form.get("role", "rider")
        payment_method = request.form.get("payment_method", "").strip()

        if not first_name or not last_name or not username or not email or not password:
            flash("Bitte alle Pflichtfelder ausfüllen.", "error")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Das Passwort muss mindestens 6 Zeichen lang sein.", "error")
            return render_template("auth/register.html")

        if password != password_confirm:
            flash("Die beiden Passwörter stimmen nicht überein.", "error")
            return render_template("auth/register.html")

        if role not in {"rider", "provider"}:
            role = "rider"

        if role == "rider" and not payment_method:
            flash("Für Fahrerprofile ist ein Zahlungsmittel erforderlich.", "error")
            return render_template("auth/register.html")

        if role == "rider" and payment_method not in PAYMENT_METHOD_OPTIONS:
            flash("Bitte ein gültiges Zahlungsmittel auswählen.", "error")
            return render_template("auth/register.html")

        if role == "provider":
            payment_method = ""

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Benutzername oder E-Mail existiert bereits.", "error")
            return render_template("auth/register.html")

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=role,
            payment_method=payment_method or None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Dein Konto ist jetzt aktiv.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            or_(
                User.email == login_value.lower(),
                User.username == login_value,
            )
        ).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Du bist jetzt angemeldet.", "success")
            return redirect(url_for("main.index"))

        flash("Die Anmeldung konnte nicht abgeschlossen werden.", "error")

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest erfolgreich abgemeldet.", "success")
    return redirect(url_for("main.index"))


@bp.route("/api-token", methods=["GET", "POST"])
@login_required
def api_token():
    token = None
    if request.method == "POST":
        token = create_api_token_for_user(current_user)
        flash("Ein neuer API-Token wurde erstellt. Bitte sichere ihn direkt nach der Generierung.", "success")
    return render_template("auth/api_token.html", token=token)
