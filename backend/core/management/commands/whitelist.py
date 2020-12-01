from django.core.management.base import BaseCommand, CommandError
from core.models import Customer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates Settlementor Whitelist'

    def add_arguments(self, parser):
        parser.add_argument('owner_id', type=str)
        parser.add_argument(
            '--approved',
            action='store_true',
            help='Update the whitelist as approved for the pending command',
        )
        parser.add_argument(
            '--rejected',
            action='store_true',
            help='Update the whitelist as rejected for the pending command',
        )

    def handle(self, *args, **options):
        if 'owner_id' in options:
            owner_id = options['owner_id']
            try:
                cust = Customer.objects.get(owner_id=owner_id)
            except Exception as ex:
                print(ex)
                logger.error(f'Can not find the customer with owner id: {owner_id}')
                raise CommandError(f'Can not find the customer with owner id: {owner_id}')

            if options['approved'] and options['rejected']:
                logger.error(f'It must be either approved or rejected not both!')
                raise CommandError(f'It must be either approved or rejected not both!')
            if not options['approved'] and not options['rejected']:
                logger.error(f'Whitelist command must provide owner_id and either --approved or --rejected')
                print(options)
                raise CommandError(f'Whitelist command must provide owner_id and either --approved or --rejected')

            if options['approved']:
                cust.request = 'Approved'
                if cust.command in ['ADD', 'UPDATE']:
                    new_status = 'Active'
                    if cust.command == 'UPDATE':
                        cust.account_number = cust.account_number_req
                        cust.bank_id = cust.bank_id_req
                        cust.account_number_req = None
                        cust.bank_id_req = None
                else:  # Remove
                    new_status = 'Removed'
                cust.status = new_status
                cust.save()
                logger.info(f'Successfully approved customer whitelist [{cust.command}] for customer: {owner_id}')
            else:  # Rejected
                cust.request = 'Rejected'
                cust.account_number_req = None
                cust.bank_id_req = None
                cust.save()
                logger.info(f'Successfully rejected customer whitelist [{cust.command}] for customer: {owner_id}')
            self.stdout.write(self.style.SUCCESS(f'Successfully updated customer whitelist {owner_id}'))
        else:
            logger.error(f'Whitelist command must provide owner_id and either --approved or --rejected')
            CommandError(f'Whitelist command must provide owner_id and either --approved or --rejected')
