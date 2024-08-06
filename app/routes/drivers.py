from flask import Blueprint, jsonify, request
from sqlalchemy import select

from .. import db
from .. import models
from .. import schemas

drivers_bp = Blueprint('drivers_bp', __name__)


@drivers_bp.route('/drivers', methods=['GET', 'POST'])
def drivers():
    if request.method == 'GET':
        try:
            query = (
                select(models.Driver)
            )
            drivers = db.session.execute(query).scalars().all()
            drivers_dto = [
                schemas.DriverDto.from_orm(driver).dict() for driver in drivers
            ]

            return jsonify(drivers_dto), 200

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'POST':
        try:
            driver_dto = request.get_json()
            driver = models.Driver(
                full_name=driver_dto['full_name'],
                phone_number=driver_dto['phone_number'],
                car_type=driver_dto['car_type']
            )

            db.session.add(driver)
            db.session.commit()

            return jsonify({'message': 'CREATED'}), 201

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500


@drivers_bp.route('/drivers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def driver(id):
    if request.method == 'GET':
        try:
            driver = models.Driver.query.get(id)
            if not driver:
                return jsonify({'error': 'Driver not found'}), 404

            driver_dto = schemas.DriverDto.from_orm(driver).dict()
            return jsonify({"driver": driver_dto}), 200

        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'PUT':
        try:
            driver = models.Driver.query.get(id)

            if not driver:
                return jsonify({'error': 'Driver not found'}), 404

            driver_dto = request.get_json()

            if 'full_name' in driver_dto:
                driver.full_name = driver_dto['full_name']
            if 'phone_number' in driver_dto:
                driver.phone_number = driver_dto['phone_number']
            if 'car_type' in driver_dto:
                driver.car_type = driver_dto['car_type']

            db.session.commit()

            return jsonify({'message': 'UPDATED'}), 200
        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500

    if request.method == 'DELETE':
        try:
            driver = models.Driver.query.get(id)
            if driver:
                db.session.delete(driver)
                db.session.commit()

                return jsonify({'message': 'DELETED'}), 204
            else:
                return jsonify({'error': 'Driver not found'}), 404
        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error', 'message': str(ex)}), 500
