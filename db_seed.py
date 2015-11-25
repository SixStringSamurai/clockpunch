#!flask/bin/python
# This script seeds the database with some fake users, with fake clock-punch records.  One caveat: any testing requiring use of a real user account has to be done with one that was registered using the openID method exposed through the webpage itself, and this account has to be created before this script is run. Giving said user manager-privileges can be done by this script, but it is not currently implemented that way, and has to be done manually through the console.

from app import db, models
import datetime


print( "Adding seed-data to the database.")

user_seeds = [{'nickname': 'Kayla Carlyle', 'email': 'kaylacarylyle@yahoo.com', 'employee_number': 123456, 'is_manager': True},
{'nickname': 'Mike Rotch', 'email': 'mrotch@gmail.com', 'employee_number': 345678, 'is_manager': False}, 
{'nickname': 'Danielle Reguser', 'email': 'daneillereguser@gmail.com', 'employee_number': 456789, 'is_manager': False}]

clock_punches = [{'timestamp': datetime.datetime.fromtimestamp(1447866000), 'in_or_out':'IN', 'notes':'Starting opening shift'},
	{'timestamp': datetime.datetime.fromtimestamp(1447876800), 'in_or_out':'OUT', 'notes':'Beginning one-hour lunch break'},
	{'timestamp': datetime.datetime.fromtimestamp(1447880400), 'in_or_out':'IN', 'notes':'Back from lunch'},
    {'timestamp': datetime.datetime.fromtimestamp(1447894800), 'in_or_out':'OUT', 'notes':'Out for the day, signed off by K.C.'}
    ]

#remove previous users (except the main admin one)
users = models.User.query.all()
punches = models.Punch.query.all()
for u in users[1:]:
	db.session.delete(u)
for p in punches:
	db.session.delete(p)
db.session.commit()


#seed punches for the main admin user
u = models.User.query.get(1)
u.is_manager = True
db.session.add(u)
db.session.commit()
for cp in clock_punches:
	punch = models.Punch(timestamp=cp['timestamp'], in_or_out=cp['in_or_out'], notes=cp['notes'], author=u)
	db.session.add(punch)
	db.session.commit()
#seed for the rest of the dummy users and punches
for u in user_seeds:
	user = models.User(nickname=u['nickname'], email=u['email'], employee_number=u['employee_number'], is_manager=u['is_manager'])
	db.session.add(user)
	db.session.commit()
	for cp in clock_punches:
		punch = models.Punch(timestamp=cp['timestamp'], in_or_out=cp['in_or_out'], notes=cp['notes'], author=user)
		db.session.add(punch)
		db.session.commit()

users = models.User.query.all()
punches = models.Punch.query.all()
print('Done. DB dump follows:\n')
print('========== Users ==========')
print(users)
print('====== Clock Punches ======')
print(punches)
	

