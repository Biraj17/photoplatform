import random
import urllib.error
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import Photographer, PhotographerProject, PortfolioImage

PORTFOLIO_IMAGES_PER_PHOTOGRAPHER = 3

PROJECT_IDEAS = {
    "Wedding": [
        ("Kathmandu Valley Wedding", "A full-day wedding shoot covering the ceremony, reception, and candid family moments."),
        ("Pokhara Lakeside Wedding", "Sunrise couple portraits by Phewa Lake followed by the reception coverage."),
    ],
    "Portrait": [
        ("Studio Portrait Session", "A series of natural-light studio portraits for a personal branding project."),
        ("Golden Hour Portraits", "Outdoor portrait session timed around golden hour for warm, soft lighting."),
    ],
    "Family": [
        ("Family Weekend Shoot", "A relaxed outdoor session with a family of four, focused on candid interaction."),
        ("Three Generations", "A portrait session bringing grandparents, parents, and kids together in one shoot."),
    ],
    "Fashion": [
        ("Streetwear Lookbook", "A lookbook shoot for a local streetwear label across three city locations."),
        ("Editorial Fashion Story", "A concept-driven editorial series exploring light and texture."),
    ],
    "Travel": [
        ("Annapurna Trail Diaries", "A week-long documentary shoot following trekkers along the Annapurna circuit."),
        ("Everest Region Landscapes", "Landscape and culture photography across villages in the Khumbu region."),
    ],
}


class Command(BaseCommand):
    help = "Populate existing photographer profiles with placeholder photos and a sample project (demo data only)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout", type=int, default=15,
            help="Per-image download timeout in seconds (default: 15)",
        )

    def handle(self, *args, **options):
        self.timeout = options["timeout"]
        photographers = Photographer.objects.all()
        if not photographers.exists():
            self.stdout.write("No photographers found — nothing to seed.")
            return

        for photographer in photographers:
            self.stdout.write(f"Seeding media for {photographer.full_name} ({photographer.specialty})...")

            if not photographer.profile_image:
                filename = f"profile-{photographer.pk}.jpg"
                content = self._download(f"photoplat-profile-{photographer.pk}", 600, 600, filename)
                if content:
                    photographer.profile_image.save(filename, content, save=True)

            existing_portfolio = photographer.portfolio_images.count()
            for i in range(existing_portfolio, PORTFOLIO_IMAGES_PER_PHOTOGRAPHER):
                filename = f"portfolio-{photographer.pk}-{i}.jpg"
                content = self._download(f"photoplat-portfolio-{photographer.pk}-{i}", 900, 700, filename)
                if content:
                    portfolio_image = PortfolioImage(photographer=photographer)
                    portfolio_image.image.save(filename, content, save=True)

            if photographer.projects.count() == 0:
                title, description = random.choice(
                    PROJECT_IDEAS.get(photographer.specialty, PROJECT_IDEAS["Portrait"])
                )
                filename = f"project-{photographer.pk}.jpg"
                content = self._download(f"photoplat-project-{photographer.pk}", 900, 600, filename)
                project = PhotographerProject(
                    photographer=photographer,
                    title=title,
                    location=photographer.city or "Kathmandu, Nepal",
                    description=description,
                )
                if content:
                    project.cover_image.save(filename, content, save=False)
                project.save()

        self.stdout.write(self.style.SUCCESS("Done seeding demo media."))

    def _download(self, seed, width, height, filename):
        url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                data = response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            self.stderr.write(self.style.WARNING(f"  Could not download image ({seed}): {exc}"))
            return None
        content = ContentFile(data)
        content.name = filename
        return content
