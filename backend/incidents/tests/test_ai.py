from django.test import SimpleTestCase

from incidents.ai_service import predict

# title, description, expected urgency, expected category, expected needs_review
CASES = [
    ('Building fire', 'Fire on second floor, people trapped', 'critical', 'fire', False),
    ('Medical emergency', 'Elderly man collapsed in the market, not responding', 'critical', 'medical', False),
    ('Road accident', 'Two bikes collided, one injured', 'high', 'accident', False),
    ('Gas leak', 'Strong gas smell in the apartment building lobby', 'high', 'fire', False),
    ('Water logging', 'Street flooded after rain', 'high', 'flood', False),
    ('Chest pain', 'Man has severe chest pain at the bus stop', 'high', 'medical', False),
    ('Highway crash', 'Two cars crashed, many people injured', 'critical', 'accident', False),
    ('Drowning', 'Boy drowning in the river near the bridge', 'critical', 'flood', False),
    ('Seizure', 'Woman had a seizure at the bus stand', 'high', 'medical', False),
    ('Fever', 'Mild fever and cough since morning', 'medium', 'medical', False),
    ('Smoke', 'Smoke coming from a shop, no one is trapped', 'high', 'fire', False),
    ('Possible smoke', 'Not sure, but I think there is smoke near the school', 'high', 'fire', False),
    ('Child stuck in lift', 'A small child is stuck in the lift at the mall', 'high', 'other', True),
    ('False alarm', 'No fire, just burnt toast in the kitchen', 'low', 'other', True),
    ('Pothole', 'There is a big pothole on the main road', 'low', 'other', True),
    ('आग', 'इमारतीला आग लागली', 'low', 'other', True),     # not English: a human must triage it
]


class PredictTests(SimpleTestCase):
    def test_examples(self):
        for title, description, urgency, category, needs_review in CASES:
            with self.subTest(title=title):
                result = predict(title, description)
                self.assertEqual(result['urgency'], urgency)
                self.assertEqual(result['category'], category)
                self.assertEqual(result['needs_review'], needs_review)

    def test_reason_is_never_empty(self):
        self.assertTrue(predict('Help', 'Please help me')['reason'])