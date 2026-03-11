from django.core.management.base import BaseCommand
from apps.recommend.algorithms.user_cf import UserBasedCF
from apps.recommend.algorithms.item_cf import ItemBasedCF


class Command(BaseCommand):
    help = 'Recalculate user and item similarity matrices for Collaborative Filtering'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['user', 'item', 'all'],
            default='all',
            help='Type of similarity to recalculate: user (UserCF), item (ItemCF), or all (both)'
        )

    def handle(self, *args, **options):
        calc_type = options['type']

        if calc_type in ['user', 'all']:
            self.stdout.write(self.style.WARNING('Starting User Similarity calculation...'))
            try:
                count = UserBasedCF.compute_and_save_all()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} user similarity pairs.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to update user similarity: {str(e)}'))
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        if calc_type in ['item', 'all']:
            self.stdout.write(self.style.WARNING('Starting Item Similarity calculation...'))
            try:
                count = ItemBasedCF.compute_and_save_all()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} item similarity pairs.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to update item similarity: {str(e)}'))
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
