from django.core.management.base import BaseCommand
from django.db.models import Q
from reservations.models import Reservation
from restaurants.models import Table, Floorplan


class Command(BaseCommand):
    help = 'Assign tables to reservations that do not have tables assigned'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating the database',
        )
        parser.add_argument(
            '--restaurant-id',
            type=int,
            help='Only process reservations for a specific restaurant ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        restaurant_id = options.get('restaurant_id')

        # Find reservations without table assignments
        # For PostgreSQL ArrayField, check for None or empty arrays
        base_query = Q()
        if restaurant_id:
            base_query &= Q(restaurant_id=restaurant_id)
        
        # Get all reservations (we'll filter for empty table_numbers in Python)
        all_reservations = Reservation.objects.filter(base_query).select_related('restaurant', 'restaurant__floorplan')
        
        # Filter for reservations with no table assignments
        reservations = [
            r for r in all_reservations 
            if not r.table_numbers or len(r.table_numbers) == 0
        ]
        
        if not reservations:
            self.stdout.write(
                self.style.SUCCESS('No reservations found without table assignments.')
            )
            return

        self.stdout.write(f'Found {len(reservations)} reservation(s) without table assignments.')

        updated_count = 0
        skipped_count = 0

        for reservation in reservations:
            if not reservation.restaurant:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping reservation {reservation.id} - No restaurant assigned'
                    )
                )
                skipped_count += 1
                continue

            # Get the restaurant's floorplan
            # Since floorplan is a OneToOneField with null=True, it can be None
            floorplan = getattr(reservation.restaurant, 'floorplan', None)
            
            if not floorplan:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping reservation {reservation.id} - Restaurant "{reservation.restaurant.name}" has no floorplan'
                    )
                )
                skipped_count += 1
                continue

            # Get available tables for this floorplan
            tables = Table.objects.filter(floorplan=floorplan).order_by('number')
            
            if not tables.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping reservation {reservation.id} - No tables found for restaurant "{reservation.restaurant.name}"'
                    )
                )
                skipped_count += 1
                continue

            # Find tables that can accommodate the guest count
            assigned_tables = self.find_tables_for_guests(tables, reservation.guest_count)
            
            if not assigned_tables:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping reservation {reservation.id} - No suitable tables found for {reservation.guest_count} guests'
                    )
                )
                skipped_count += 1
                continue

            # Convert table numbers to strings (as required by ArrayField)
            table_numbers = [str(table.number) for table in assigned_tables]
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[DRY RUN] Would assign tables {", ".join(table_numbers)} to reservation {reservation.id} '
                        f'({reservation.name}, {reservation.guest_count} guests at {reservation.restaurant.name})'
                    )
                )
            else:
                reservation.table_numbers = table_numbers
                reservation.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned tables {", ".join(table_numbers)} to reservation {reservation.id} '
                        f'({reservation.name}, {reservation.guest_count} guests at {reservation.restaurant.name})'
                    )
                )
            
            updated_count += 1

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {updated_count} reservation(s) {"would be " if dry_run else ""}updated, '
                f'{skipped_count} skipped'
            )
        )

    def find_tables_for_guests(self, tables, guest_count):
        """
        Find the best combination of tables to accommodate the guest count.
        Tries to minimize the number of tables while meeting capacity requirements.
        """
        # Filter out reserved tables and sort by capacity (ascending)
        available_tables = [
            t for t in tables 
            if t.status == 'available'
        ]
        
        if not available_tables:
            return []

        # Sort by capacity (ascending) to prefer smaller tables first
        available_tables.sort(key=lambda t: t.capacity)

        # Try to find a single table that can accommodate all guests
        for table in available_tables:
            if table.capacity >= guest_count:
                return [table]

        # If no single table is large enough, find the minimum combination
        # Use a greedy approach: try to fill with the largest available tables first
        available_tables.sort(key=lambda t: t.capacity, reverse=True)
        
        selected_tables = []
        remaining_guests = guest_count
        
        for table in available_tables:
            if remaining_guests <= 0:
                break
            selected_tables.append(table)
            remaining_guests -= table.capacity

        # If we can accommodate all guests, return the selected tables
        if remaining_guests <= 0:
            return selected_tables

        # If we still can't accommodate, try a different approach:
        # Use smaller tables that together can accommodate
        available_tables.sort(key=lambda t: t.capacity)
        selected_tables = []
        remaining_guests = guest_count
        
        for table in available_tables:
            if remaining_guests <= 0:
                break
            selected_tables.append(table)
            remaining_guests -= table.capacity

        # Return tables if we can accommodate (or at least get close)
        # Allow some flexibility - if we're within 2 guests, it's acceptable
        if remaining_guests <= 2:
            return selected_tables

        return []

