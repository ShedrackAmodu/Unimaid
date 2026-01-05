from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile, StaffMember
from catalog.models import Genre, Publisher, Author, Book, Copy
from blog.models import Category, Tag, Post
from events.models import Event
from repository.models import Collection, Document
from circulation.models import Loan, Reservation
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the library system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create Genres
        genres = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Literature', 'Technology', 'Mathematics', 'Philosophy']
        genre_objects = []
        for genre_name in genres:
            from django.utils.text import slugify
            genre, created = Genre.objects.get_or_create(
                name=genre_name,
                defaults={'slug': slugify(genre_name)}
            )
            if not created and not genre.slug:
                genre.slug = slugify(genre_name)
                genre.save()
            genre_objects.append(genre)
            if created:
                self.stdout.write(f'Created genre: {genre_name}')

        # Create Publishers
        publishers = ['Oxford University Press', 'Cambridge University Press', 'Penguin Books', 'HarperCollins', 'Random House']
        publisher_objects = []
        for pub_name in publishers:
            from django.utils.text import slugify
            publisher, created = Publisher.objects.get_or_create(
                name=pub_name,
                defaults={'slug': slugify(pub_name)}
            )
            if not created and not publisher.slug:
                publisher.slug = slugify(pub_name)
                publisher.save()
            publisher_objects.append(publisher)
            if created:
                self.stdout.write(f'Created publisher: {pub_name}')

        # Create Authors
        authors_data = [
            ('Chinua', 'Achebe', 'Nigerian'),
            ('Wole', 'Soyinka', 'Nigerian'),
            ('Albert', 'Einstein', 'German'),
            ('Stephen', 'Hawking', 'British'),
            ('Jane', 'Austen', 'British'),
            ('Charles', 'Dickens', 'British'),
        ]
        author_objects = []
        for first, last, nationality in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={'nationality': nationality}
            )
            author_objects.append(author)
            if created:
                self.stdout.write(f'Created author: {first} {last}')

        # Create Books
        books_data = [
            ('Things Fall Apart', '9780385474542', 'A classic novel about pre-colonial Nigeria'),
            ('A Brief History of Time', '9780553380163', 'A popular science book about cosmology'),
            ('Pride and Prejudice', '9780141439518', 'A romantic novel of manners'),
            ('Great Expectations', '9780141439563', 'A bildungsroman by Charles Dickens'),
            ('The Theory of Relativity', '9780486417148', 'Einstein\'s groundbreaking work'),
            ('Death and the King\'s Horseman', '9780393323184', 'A play by Wole Soyinka'),
        ]
        
        for title, isbn, description in books_data:
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'isbn': isbn,
                    'description': description,
                    'genre': random.choice(genre_objects),
                    'publisher': random.choice(publisher_objects),
                    'publication_date': timezone.now().date() - timedelta(days=random.randint(365, 3650)),
                    'total_copies': random.randint(1, 5),
                    'available_copies': random.randint(0, 3),
                    'is_active': True,
                    'is_featured': random.choice([True, False]),
                }
            )
            if created:
                # Add authors
                book.authors.add(random.choice(author_objects))
                # Create copies
                for i in range(book.total_copies):
                    Copy.objects.create(
                        book=book,
                        barcode=f'{isbn}-{i+1}',
                        status='available' if i < book.available_copies else 'on_loan',
                        location='Main Library'
                    )
                self.stdout.write(f'Created book: {title}')

        # Create Blog Categories and Posts
        category, _ = Category.objects.get_or_create(name='News', defaults={'slug': 'news'})
        tag, _ = Tag.objects.get_or_create(name='library', defaults={'slug': 'library'})
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            post, created = Post.objects.get_or_create(
                title='Welcome to Ramat Library',
                defaults={
                    'author': admin_user,
                    'category': category,
                    'content': 'Welcome to the new Ramat Library management system. We are excited to serve you better with our enhanced digital services.',
                    'excerpt': 'Welcome to the new Ramat Library management system.',
                    'is_published': True,
                    'published_date': timezone.now(),
                }
            )
            if created:
                post.tags.add(tag)
                self.stdout.write('Created blog post')

        # Create Collections and Repository Documents
        collection, _ = Collection.objects.get_or_create(
            name='Theses',
            defaults={'slug': 'theses', 'description': 'Student theses and dissertations'}
        )
        
        if admin_user:
            doc, created = Document.objects.get_or_create(
                title='Sample Thesis Document',
                defaults={
                    'document_type': 'thesis',
                    'collection': collection,
                    'author': 'Sample Author',
                    'department': 'Computer Science',
                    'year': 2024,
                    'abstract': 'This is a sample thesis document for demonstration purposes.',
                    'access_level': 'open',
                    'is_active': True,
                    'is_approved': True,
                    'submitted_by': admin_user,
                }
            )
            if created:
                self.stdout.write('Created repository document')

        # Create Events
        event, created = Event.objects.get_or_create(
            title='Library Orientation Workshop',
            defaults={
                'description': 'An orientation workshop for new library users',
                'event_type': 'workshop',
                'start_date': timezone.now() + timedelta(days=7),
                'end_date': timezone.now() + timedelta(days=7, hours=2),
                'location': 'Main Library Conference Room',
                'capacity': 50,
                'requires_registration': True,
                'is_published': True,
                'organizer': admin_user,
            }
        )
        if created:
            self.stdout.write('Created event')

        # Create Staff Members
        if admin_user:
            staff, created = StaffMember.objects.get_or_create(
                user=admin_user,
                defaults={
                    'position': 'Library Director',
                    'department': 'Administration',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write('Created staff member')

        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
        self.stdout.write(self.style.SUCCESS('You can now login with the admin account and explore the system.'))

