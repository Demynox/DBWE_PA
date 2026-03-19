from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models.scooter import Scooter

bp = Blueprint("scooters", __name__)


@bp.route("/")
@login_required
def list_scooters():
    status = request.args.get("status", "")
    query = Scooter.query.order_by(Scooter.id.desc())
    if status:
        query = query.filter_by(status=status)
    scooters = query.all()
    return render_template("scooters/list.html", scooters=scooters, status=status)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_scooter():
    if not current_user.can_manage_scooters():
        flash("Nur Anbieter dürfen Fahrzeuge verwalten.", "error")
        return redirect(url_for("scooters.list_scooters"))

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        model_name = request.form.get("model_name", "").strip()
        battery_level = request.form.get("battery_level", "100").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        city = request.form.get("city", "Zürich").strip()

        if not code or not model_name or not latitude or not longitude:
            flash("Bitte alle Felder ausfüllen.", "error")
            return render_template("scooters/create.html")

        if Scooter.query.filter_by(code=code).first():
            flash("Der Fahrzeugcode existiert bereits.", "error")
            return render_template("scooters/create.html")

        try:
            battery_level_value = int(battery_level)
            latitude_value = float(latitude)
            longitude_value = float(longitude)
        except ValueError:
            flash("Bitte gültige Zahlen für Akku und GPS-Koordinaten eingeben.", "error")
            return render_template("scooters/create.html")

        scooter = Scooter(
            code=code,
            model_name=model_name,
            battery_level=battery_level_value,
            latitude=latitude_value,
            longitude=longitude_value,
            city=city,
            provider=current_user,
        )
        db.session.add(scooter)
        db.session.commit()
        flash("Das Fahrzeug wurde erfasst.", "success")
        return redirect(url_for("scooters.list_scooters"))

    return render_template("scooters/create.html")


@bp.route("/<int:scooter_id>/edit", methods=["GET", "POST"])
@login_required
def edit_scooter(scooter_id):
    scooter = db.get_or_404(Scooter, scooter_id)

    # Ein Anbieter darf nur die eigenen Fahrzeuge bearbeiten.
    if not current_user.can_manage_scooters() or scooter.provider_id != current_user.id:
        flash("Du darfst dieses Fahrzeug nicht bearbeiten.", "error")
        return redirect(url_for("scooters.list_scooters"))

    if request.method == "POST":
        try:
            battery_level = int(request.form.get("battery_level", scooter.battery_level))
            latitude = float(request.form.get("latitude", scooter.latitude))
            longitude = float(request.form.get("longitude", scooter.longitude))
        except ValueError:
            flash("Bitte gültige Zahlen für Akku und GPS-Koordinaten eingeben.", "error")
            return render_template("scooters/edit.html", scooter=scooter)

        scooter.model_name = request.form.get("model_name", scooter.model_name).strip()
        scooter.battery_level = battery_level
        scooter.latitude = latitude
        scooter.longitude = longitude
        scooter.city = request.form.get("city", scooter.city).strip()
        scooter.status = request.form.get("status", scooter.status)
        db.session.commit()
        flash("Die Fahrzeugdaten wurden aktualisiert.", "success")
        return redirect(url_for("scooters.list_scooters"))

    return render_template("scooters/edit.html", scooter=scooter)


@bp.route("/<int:scooter_id>/delete", methods=["POST"])
@login_required
def delete_scooter(scooter_id):
    scooter = db.get_or_404(Scooter, scooter_id)

    if not current_user.can_manage_scooters() or scooter.provider_id != current_user.id:
        flash("Du darfst dieses Fahrzeug nicht entfernen.", "error")
        return redirect(url_for("scooters.list_scooters"))

    if scooter.status == "in_use":
        flash("Ein aktives Fahrzeug kann nicht entfernt werden.", "error")
        return redirect(url_for("scooters.list_scooters"))

    db.session.delete(scooter)
    db.session.commit()
    flash("Das Fahrzeug wurde entfernt.", "success")
    return redirect(url_for("scooters.list_scooters"))
