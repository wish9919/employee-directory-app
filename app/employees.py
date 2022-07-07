from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from app.auth import login, login_required
from app.db import get_db

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.route("/")
def index():
    db = get_db()
    employees = db.execute(
        'SELECT id, first_name, last_name, designation, note, created_at'
        ' FROM employees'
        ' ORDER BY created_at DESC '
    ).fetchall()
    return render_template('employees/index.html', employees=employees)


@bp.route("/create", methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        designation = request.form["designation"]
        note = request.form["note"]
        error = None

        if not first_name:
            error = 'First name is required!'
        elif not last_name:
            error = 'Last name is required!'
        elif not designation:
            error = 'Designation is required!'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO employees (first_name, last_name, designation, note)'
                ' VALUES (?, ?, ?, ?)', (first_name,
                                         last_name, designation, note)
            )
            db.commit()
            return redirect(url_for("employees.index"))

    return render_template('employees/create.html')


def get_employee(id):
    employee = get_db().execute(
        'SELECT id, first_name, last_name, designation, note, created_at'
        ' FROM employees'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if employee is None:
        abort(404, f"Employee id {id} doesn't exist.")

    return employee


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    employee = get_employee(id)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        designation = request.form["designation"]
        note = request.form["note"]
        error = None

        if not first_name:
            error = 'First name is required.'
        elif not last_name:
            error = 'Last name is required.'
        elif not designation:
            error = "Designation is required."
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE employees SET first_name = ?, last_name = ?, designation = ?, note = ?'
                ' WHERE id = ?',
                (first_name, last_name, designation, note, id,)
            )
            db.commit()
            return redirect(url_for('employees.index'))

    return render_template('employees/update.html', employee=employee)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_employee(id)
    db = get_db()
    db.execute('DELETE FROM employees WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('employees.index'))
