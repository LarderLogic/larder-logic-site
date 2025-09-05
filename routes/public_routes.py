from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
@public_bp.route("/index")
def index():
    return render_template("index.html")

@public_bp.route("/mise")
def mise():
    return render_template("mise.html")


@public_bp.route("/method")
def method():
    return render_template("method.html")


@public_bp.route("/mastery")
def mastery():
    return render_template("mastery.html")
