from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item')  # Association proxy for related items

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'

    def serialize(self):
        """Serializes the customer, including reviews and items."""
        return {
            'id': self.id,
            'name': self.name,
            'items': [
                item.serialize_summary() for item in self.items if item is not None
            ],  # Graceful handling of None
            'reviews': [
                review.serialize_summary() for review in self.reviews or []
            ]  # Include a summary of each review
        }

    def serialize_summary(self):
        """Minimal serialization for nested use."""
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_dict(self):
        """Alias for serialize method to match expected naming."""
        return self.serialize()

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    reviews = db.relationship('Review', back_populates='item')

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'

    def serialize(self):
        """Serializes the item, including all reviews."""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'reviews': [review.serialize_summary() for review in self.reviews or []]  # Graceful handling
        }

    def serialize_summary(self):
        """Serializes the item with minimal details for nested use."""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
        }

    def to_dict(self):
        """Alias for serialize method to match expected naming."""
        return self.serialize()


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)

    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'

    def serialize(self):
        """Serializes the review, excluding reverse relationships."""
        return {
            'id': self.id,
            'comment': self.comment,
            'customer': self.customer.serialize_summary() if self.customer else None,
            'item': self.item.serialize_summary() if self.item else None,
        }

    def serialize_summary(self):
        """Serializes the review with minimal details for nested use."""
        return {
            'id': self.id,
            'comment': self.comment,
        }

    def to_dict(self):
        """Alias for serialize method to match expected naming."""
        return self.serialize()
