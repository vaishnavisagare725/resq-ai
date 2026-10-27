from io import StringIO

from django.core.management import call_command

from .base import ApiTestCase


class BackfillTests(ApiTestCase):
    def run_command(self):
        out = StringIO()
        call_command('ai_backfill', stdout=out)
        return out.getvalue()

    def test_it_explains_and_routes_an_old_incident(self):
        old = self.make(title='Building fire', description='Fire on second floor, people trapped')
        message = self.run_command()
        old.refresh_from_db()
        self.assertIn('AI reviewed 1 incident(s)', message)
        self.assertEqual((old.category, old.department), ('fire', 'fire'))
        self.assertNotEqual(old.ai_reason, '')
        self.assertFalse(old.needs_review)

    def test_running_it_twice_is_safe(self):
        self.make(title='Building fire', description='Fire on second floor, people trapped')
        self.run_command()
        self.assertIn('AI reviewed 0 incident(s)', self.run_command())

    def test_it_never_overrides_a_choice_a_human_made(self):
        human = self.make(
            title='Fire in a shop', description='Fire in the building',
            category='medical', department='medical',
        )
        self.run_command()
        human.refresh_from_db()
        self.assertEqual(human.category, 'medical')   # the AI would say "fire", but a human chose
        self.assertNotEqual(human.ai_reason, '')       # it still got an explanation

    def test_it_leaves_taken_and_resolved_incidents_alone(self):
        taken = self.make(title='Fire', description='Fire in the building')
        taken.assign_responder(self.med_boss, self.med_boss)
        done = self.make(title='Fire', description='Fire in the building', department='fire')
        done.assign_responder(self.fire_boss, self.fire_boss)
        done.change_status('resolved', self.fire_boss)

        self.run_command()
        taken.refresh_from_db()
        done.refresh_from_db()
        self.assertEqual(taken.category, 'other')      # already in a team's hands
        self.assertEqual(done.ai_reason, '')           # resolved: not touched at all