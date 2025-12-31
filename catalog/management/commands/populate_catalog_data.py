from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import Genre, Author, Publisher, Book, BookCopy
import random


class Command(BaseCommand):
    help = "Populate the catalog with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Populating catalog with sample data...")

        # Create genres
        genres_data = [
            {"name": "Fiction", "description": "Fictional literature"},
            {"name": "Non-Fiction", "description": "Factual literature"},
            {"name": "Science Fiction", "description": "Science fiction books"},
            {"name": "Mystery", "description": "Mystery and detective novels"},
            {"name": "Romance", "description": "Romance novels"},
            {"name": "Biography", "description": "Biographical works"},
            {"name": "History", "description": "Historical books"},
            {"name": "Technology", "description": "Technology and computing"},
            {"name": "Self-Help", "description": "Self-improvement books"},
            {"name": "Children", "description": "Books for children"},
        ]

        genres = []
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_data["name"],
                defaults={"description": genre_data["description"]},
            )
            genres.append(genre)
            if created:
                self.stdout.write(f"Created genre: {genre.name}")

        # Create authors
        authors_data = [
            {"first_name": "George", "last_name": "Orwell"},
            {"first_name": "Jane", "last_name": "Austen"},
            {"first_name": "Harper", "last_name": "Lee"},
            {"first_name": "J.K.", "last_name": "Rowling"},
            {"first_name": "Stephen", "last_name": "King"},
            {"first_name": "Agatha", "last_name": "Christie"},
            {"first_name": "Isaac", "last_name": "Asimov"},
            {"first_name": "Maya", "last_name": "Angelou"},
            {"first_name": "Chimamanda Ngozi", "last_name": "Adichie"},
            {"first_name": "Wole", "last_name": "Soyinka"},
        ]

        authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=author_data["first_name"], last_name=author_data["last_name"]
            )
            authors.append(author)
            if created:
                self.stdout.write(f"Created author: {author.full_name}")

        # Create publishers
        publishers_data = [
            {"name": "Penguin Books", "website": "https://www.penguin.com"},
            {"name": "HarperCollins", "website": "https://www.harpercollins.com"},
            {"name": "Random House", "website": "https://www.randomhouse.com"},
            {"name": "Oxford University Press", "website": "https://www.oup.com"},
            {
                "name": "Cambridge University Press",
                "website": "https://www.cambridge.org",
            },
        ]

        publishers = []
        for pub_data in publishers_data:
            publisher, created = Publisher.objects.get_or_create(
                name=pub_data["name"], defaults={"website": pub_data["website"]}
            )
            publishers.append(publisher)
            if created:
                self.stdout.write(f"Created publisher: {publisher.name}")

        # Create books
        books_data = [
            {
                "title": "1984",
                "isbn": "9780451524935",
                "authors": [authors[0]],  # Orwell
                "publisher": publishers[0],  # Penguin
                "genres": [genres[0], genres[2]],  # Fiction, Sci-Fi
                "description": "A dystopian novel about totalitarianism and surveillance.",
                "publication_date": "1949-06-08",
                "pages": 328,
            },
            {
                "title": "Pride and Prejudice",
                "isbn": "9780141439518",
                "authors": [authors[1]],  # Austen
                "publisher": publishers[0],  # Penguin
                "genres": [genres[0], genres[4]],  # Fiction, Romance
                "description": "A romantic novel about Elizabeth Bennet and Mr. Darcy.",
                "publication_date": "1813-01-28",
                "pages": 432,
            },
            {
                "title": "To Kill a Mockingbird",
                "isbn": "9780061120084",
                "authors": [authors[2]],  # Lee
                "publisher": publishers[1],  # HarperCollins
                "genres": [genres[0]],  # Fiction
                "description": "A novel about racial injustice in the American South.",
                "publication_date": "1960-07-11",
                "pages": 376,
            },
            {
                "title": "Harry Potter and the Philosopher's Stone",
                "isbn": "9780747532699",
                "authors": [authors[3]],  # Rowling
                "publisher": publishers[1],  # HarperCollins
                "genres": [
                    genres[0],
                    genres[2],
                    genres[9],
                ],  # Fiction, Sci-Fi, Children
                "description": "A young wizard's adventures at Hogwarts School.",
                "publication_date": "1997-06-26",
                "pages": 223,
            },
            {
                "title": "The Shining",
                "isbn": "9780307743657",
                "authors": [authors[4]],  # King
                "publisher": publishers[2],  # Random House
                "genres": [genres[0], genres[3]],  # Fiction, Mystery
                "description": "A horror novel about a haunted hotel.",
                "publication_date": "1977-01-28",
                "pages": 447,
            },
            {
                "title": "Murder on the Orient Express",
                "isbn": "9780062693662",
                "authors": [authors[5]],  # Christie
                "publisher": publishers[1],  # HarperCollins
                "genres": [genres[0], genres[3]],  # Fiction, Mystery
                "description": "Detective Hercule Poirot solves a murder mystery.",
                "publication_date": "1934-01-01",
                "pages": 256,
            },
            {
                "title": "Foundation",
                "isbn": "9780553293357",
                "authors": [authors[6]],  # Asimov
                "publisher": publishers[1],  # HarperCollins
                "genres": [genres[0], genres[2]],  # Fiction, Sci-Fi
                "description": "A science fiction novel about the fall of the Galactic Empire.",
                "publication_date": "1951-05-01",
                "pages": 255,
            },
            {
                "title": "I Know Why the Caged Bird Sings",
                "isbn": "9780345514400",
                "authors": [authors[7]],  # Angelou
                "publisher": publishers[2],  # Random House
                "genres": [genres[5], genres[1]],  # Biography, Non-Fiction
                "description": "An autobiography by Maya Angelou.",
                "publication_date": "1969-01-01",
                "pages": 289,
            },
            {
                "title": "Americanah",
                "isbn": "9780307455925",
                "authors": [authors[8]],  # Adichie
                "publisher": publishers[2],  # Random House
                "genres": [genres[0]],  # Fiction
                "description": "A novel about Nigerian immigrants in America.",
                "publication_date": "2013-05-14",
                "pages": 477,
            },
            {
                "title": "The Lion and the Jewel",
                "isbn": "9780199115641",
                "authors": [authors[9]],  # Soyinka
                "publisher": publishers[3],  # Oxford
                "genres": [genres[0]],  # Fiction
                "description": "A play about cultural conflict in Nigeria.",
                "publication_date": "1959-01-01",
                "pages": 64,
            },
        ]

        books = []
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                title=book_data["title"],
                defaults={
                    "isbn": book_data["isbn"],
                    "publisher": book_data["publisher"],
                    "description": book_data["description"],
                    "publication_date": book_data["publication_date"],
                    "pages": book_data["pages"],
                },
            )

            if created:
                # Add many-to-many relationships
                book.authors.set(book_data["authors"])
                book.genres.set(book_data["genres"])
                book.save()
                self.stdout.write(f"Created book: {book.title}")

            books.append(book)

        # Create book copies (2-3 copies per book)
        for book in books:
            # Check how many copies already exist
            existing_copies = book.copies.count()
            copies_needed = max(0, random.randint(2, 4) - existing_copies)

            for i in range(copies_needed):
                copy_number = f"{book.id:04d}-{i+1:02d}"
                BookCopy.objects.get_or_create(
                    book=book,
                    copy_number=copy_number,
                    defaults={
                        "status": "available",
                        "location": f"Shelf {random.randint(1, 10)}{chr(65 + random.randint(0, 5))}",
                        "acquisition_date": timezone.now().date(),
                    },
                )

        self.stdout.write(
            self.style.SUCCESS("Successfully populated catalog with sample data!")
        )
        self.stdout.write(
            f"Created {len(genres)} genres, {len(authors)} authors, {len(publishers)} publishers, {len(books)} books"
        )
        total_copies = BookCopy.objects.count()
        self.stdout.write(f"Created {total_copies} book copies")
