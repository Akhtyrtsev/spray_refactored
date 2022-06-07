# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

ADDRESS_TYPES = [
    ('Client', 'Client'),
    ('Valet', 'Valet'),
]

USER_TYPE_CHOICES = [
    (1, 'superuser'),
    (2, 'staff'),
    (3, 'client'),
    (4, 'valet'),
]

CITY_CHOICES = [
    ('Los Angeles', 'Los Angeles'),
    ('Las Vegas', 'Las Vegas'),
    ('Miami', 'Miami')
]

CUSTOMER_STATUSES = [
    ('New', 'New'),
    ('Returning', 'Returning'),
    ('Member', 'Member'),
    ('Subscriber', 'Subscriber'),
]

TYPES_OF_REQUESTS = [
    ('Re-assign', 'Re-assign'),
    ('NotOnCall', 'NotOnCall'),
    ('Changed', 'Changed'),
    ('Feed', 'Feed'),
    ('Automatic', 'Automatic')
]
