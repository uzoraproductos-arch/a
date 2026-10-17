# -*- coding: utf-8 -*-
"""¿Con qué presupuesto se mide cada megaobra? (decisión del autor, 17-10-2026)

El sobrecosto principal se mide contra el presupuesto de la ficha. Para
algunas obras hay otro monto oficial anterior, el primero que se documentó
(simulador_megaobras.cuenta, renglón presupuesto_original_mdp). El autor
pidió no cambiar la cifra principal sino explicarlo en una nota
desplegable: cuál es el primer monto, de dónde sale y cuánto daría el
sobrecosto medido contra él. Lo usan mo_pulso.py (la cuenta de cada obra)
y mo_sector.py (la ficha de cada obra).
"""
import html

from presupuesto_modulos import chip


def esc(t):
    return html.escape(str(t), quote=True)


def _mdp(v):
    return '$' + format(v, ',.1f') + ' mdp'


def _fuentes(f):
    return ' · '.join('<a href="%s" target="_blank" rel="noopener">%s%s ↗</a>'
                      % (esc(x['url']), esc(x['doc'] if len(x['doc']) < 110 else x['doc'][:108] + '…'),
                         (', p. ' + esc(x['pag'])) if x.get('pag') else '') for x in f.get('f') or [])


def nota_base(o, filas, clase):
    """<details> con la explicacion, o '' si la obra no tiene el renglon."""
    f = next((x for x in filas or [] if x['c'] == 'presupuesto_original_mdp'), None)
    if not f:
        return ''
    principal = o['inversion_presupuestada_mdp']
    real = o['inversion_real_mdp']
    if f['e'] == 'no_aplica':
        cuerpo = ('<p>No aplica: es un rescate financiero, no una obra. Su cifra de partida es lo que se presentó en su '
                  'momento (%s), y por eso lo que creció después no se compara con el sobrecosto de una obra.</p>'
                  % _mdp(principal))
    elif f['e'] == 'pendiente':
        cuerpo = ('<p>El sobrecosto se mide contra %s. El primer monto documentado de la obra sigue sin publicarse %s: %s</p>'
                  % (_mdp(principal), chip('pendiente', 'cuenta-' + o['id']), esc(f.get('resp') or '')))
    elif abs(f['v'] - principal) <= max(0.05, principal * 0.005):
        cuerpo = ('<p>El presupuesto con que se mide (%s) es también el primer monto documentado (%s) %s: %s No hay otra '
                  'base oficial que cambie el sobrecosto.</p><p>Fuente: %s</p>'
                  % (_mdp(principal), f.get('anio') or '', chip(f['e']), esc(f.get('op') or ''), _fuentes(f)))
    else:
        alt = (real / f['v'] - 1) * 100
        cuerpo = ('<p>El sobrecosto de arriba se mide contra %s. Pero el <b>primer monto documentado</b> fue %s (%s) %s: %s</p>'
                  '<p>Medido contra ese primer monto, el sobrecosto sería <b>%s%s %%</b>: (%s ÷ %s − 1) × 100 %s.</p>'
                  '<p>Las dos bases son oficiales y responden preguntas distintas: contra el primer monto ves cuánto creció '
                  'la obra desde que se registró por primera vez; contra el de arriba, cuánto se pasó del monto que explica '
                  'la definición del presupuesto.</p><p>Fuente: %s</p>'
                  % (_mdp(principal), _mdp(f['v']), f.get('anio') or '', chip(f['e']), esc(f.get('op') or ''),
                     '+' if alt > 0 else '', format(alt, '.1f'), format(real, ',.1f'), format(f['v'], ',.1f'),
                     chip('derivado'), _fuentes(f)))
    return ('<details class="%s"><summary><span aria-hidden="true">📏</span> ¿Con qué presupuesto se mide?</summary>%s</details>'
            % (clase, cuerpo))
