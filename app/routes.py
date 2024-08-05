from flask import current_app as app
from flask import jsonify, request
from sqlalchemy import text, select

from . import db
from . import models
from . import schemas


@app.route('/')
def index():
    version_query = db.session.execute(text("SELECT version()")).fetchone()
    postgres_version = version_query[0] if version_query else "Unknown"

    data = {
        'postgresql version': postgres_version,
        'flask version': '3.0.3'
    }

    return jsonify(data)


@app.route('/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'GET':
        try:
            query = (
                select(models.Employee)
            )
            employees = db.session.execute(query).scalars().all()
            employees_dto = [
                schemas.EmployeeDto.from_orm(employee).dict() for employee in employees
            ]

            return jsonify(employees_dto), 200

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'POST':
        try:
            employee_dto = request.get_json()
            employee = models.Employee(
                full_name=employee_dto['full_name'],
                post=employee_dto['post'],
                phone_number=employee_dto['phone_number'],
                email=employee_dto['email']
            )

            db.session.add(employee)
            db.session.commit()

            return jsonify({'message': 'CREATED'}), 201

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500


@app.route('/employees/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def employee(id):
    if request.method == 'GET':
        try:
            employee = models.Employee.query.get(id)
            employee_dto = schemas.EmployeeDto.from_orm(employee).dict()

            if not employee:
                return jsonify({'error': 'Employee not found'}), 404

            return jsonify({"employee": employee_dto}), 200

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'PUT':
        try:
            employee = models.Employee.query.get(id)

            if not employee:
                return jsonify({'error': 'Employee not found'}), 404

            employee_dto = request.get_json()

            if employee_dto['full_name']:
                employee.full_name = employee_dto['full_name']
            if employee_dto['post']:
                employee.post = employee_dto['post']
            if employee_dto['phone_number']:
                employee.phone_number = employee_dto['phone_number']
            if employee_dto['email']:
                employee.email = employee_dto['email']

            db.session.commit()

            return jsonify({'message': 'UPDATED'}), 200
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'DELETE':
        try:
            employee = models.Employee.query.get(id)
            if employee:
                db.session.delete(employee)
                db.session.commit()

                return jsonify({'message': 'DELETED'}), 204
            else:
                return jsonify({'error': 'Employee not found'}), 404
        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500
