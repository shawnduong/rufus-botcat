import sqlalchemy as db

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Load all things DB.
engine = db.create_engine("sqlite:///database.sqlite")
session = Session(engine)
base = declarative_base()

class Watcher(base):
	"""
	A single Discord user ID to CRN entry.
	"""

	__tablename__ = "watcher"

	id      = db.Column(db.Integer, primary_key=True)
	userID  = db.Column(db.Integer, nullable=False)
	CRN     = db.Column(db.Integer, nullable=False)

	def __init__(self, userID, CRN):

		self.userID  = userID
		self.CRN     = CRN

# Create the DB.
base.metadata.create_all(engine)
