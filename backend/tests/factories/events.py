"""
Event factory for generating test data.
"""
import factory
from datetime import datetime, timezone, timedelta
from faker import Faker

from app.models.event import Event
from tests.factories.user import UserFactory

fake = Faker(['hu_HU', 'en_US'])


class EventFactory(factory.Factory):
    """Factory for creating Event instances."""
    
    class Meta:
        model = Event
    
    # Event fields
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3).rstrip('.'))
    occurrence = factory.LazyFunction(
        lambda: fake.date_time_between(
            start_date=datetime.now(timezone.utc), 
            end_date=datetime.now(timezone.utc) + timedelta(days=90),
            tzinfo=timezone.utc
        )
    )
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=500) if fake.boolean(chance_of_getting_true=70) else None)
    
    # User relationship - this will create a new user for each event
    user = factory.SubFactory(UserFactory)
    
    # Timestamps
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    # Soft delete
    deleted_at = None


class PastEventFactory(EventFactory):
    """Factory for creating past Event instances."""
    
    occurrence = factory.LazyFunction(
        lambda: fake.date_time_between(
            start_date=datetime.now(timezone.utc) - timedelta(days=90),
            end_date=datetime.now(timezone.utc) - timedelta(days=1),
            tzinfo=timezone.utc
        )
    )


class HungarianEventFactory(EventFactory):
    """Factory for creating Hungarian Event instances with local titles."""
    
    title = factory.LazyFunction(
        lambda: fake.random_element(elements=[
            "Csapatépítő tréning",
            "Projekt megbeszélés",
            "Ügyfél prezentáció",
            "Agilis review meeting",
            "Kódolós workshop",
            "Design thinking worksho",
            "Sprint planning",
            "Retrospektív",
            "All-hands meeting",
            "Tech talk",
            "Termék demó",
            "Stratégiai tervezés",
            "Mentoring session",
            "Networking event",
            "Hackathon",
        ])
    )


class WorkshopEventFactory(EventFactory):
    """Factory for creating Workshop Event instances."""
    
    title = factory.LazyFunction(
        lambda: fake.random_element(elements=[
            "Python Workshop",
            "React Development Training",
            "Database Design Workshop",
            "API Development Masterclass",
            "DevOps Best Practices",
            "Security Awareness Training",
            "Agile Methodology Workshop",
            "UI/UX Design Principles",
            "Machine Learning Basics",
            "Cloud Computing Fundamentals",
        ])
    )
    
    description = factory.LazyFunction(
        lambda: fake.paragraph(nb_sentences=5) + "\n\nKötelező előzetes regisztráció! Laptop szükséges."
    )


class MeetingEventFactory(EventFactory):
    """Factory for creating Meeting Event instances."""
    
    title = factory.LazyFunction(
        lambda: fake.random_element(elements=[
            "Weekly Standup",
            "Sprint Review",
            "Project Kickoff",
            "Quarterly Review",
            "Client Meeting",
            "Team Sync",
            "One-on-One",
            "Architecture Review",
            "Code Review Session",
            "Planning Meeting",
        ])
    )
    
    # Meetings are usually shorter and more frequent
    occurrence = factory.LazyFunction(
        lambda: fake.date_time_between(
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            tzinfo=timezone.utc
        )
    )


class DeletedEventFactory(EventFactory):
    """Factory for creating soft-deleted Event instances."""
    
    deleted_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
