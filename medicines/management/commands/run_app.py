import threading
import os
import time
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Start the complete MediMimes application (server + medication monitoring)'

    def handle(self, *args, **options):
        def run_server():
            """Run Django development server"""
            os.system('python manage.py runserver 127.0.0.1:8000')
        
        def run_medication_check():
            """Run medication check in a loop"""
            while True:
                call_command('run_medication_check')
                time.sleep(60)  # Check every minute
        
        # Start both threads
        server_thread = threading.Thread(target=run_server, daemon=True)
        check_thread = threading.Thread(target=run_medication_check, daemon=True)
        
        server_thread.start()
        check_thread.start()
        
        self.stdout.write(
            self.style.SUCCESS(' MediMimes application started successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS(' Server running on: http://127.0.0.1:8000/')
        )
        self.stdout.write(
            self.style.SUCCESS(' Medication monitoring: ACTIVE')
        )
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING(' Shutting down MediMimes...'))