from django.core.management.base import BaseCommand
from blog.models import Category, Post, Comment


class Command(BaseCommand):
    help = "Populate sample blog data for the library application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating sample blog data...")

        # Sample categories
        categories_data = [
            {
                "name": "Library News",
                "slug": "library-news",
                "description": "Latest news and announcements from the library",
            },
            {
                "name": "Research",
                "slug": "research",
                "description": "Research highlights and academic achievements",
            },
            {
                "name": "Events",
                "slug": "events",
                "description": "Upcoming events and library activities",
            },
            {
                "name": "Technology",
                "slug": "technology",
                "description": "Digital library updates and tech news",
            },
        ]

        # Create categories
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data["slug"], defaults=cat_data
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Sample posts
        posts_data = [
            {
                "title": "New Digital Library Resources Now Available",
                "slug": "new-digital-library-resources",
                "excerpt": "We're excited to announce the addition of hundreds of new digital resources to our online collection.",
                "content": """
                <p>The University of Maiduguri Library is pleased to announce the addition of hundreds of new digital resources to our online collection. These resources include:</p>

                <ul>
                    <li>Access to over 50,000 e-books across various disciplines</li>
                    <li>Expanded journal collections with full-text articles</li>
                    <li>New multimedia resources including videos and podcasts</li>
                    <li>Enhanced research databases for academic research</li>
                </ul>

                <p>Students and faculty can now access these resources 24/7 from anywhere with an internet connection. This expansion significantly enhances our commitment to providing comprehensive information resources to support teaching, learning, and research activities.</p>

                <p>To access these resources, visit our digital library portal and log in with your university credentials.</p>
                """,
                "category_slug": "technology",
                "author": "Dr. Aisha Umar",
                "is_featured": True,
            },
            {
                "title": "Library Extended Hours During Exam Period",
                "slug": "library-extended-hours-exam-period",
                "excerpt": "The library will remain open extended hours to support students during the upcoming examination period.",
                "content": """
                <p>In response to student needs during the examination period, the University of Maiduguri Library will operate extended hours starting next week.</p>

                <h3>Extended Hours Schedule:</h3>
                <ul>
                    <li>Monday - Friday: 7:00 AM - 10:00 PM</li>
                    <li>Saturday: 8:00 AM - 8:00 PM</li>
                    <li>Sunday: 10:00 AM - 6:00 PM</li>
                </ul>

                <p>During this period, we will also increase the number of study spaces available and provide additional research assistance. Our reference librarians will be available to help students with research questions and provide guidance on academic resources.</p>

                <p>We encourage all students to take advantage of these extended hours to maximize their study time and academic success.</p>
                """,
                "category_slug": "library-news",
                "author": "Library Administration",
                "is_featured": False,
            },
            {
                "title": "Annual Research Excellence Awards Ceremony",
                "slug": "annual-research-excellence-awards",
                "excerpt": "Celebrating outstanding research achievements by our faculty and students at the annual awards ceremony.",
                "content": """
                <p>The University of Maiduguri Library hosted the Annual Research Excellence Awards Ceremony, recognizing outstanding research achievements by faculty and students.</p>

                <p>This year's ceremony celebrated:</p>
                <ul>
                    <li>Best Research Paper Awards in various disciplines</li>
                    <li>Outstanding Librarian Service Awards</li>
                    <li>Student Research Achievement Awards</li>
                    <li>Innovation in Research Methodology Awards</li>
                </ul>

                <p>The event highlighted the significant contributions of our academic community to knowledge advancement and societal development. The library played a crucial role in supporting these research endeavors by providing access to comprehensive information resources and research assistance.</p>

                <p>Congratulations to all the award recipients for their dedication to academic excellence!</p>
                """,
                "category_slug": "research",
                "author": "Dr. Ibrahim Saleh",
                "is_featured": True,
            },
            {
                "title": "Upcoming Workshop: Effective Research Strategies",
                "slug": "workshop-effective-research-strategies",
                "excerpt": "Join us for a comprehensive workshop on developing effective research strategies and utilizing library resources.",
                "content": """
                <p>The University of Maiduguri Library is organizing a comprehensive workshop on "Effective Research Strategies" designed to equip students and researchers with essential skills for academic success.</p>

                <h3>Workshop Details:</h3>
                <ul>
                    <li><strong>Date:</strong> December 15, 2025</li>
                    <li><strong>Time:</strong> 10:00 AM - 4:00 PM</li>
                    <li><strong>Venue:</strong> Library Auditorium</li>
                    <li><strong>Target Audience:</strong> Undergraduate and postgraduate students, faculty members</li>
                </ul>

                <h3>Topics Covered:</h3>
                <ul>
                    <li>Developing research questions and hypotheses</li>
                    <li>Effective literature search techniques</li>
                    <li>Evaluating information sources</li>
                    <li>Citation and reference management</li>
                    <li>Using library databases and online resources</li>
                    <li>Research ethics and academic integrity</li>
                </ul>

                <p>Registration is free and can be done at the library reception or online through our website. Limited seats available - early registration recommended!</p>
                """,
                "category_slug": "events",
                "author": "Mrs. Fatima Bello",
                "is_featured": False,
            },
        ]

        # Get categories for posts
        categories = {cat.slug: cat for cat in Category.objects.all()}

        # Create posts
        for post_data in posts_data:
            category = categories.get(post_data.pop("category_slug"))
            if category:
                post, created = Post.objects.get_or_create(
                    slug=post_data["slug"], defaults={**post_data, "category": category}
                )
                if created:
                    self.stdout.write(f"Created post: {post.title}")

        # Sample comments
        comments_data = [
            {
                "post_slug": "new-digital-library-resources",
                "author_name": "Ahmed Musa",
                "author_email": "ahmed.musa@unimaid.edu.ng",
                "content": "This is fantastic news! The expanded digital collection will greatly benefit our research work.",
            },
            {
                "post_slug": "library-extended-hours-exam-period",
                "author_name": "Zainab Ibrahim",
                "author_email": "zainab.ibrahim@unimaid.edu.ng",
                "content": "Thank you for considering students' needs. The extended hours will be very helpful during exam preparation.",
            },
            {
                "post_slug": "annual-research-excellence-awards",
                "author_name": "Prof. Musa Ahmed",
                "author_email": "musa.ahmed@unimaid.edu.ng",
                "content": "Congratulations to all the award winners! This ceremony showcases the excellent research being conducted at our university.",
            },
        ]

        # Create comments
        for comment_data in comment_data:
            post_slug = comment_data.pop("post_slug")
            try:
                post = Post.objects.get(slug=post_slug)
                comment, created = Comment.objects.get_or_create(
                    post=post,
                    author_name=comment_data["author_name"],
                    author_email=comment_data["author_email"],
                    defaults=comment_data,
                )
                if created:
                    self.stdout.write(f"Created comment by {comment.author_name}")
            except Post.DoesNotExist:
                self.stdout.write(
                    f"Warning: Post with slug '{post_slug}' not found for comment"
                )

        self.stdout.write(self.style.SUCCESS("Blog sample data population completed!"))
