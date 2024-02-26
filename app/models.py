from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from app import db

class TransactionItem(db.Model):
    __tablename__ = 'transaction_item'
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    price_at_time_of_sale = db.Column(db.Float, nullable=False)

    transaction = db.relationship('Transaction', back_populates='transaction_items')
    item = db.relationship('Item', back_populates='transaction_items')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    closed = db.Column(db.Boolean, default=False, nullable=False)
    # Backref to transactions and screens
    transactions = db.relationship('Transaction', backref='event')
    screens = db.relationship('Screen', backref='event')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'))  # Assuming there's a Screen model
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Relationships
    transaction_items = db.relationship('TransactionItem', back_populates='transaction')
    screen = db.relationship('Screen', back_populates='transactions')  # Assuming there's a back_populates in Screen model

    def calculate_total(self):
        return sum(item.price_at_time_of_sale for item in self.transaction_items)


class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    # Add cascade option to automatically delete associated ScreenItems
    items = db.relationship('ScreenItem', back_populates='screen', cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', back_populates='screen')

class ScreenItem(db.Model):
    __tablename__ = 'screen_item'
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id', ondelete="CASCADE"), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    priority = db.Column(db.Integer)  # Additional field for priority

    screen = db.relationship('Screen', back_populates='items')
    item = db.relationship('Item', back_populates='screens')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    gl_code = db.Column(db.String(50), nullable=False)
    # No change needed here for cascading deletes from Screen to ScreenItem
    screens = db.relationship('ScreenItem', back_populates='item')
    transaction_items = db.relationship('TransactionItem', back_populates='item')

