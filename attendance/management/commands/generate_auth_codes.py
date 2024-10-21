from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import AuthCode
import random


class Command(BaseCommand):
    help = 'Generate authentication codes for employees'

    def handle(self, *args, **kwargs):
        users = User.objects.all()  # Get all users

        for user in users:
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Generate a 6-digit random code

            # Check if the user already has an AuthCode entry
            auth_code, created = AuthCode.objects.get_or_create(user=user)

            # Update the code if it already exists or set a new one
            auth_code.code = code
            auth_code.save()

            # Print success message for each user
            self.stdout.write(self.style.SUCCESS(f'Generated code for {user.username}: {code}'))

        self.stdout.write(self.style.SUCCESS('Authentication codes generated/updated for all employees.'))
