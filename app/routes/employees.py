from flask import Blueprint, abort, jsonify, request, render_template, flash
from flask_login import login_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db, logger
from .. import models
from .. import schemas
from ..models import Employee
from ..services.check_post import admin_required

employees_bp = Blueprint('employees_bp', __name__)


@employees_bp.route('/employees', methods=['GET', 'POST'])
@login_required
@admin_required
def employees():
    logger.debug(f'{request.method} /employees')

    if request.method == 'POST':
        try:
            employee = models.Employee(
                full_name=request.form.get('full_name'),
                post=request.form.get('post'),
                phone_number=request.form.get('phone_number'),
                email=request.form.get('email')
            )

            db.session.add(employee)
            db.session.commit()

            return jsonify({'message': 'CREATED'}), 201

        except SQLAlchemyError as ex:
            db.session.rollback()
            logger.exception(ex)
            abort(500)

    try:
        query = (
            select(models.Employee)
        )
        employees = db.session.execute(query).scalars().all()
        employees_dto = [
            schemas.EmployeeDto.from_orm(employee).dict() for employee in employees
        ]

        return render_template('employees.html', employees=employees_dto), 200

    except SQLAlchemyError as ex:
        db.session.rollback()
        logger.exception(ex)
        abort(500)


@employees_bp.route('/employees/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def employee(id):
    logger.debug(f'{request.method} /employees/{id}')
    if request.method == 'GET':
        try:
            employee = models.Employee.query.get(id)
            if not employee:
                abort(404)

            employee_dto = schemas.EmployeeDto.from_orm(employee).dict()
            return render_template('employee_card.html', empl=employee_dto), 200

        except SQLAlchemyError as ex:
            db.session.rollback()
            logger.exception(ex)
            abort(500)

    if request.method == 'PUT':
        try:
            employee = models.Employee.query.get(id)

            if not employee:
                abort(404)

            employee_dto = request.get_json()

            if 'full_name' in employee_dto:
                employee.full_name = employee_dto['full_name']
            if 'post' in employee_dto:
                employee.post = employee_dto['post']
            if 'phone_number' in employee_dto:
                employee.phone_number = employee_dto['phone_number']
            if 'email' in employee_dto:
                employee.email = employee_dto['email']

            db.session.commit()

            return jsonify({'message': 'UPDATED'}), 200
        except SQLAlchemyError as ex:
            db.session.rollback()
            logger.exception(ex)
            abort(500)

    if request.method == 'DELETE':
        try:
            employee = models.Employee.query.get(id)
            if employee:
                db.session.delete(employee)
                db.session.commit()
                flash('Сотрудник успешно удалён', 'success')
                return jsonify({'message': 'DELETED'}), 204
            else:
                abort(404)
        except SQLAlchemyError as ex:
            db.session.rollback()
            logger.exception(ex)
            abort(500)


@employees_bp.route('/search/employees/', methods=['GET'])
@login_required
@admin_required
def search():
    logger.debug(f'{request.method} /search/employees/')

    full_name = request.args.get('full_name')
    phone_number = request.args.get('phone_number')
    post = request.args.get('post')
    email = request.args.get('email')

    query = Employee.query

    if full_name:
        query = query.filter(Employee.full_name == full_name)
    if phone_number:
        query = query.filter(Employee.phone_number == phone_number)
    if post:
        query = query.filter(Employee.post == post)
    if email:
        query = query.filter(Employee.email == email)

    try:
        filter_employees = query.all()
        return render_template('found_employees.html', employees=filter_employees), 200

    except SQLAlchemyError as ex:
        logger.exception(ex)
        abort(500)
