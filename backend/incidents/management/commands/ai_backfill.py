from django.core.management.base import BaseCommand

from incidents.ai_service import predict
from incidents.models import CATEGORY_TO_DEPARTMENT, Incident


class Command(BaseCommand):
    help = 'Run the AI over open incidents that have no AI explanation yet.'

    def handle(self, *args, **options):
        count = 0
        for inc in Incident.objects.filter(ai_reason='').exclude(status='resolved'):
            result = predict(inc.title, inc.description)
            inc.ai_reason = result['reason']
            inc.needs_review = result['needs_review']
            if inc.category == 'other' and not inc.department and not inc.assigned_to_id:
                inc.category = result['category']
                inc.department = CATEGORY_TO_DEPARTMENT.get(result['category'], '')
            inc.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'AI reviewed {count} incident(s).'))