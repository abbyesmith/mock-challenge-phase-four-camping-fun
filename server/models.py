from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


# class Camper(db.Model, SerializerMixin):
#     __tablename__ = 'campers'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False, unique=True)
#     age = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
#     signups = db.relationship('Signup', backref = "campers")
#     # serialize_rules = ('-signups.campers')

#     @validates('age')
#     def validates_age(self, key, value):
#         if value < 8:
#             raise ValueError ("Camper is too young, must be between 8 and 18 years old.")
#         elif value > 18:
#             raise ValueError ("Camper is too old, must be between 8 and 18 years old.")
#         return value


# class Activity(db.Model, SerializerMixin):
#     __tablename__ = 'activities'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     difficulty = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
#     signups = db.relationship('Signup', backref = "activities")
#     # serialize_rules = ('-signups.activities')
#     # again, this serialize rule resulted in a ' ' error. Do not know why.


# class Signup(db.Model, SerializerMixin):
#     __tablename__ = 'signups'

#     id = db.Column(db.Integer, primary_key=True)
#     camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
#     activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
#     time = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
#     # serialize_rules = ('-managers.players', '-teams.players')
#     serialize_rules = ('-activities.signups', '-campers.signups')

#     @validates('time')
#     def validates_age(self, key, value):
#         if value < 0:
#             raise ValueError ("Not a valid activity time.")
#         elif value > 23:
#             raise ValueError ("Not a valid activity time.")
#         return value
    
#     @validates('activity_id')
#     def validate_activity_id(self, key, value):
#         activities = Activity.query.all()
#         activity_ids = [activity.id for activity in activities]
#         if not value in activity_ids:
#             raise ValueError("Not a valid activity")
#         return value
    
#     @validates('camper_id')
#     def validate_camper_id(self, key, value):
#         campers = Camper.query.all()
#         camper_ids = [camper.id for camper in campers]
#         if not value in camper_ids:
#             raise ValueError("Invalid camper ID")
#         return value


# My code didn't work. Use back_populates. More reliable.

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    signups = db.relationship('Signup', back_populates='camper')
    activities = association_proxy('signups', 'activity')
    serialize_rules = ('-signups', '-created_at',
                       '-updated_at', '-activities.created_at', '-activities.updated_at', '-activities.campers')

    @validates('age')
    def validates_age(self, key, value):
        if value < 8:
            raise ValueError("Camper too young.")
        elif value > 18:
            raise ValueError("Camper too old.")
        return value


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    signups = db.relationship(
        'Signup', back_populates='activity', cascade="all,delete, delete-orphan")
    campers = association_proxy('signups', 'camper')
    serialize_rules = ('-signups',
                       '-campers.activities', '-created_at', '-updated_at')


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    serialize_rules = ('-camper.signups', '-activity.signups',
                       '-camper.activities', '-activity.campers', '-created_at', '-updated_at')

    @validates('camper_id')
    def validates_camper_id(self, key, value):
        campers = Camper.query.all()
        camper_ids = [camper.id for camper in campers]
        if not value in camper_ids:
            raise ValueError("Not a camper.")
        return value

    @validates('activity_id')
    def validates_activity_id(self, key, value):
        activities = Activity.query.all()
        activity_ids = [activity.id for activity in activities]
        if not value in activity_ids:
            raise ValueError("Not an activity.")
        return value
