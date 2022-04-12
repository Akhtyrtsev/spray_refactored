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

ADDRESS_TYPES = [
    ('For appointment', 'For appointment'),
    ('For Valet', 'For Valet'),
]

CANCELLED_BY_CHOICES = [
    ('Admin', 'Admin'),
    ('Client', 'Client'),
    ('Valet', 'Valet'),
]

APPOINTMENT_MICRO_STATUSES = [
    ('Valet on my way', 'Valet on my way'),
    ('Check In', 'Check In'),
    ('Working', 'Working'),
    ('No show', 'No show'),
]

REFUND_CHOICES = [
    ('no', 'no'),
    ('full', 'full'),
    ('1/2', '1/2'),
]

APPOINTMENT_STATUSES = [
    ('New', 'New'),
    ('Pending', 'Pending'),
    ('Upcoming', 'Upcoming'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled')
]
