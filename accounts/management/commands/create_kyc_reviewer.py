from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from accounts.admin import KYC_REVIEWER_GROUP
from accounts.models import Photographer


class Command(BaseCommand):
    help = (
        "Create (or update) a staff user who can only review and update photographer KYC status "
        "from the Django admin. Creates the 'KYC Reviewers' group on first run."
    )

    def add_arguments(self, parser):
        parser.add_argument("email", help="Login email/username for the reviewer")
        parser.add_argument("password", help="Password for the reviewer")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]

        content_type = ContentType.objects.get_for_model(Photographer)
        view_perm = Permission.objects.get(content_type=content_type, codename="view_photographer")
        change_perm = Permission.objects.get(content_type=content_type, codename="change_photographer")

        group, _ = Group.objects.get_or_create(name=KYC_REVIEWER_GROUP)
        group.permissions.set([view_perm, change_perm])

        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "is_staff": True},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = False
        user.set_password(password)
        user.save()
        user.groups.add(group)

        if Photographer.objects.filter(user=user).exists():
            raise CommandError(
                f"{email} already has a photographer profile — use a separate account for KYC review."
            )

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} KYC reviewer '{email}'. They can log in at /admin/ and review Photographer KYC only."
        ))
