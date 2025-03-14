import random
import pandas as pd
import sqlite3
from faker import Faker
from datetime import datetime, timedelta


conn = sqlite3.connect("ticketer.db")
cursor = conn.cursor()
fake = Faker()
organizations = []
events = []
ticket_types = []



def generate_organizations(n: int =10):
    categories = ["Media", "Business", "Sports", "Entertainment", "Education"]
    employee_sizes = ["1-50", "51-100", "101-500", "500+"]

    for _ in range(n):
        company_name = fake.company()
        company_email = fake.email()
        company_desc = fake.catch_phrase()
        category = random.choice(categories)
        logo = fake.image_url()
        employee_size = random.choice(employee_sizes) 
        total_ticket_sales = 0
        total_ticket_revenue = 0.0

        cursor.execute('''
            INSERT INTO Organization (name, email, description, category, logo, employee_size, total_ticket_sales, total_ticket_revenue, date_joined)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name,
                company_email,
                company_desc,
                category,
                logo,
                employee_size,
                total_ticket_sales,
                total_ticket_revenue,
                datetime.today().timestamp()
            )
        )
        organizations.append(cursor.lastrowid)

def generate_events(n: int=25):

    for _ in range(n):  
        organization = random.choice(organizations)
        event_name = fake.catch_phrase()
        event_desc = fake.paragraph()
        location_coords = "%d, %d" % (fake.latitude(), fake.longitude())
        maximum_size = random.randint(50, 1000)
        start_date = fake.date_time_between(start_date='-1y', end_date='+1y')
        end_date = start_date + timedelta(hours=random.randint(1, 24))
        delta = (end_date - start_date).total_seconds()
        duration = int(delta)/3600 # to hours

        cursor.execute('''
            INSERT INTO Event (organization_id, name, description, location_coords, maximum_size, start_date, end_date, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                organization,
                event_name,
                event_desc,
                location_coords,
                maximum_size,
                start_date.timestamp(),
                end_date.timestamp(),
                duration 
        ))
        events.append(cursor.lastrowid) 

def generate_ticket_type():
    for event in events:
        for _ in range(4):
            name = fake.word().capitalize() + " Ticket"
            description = fake.sentence()
            price = round(random.uniform(10, 500), 2)
            created_at = datetime.today().timestamp()

            cursor.execute('''
                INSERT INTO EventTicketType (event_id, name, description, price, created_at)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    event,
                    name,
                    description,
                    price,
                    created_at
            ))
            ticket_types.append((event, cursor.lastrowid)) 

def generate_tickets(n: int=1000):
    for event, ticket_type in ticket_types:
        for _ in range(random.randint(10, 20)):  # 10-20 tickets per ticket type
            reference = fake.uuid4()
            name = fake.name()
            email = fake.email()
            expired = random.choice([True, False])
            created_at = datetime.today().timestamp()
            cursor.execute('''
            INSERT INTO EventTicket (reference, event_id, event_ticket_type_id, name, email, expired, created_at, expired_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reference,
                event,
                ticket_type,
                name,
                email,
                expired,
                datetime.today().timestamp(),
                (created_at + 20000) if expired else None
            ))

def generate_coupons(n: int=20):
    for event in events:
        for _ in range(random.randint(1, 3)): 
            code = fake.lexify(text='??????').upper()
            coupon_type = random.choice(["percentage", "amount"])
            coupon_value = random.randint(10, 100) if coupon_type == "percentage" else round(random.uniform(10, 500), 2)
            active = random.choice([True, False])
            cursor.execute('''
            INSERT INTO EventCoupon (event_id, coupon_code, coupon_type, coupon_value, is_active, event_ticket_type_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event,
                code,
                coupon_type,
                coupon_value,
                active,
                random.choice(ticket_types)[1]
            ))

# Commit and close
generate_organizations()
generate_events()
generate_ticket_type()
generate_tickets()
generate_coupons()
print("Closing connection...")
conn.commit()
conn.close()
print("Data generated.")