import random
from faker import Faker
from models import db, Hero, Power, HeroPower
from app import app

fake = Faker()

with app.app_context():
    # the rest of your seeding code goes here

    # Create some fake powers
    powers = []
    for _ in range(10):
        power = Power(
            name=fake.word(),
            description=fake.paragraph(nb_sentences=5)  # ensure the description is long enough
        )
        powers.append(power)
        db.session.add(power)

    db.session.commit()

    # Create some fake heroes and associate them with random powers
    for _ in range(20):
        hero = Hero(
            name=fake.name(),
            super_name=fake.user_name()
        )

        # Associating hero with random powers
        hero_powers = []
        for power in random.sample(powers, k=random.randint(1, 4)):  # assigning 1 to 4 powers randomly to each hero
            hero_power = HeroPower(
                strength=random.choice(['Strong', 'Weak', 'Average']),
                power=power
            )
            hero_powers.append(hero_power)
            db.session.add(hero_power)

        hero.powers = hero_powers
        db.session.add(hero)

    db.session.commit()