from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="Student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lost_items = db.relationship("LostItem", backref="reporter", lazy=True)
    found_items = db.relationship("FoundItem", backref="reporter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


class LostItem(db.Model):
    __tablename__ = "lost_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(200), default="")
    image_path = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(30), default="open")  # open | matched | closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "image_path": self.image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class FoundItem(db.Model):
    __tablename__ = "found_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(200), default="")
    image_path = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(30), default="open")  # open | matched | closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "image_path": self.image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey("lost_items.id"), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey("found_items.id"), nullable=False)
    text_score = db.Column(db.Float, default=0.0)
    image_score = db.Column(db.Float, default=0.0)
    combined_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="pending")  # pending | confirmed | rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lost_item = db.relationship("LostItem")
    found_item = db.relationship("FoundItem")

    def to_dict(self):
        return {
            "id": self.id,
            "lost_item": self.lost_item.to_dict(),
            "found_item": self.found_item.to_dict(),
            "text_score": round(self.text_score, 3),
            "image_score": round(self.image_score, 3),
            "combined_score": round(self.combined_score, 3),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
