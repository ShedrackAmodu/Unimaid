from django.core.management.base import BaseCommand
from core.models import LibraryDivision


class Command(BaseCommand):
    help = "Populate sample data for the library application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating sample library divisions...")

        # Sample library divisions data
        divisions_data = [
            {
                "name": "Collection Development Division",
                "description": "Responsible for selecting, acquiring, organizing, and maintaining the library's resources, such as books, journals, and digital materials, to meet the needs of its users.",
                "category": "division",
                "order": 1,
            },
            {
                "name": "Cataloguing Division",
                "description": "Organizes and classifies all library materials, creating records and entries so that users can easily find and access resources.",
                "category": "division",
                "order": 2,
            },
            {
                "name": "Readers Services Division",
                "description": "Assists users in accessing and using library resources, including lending books, providing reference help, and guiding users in research and information retrieval.",
                "category": "division",
                "order": 3,
            },
            {
                "name": "E-Library Division",
                "description": "Provides access to electronic resources—such as e-books, journals, databases, and multimedia allowing users to read, search, and download materials online.",
                "category": "division",
                "order": 4,
            },
            {
                "name": "Research and Bibliographic Services Division",
                "description": "Support to users in conducting research, offering guidance on finding, evaluating, and using information, as well as creating bibliographies and citations.",
                "category": "division",
                "order": 5,
            },
            {
                "name": "American Space",
                "description": "A dedicated space providing access to American literature, research materials, and cultural resources.",
                "category": "center",
                "order": 1,
            },
            {
                "name": "International Institute of Islamic Thought",
                "description": "Specialized center for Islamic studies, research, and scholarly resources.",
                "category": "center",
                "order": 2,
            },
            {
                "name": "Digital Library Center",
                "description": "Modern facility providing access to digital collections, online databases, and electronic resources.",
                "category": "center",
                "order": 3,
            },
        ]

        # Create divisions
        for division_data in divisions_data:
            division, created = LibraryDivision.objects.get_or_create(
                name=division_data["name"], defaults=division_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created division: {division.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Division already exists: {division.name}")
                )

        self.stdout.write(self.style.SUCCESS("Sample data population completed!"))
