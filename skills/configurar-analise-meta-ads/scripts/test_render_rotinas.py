"""Testes sintéticos de renderização/contrato, sem rede ou conta real. Não testam o conector HYPD nem idempotência real do agendador."""
import copy
import json
import unittest
from decimal import Decimal
from render_rotinas import ROOT, render, validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((ROOT / 'references/perfil-template.json').read_text())
        self.p.update(account_id='SYNTHETIC', account_name='Conta de teste', currency='BRL', account_timezone='America/Sao_Paulo', schedule_timezone='America/Sao_Paulo', schedule_timezone_confirmed=True, connection_verified_at='2026-10-14T12:00:00Z', profile_confirmed=True, max_new_customer_cost=50, max_contact_cost=10, contact_type='lead cadastrado', contact_event='synthetic_lead', attribution='7 dias clique, 1 dia visualização; base impressão')

    def test_two_slots_self_contained(self):
        for slot, hour in [('manha', 9), ('tarde', 17)]:
            out = render(self.p, slot)
            self.assertEqual(out['schedule']['hour'], hour)
            self.assertIn('Não altere campanhas, anúncios ou orçamento', out['instructions'])
            self.assertIn('Zero confirmado', out['instructions'])
            self.assertIn('D−14', out['instructions'])
            self.assertNotIn('[conversa iniciada ou lead cadastrado]', out['instructions'])
            self.assertIn('unknown', out['instructions'])
        self.assertEqual(render(self.p, 'manha'), render(self.p, 'manha'))

    def test_weighted_cost_example_preserved(self):
        text = render(self.p, 'manha')['instructions']
        total_cost = (Decimal(90) + Decimal(10)) / (Decimal(9) + Decimal(2))
        self.assertEqual(total_cost.quantize(Decimal('0.01')), Decimal('9.09'))
        self.assertIn('100/11', text)
        self.assertIn('7,50 está errada', text)

    def test_distinct_schedule_timezone_only_changes_schedule(self):
        self.p['schedule_timezone'] = 'Europe/London'
        out = render(self.p, 'tarde')
        self.assertEqual(out['schedule']['timezone'], 'Europe/London')
        self.assertIn('As janelas de dados usam exclusivamente America/Sao_Paulo', out['instructions'])
        self.assertIn('muda SOMENTE os horários da agenda', out['instructions'])

    def test_blank_template_rejected(self):
        with self.assertRaises(ValueError):
            validate(json.loads((ROOT / 'references/perfil-template.json').read_text()))

    def test_ambiguous_contact_rejected(self):
        self.p['contact_type'] = 'ambos'
        with self.assertRaises(ValueError):
            validate(self.p)

    def test_zero_or_nonfinite_targets_rejected(self):
        for value in [0, -1, float('nan'), float('inf'), True]:
            p = copy.deepcopy(self.p)
            p['max_contact_cost'] = value
            with self.assertRaises(ValueError):
                validate(p)

    def test_secrets_or_extra_fields_rejected(self):
        self.p['access_token'] = 'synthetic-not-a-token'
        with self.assertRaises(ValueError):
            validate(self.p)

    def test_unconfirmed_profile_rejected(self):
        self.p['profile_confirmed'] = False
        with self.assertRaises(ValueError):
            validate(self.p)

    def test_unconfirmed_timezone_rejected(self):
        self.p['schedule_timezone_confirmed'] = False
        with self.assertRaises(ValueError):
            validate(self.p)

    def test_placeholders_and_unverified_currency_rejected(self):
        for field, value in [('account_id', '<account_id>'), ('attribution', 'TBD'), ('contact_event', ' unknown '), ('currency', 'ZZZ'), ('account_name', ' Pendente '), ('language', 'TODO')]:
            p = copy.deepcopy(self.p)
            p[field] = value
            with self.assertRaises(ValueError, msg=f'{field}={value}'):
                validate(p)

    def test_currency_personalization(self):
        self.p.update(currency='USD', max_contact_cost=4, max_new_customer_cost=25)
        out = render(self.p, 'tarde')['instructions']
        self.assertIn('USD 25', out)
        self.assertNotIn('R$ 50', out)


if __name__ == '__main__':
    unittest.main()
