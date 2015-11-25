from app import db
from hashlib import md5


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    punches = db.relationship('Punch', backref='author', lazy='dynamic')
    employee_number = db.Column(db.Integer)
    is_manager = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return 'User Nickname: %r, Email: %r, Employee Number: %r, Manager: %r' % (self.nickname, self.email, self.employee_number, self.is_manager)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)


class Punch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    in_or_out = db.Column(db.String(64))
    notes = db.Column(db.String(128)) #for storage of intervals or notes on changes
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '%s Punch-%s at %s, Notes: %s>' % (self.author, self.in_or_out, self.timestamp, self.notes)



