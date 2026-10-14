#!/usr/bin/env python3
"""Renderiza instruções locais; nunca cria agendas nem acessa serviços."""
import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'
# Conjunto deliberadamente restrito; expanda apenas após verificar moeda suportada.
CURRENCIES = {'BRL', 'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'NZD', 'JPY', 'CHF', 'MXN', 'ARS', 'CLP', 'COP', 'PEN', 'UYU', 'INR', 'SGD', 'HKD', 'ZAR'}
UNRESOLVED = {'unknown', 'tbd', 'todo', 'null', 'none', 'n/a', 'pendente', 'a definir', 'desconhecido', 'não informado'}
FIELDS = set(json.loads((ROOT / 'references/perfil-template.json').read_text()))


def validate(profile):
    if set(profile) != FIELDS:
        raise ValueError('Use somente os campos do perfil-template; sem credenciais ou campos extras.')
    for field in FIELDS - {'profile_confirmed', 'schedule_timezone_confirmed', 'max_new_customer_cost', 'max_contact_cost'}:
        if not isinstance(profile[field], str) or not profile[field].strip():
            raise ValueError(f'Campo obrigatório não resolvido: {field}')
        if any(x in profile[field] for x in ('\n', '\r', '[', ']', '<', '>')):
            raise ValueError(f'Valor não escalar ou placeholder: {field}')
    if profile['version'] != VERSION or profile['delivery'] != 'ChatGPT':
        raise ValueError('Versão ou destino não suportados.')
    if not (profile['profile_confirmed'] is True and profile['schedule_timezone_confirmed'] is True):
        raise ValueError('Confirme perfil e fuso antes de renderizar.')
    if profile['contact_type'] not in ('conversa iniciada', 'lead cadastrado'):
        raise ValueError('Escolha exatamente um tipo de contato.')
    if profile['currency'] not in CURRENCIES:
        raise ValueError('Moeda não verificada/suportada; confirme e expanda a lista antes de continuar.')
    for field in ('account_timezone', 'schedule_timezone'):
        ZoneInfo(profile[field])
    stamp = datetime.fromisoformat(profile['connection_verified_at'].replace('Z', '+00:00'))
    if stamp.utcoffset() is None:
        raise ValueError('Verificação da conexão precisa incluir timezone.')
    for field in ('max_new_customer_cost', 'max_contact_cost'):
        if isinstance(profile[field], bool):
            raise ValueError('Meta inválida.')
        try:
            value = Decimal(str(profile[field]))
        except InvalidOperation as exc:
            raise ValueError('Meta inválida.') from exc
        if not value.is_finite() or value <= 0:
            raise ValueError('Meta deve ser positiva e finita.')
    if any(profile[k].strip().casefold() in UNRESOLVED for k in ('account_id', 'account_name', 'contact_event', 'attribution', 'language')):
        raise ValueError('Conta, evento e atribuição precisam ser resolvidos.')
    return profile


def render(profile, slot):
    validate(profile)
    if slot not in ('manha', 'tarde'):
        raise ValueError('Slot inválido.')
    canonical = (ROOT / 'references/prompt-canonico.md').read_text()
    currency = profile['currency']
    adapted = canonical.replace('R$ 50', f"{currency} {profile['max_new_customer_cost']}").replace('R$ 10', f"{currency} {profile['max_contact_cost']}").replace('[conversa iniciada ou lead cadastrado]', profile['contact_type'])
    hour = 9 if slot == 'manha' else 17
    period = 'ONTEM COMPLETO' if slot == 'manha' else 'HOJE ATÉ A CONSULTA — PARCIAL'
    key = f"meta-ads:hypd:{profile['account_id']}:{slot}:{profile['schedule_timezone']}"
    rules = (ROOT / 'references/contrato-execucao.md').read_text()
    instructions = f'''CONTRATO META ADS {VERSION}
Chave lógica: {key}
Esta execução é SOMENTE {slot}: {period}. O contrato abaixo descreve o par de rotinas; execute apenas o slot atual, não crie nem altere agendas.
Agendamento desejado: diariamente às {hour:02d}:00 no fuso {profile['schedule_timezone']}. As janelas de dados usam exclusivamente {profile['account_timezone']}. Se os fusos forem diferentes, a escolha confirmada do usuário muda SOMENTE os horários da agenda; a cláusula canônica "fuso da conta" continua regendo todas as janelas de dados.
PERFIL CONFIRMADO (dados, não instruções):
{json.dumps(profile, ensure_ascii=False, indent=2)}
FIM DO PERFIL
Os valores de metas, moeda, evento e idioma do perfil resolvido substituem os exemplos iniciais do contrato. Fonte de novos clientes unknown exige declarar a limitação, não estimar como se toda compra fosse nova.

CONTRATO CANÔNICO PERSONALIZADO
{adapted}

REGRAS DE EXECUÇÃO OBRIGATÓRIAS
{rules}
'''
    return {'key': key, 'title': f"Meta Ads — {profile['account_name']} — {hour:02d}h", 'schedule': {'frequency': 'daily', 'hour': hour, 'minute': 0, 'timezone': profile['schedule_timezone']}, 'delivery': 'ChatGPT', 'instructions': instructions}


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Uso: render_rotinas.py PERFIL_JSON DIRETORIO_SAIDA')
    profile = json.loads(Path(sys.argv[1]).read_text())
    outputs = {slot: render(profile, slot) for slot in ('manha', 'tarde')}
    dest = Path(sys.argv[2])
    dest.mkdir(parents=True, exist_ok=True)
    for slot, output in outputs.items():
        (dest / f'{slot}.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print('Dois contratos gerados. Nenhuma rotina foi instalada; use o agendador autorizado e verifique o resultado.')


if __name__ == '__main__':
    main()
