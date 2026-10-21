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


# ---- Una sola medida de ganancia o perdida (pedido del autor, 21-10-2026) ----
# Habia tres: la «perdida anual» del pulso y de la mesa 2 (operacion_oficial:
# Tren Maya y AIFA en 2024, el AIFA en cero, y el FOBAPROA en 2024 antes del
# Ramo 34: 87,461.9), el «resultado del año» de la cuenta de cada obra
# (-25,429.2) y el «costo vivo» de Sector (PEF 2026 mas intereses
# estimados). Ahora todas las paginas de Inversion y Megaobras usan esta:
# para cada obra, el renglon de la cuenta del año mas reciente publicado y,
# si ese año trae los dos, el resultado sin el apoyo del presupuesto
# (resultado_sin_transferencias_anual_mdp) antes que el del ejercicio. Las
# ganancias restan: un AIFA a favor ya no se cuenta como cero.
RES_CAMPOS = ('resultado_sin_transferencias_anual_mdp', 'resultado_anual_mdp')


def resultado(o, filas):
    """Ganancia (+) o perdida (-) del año de una obra, en mdp.

    tipo 'dato': v, anio, e, op, nota, f (fuentes), base ('sin_apoyo' si
    excluye el apoyo del presupuesto o la operacion lo hace por si misma;
    'ejercicio' si es el resultado publicado del ejercicio).
    tipo 'pendiente' o 'no_aplica': txt con el porque."""
    con = [f for f in filas or [] if f['c'] in RES_CAMPOS and 'v' in f]
    if con:
        anio = max(f.get('anio') or 0 for f in con)
        del_anio = [f for f in con if (f.get('anio') or 0) == anio]
        f = next((x for x in del_anio if x['c'] == RES_CAMPOS[0]), del_anio[0])
        sin_apoyo = f['c'] == RES_CAMPOS[0] or 'antes de transferencias' in (f.get('op') or '') or \
            'gastos totales' in (f.get('op') or '')
        return {'tipo': 'dato', 'v': f['v'], 'anio': f.get('anio'), 'e': f['e'], 'op': f.get('op') or '',
                'nota': f.get('nota') or '', 'f': f.get('f') or [], 'et': f['et'],
                'base': 'sin_apoyo' if sin_apoyo else 'ejercicio'}
    f = next((x for x in filas or [] if x['c'] == 'resultado_anual_mdp'), None)
    if f and f['e'] == 'no_aplica':
        return {'tipo': 'no_aplica', 'txt': f.get('op') or 'No aplica.'}
    if f and f['e'] == 'pendiente':
        return {'tipo': 'pendiente', 'txt': f.get('resp') or ''}
    # Sin renglon de resultado: lo que la cuenta si dice de su operacion (el
    # Bunker: la SSPC no publica el gasto del edificio por separado).
    g = next((x for x in filas or [] if x['c'] == 'costo_operativo_anual_mdp' and x['e'] == 'pendiente'), None)
    return {'tipo': 'pendiente', 'txt': (g.get('resp') if g else '') or 'Su cuenta no trae renglón de ganancia o pérdida.'}


def resultados(sm):
    """{id de obra: resultado()} para todas las obras."""
    cu = (sm.get('cuenta') or {}).get('obras') or {}
    return {o['id']: resultado(o, cu.get(o['id'])) for o in sm['obras']}


def balance(sm, ids=None):
    """Suma de la medida: neto (ganancias menos perdidas, con signo), lo
    que pierden, lo que ganan y cuantas obras hay de cada tipo."""
    res = resultados(sm)
    sel = [res[o['id']] for o in sm['obras'] if ids is None or o['id'] in ids]
    dat = [r for r in sel if r['tipo'] == 'dato']
    return {'neto': sum(r['v'] for r in dat), 'pierde': sum(r['v'] for r in dat if r['v'] < 0),
            'gana': sum(r['v'] for r in dat if r['v'] > 0), 'n_dato': len(dat),
            'n_pierde': sum(1 for r in dat if r['v'] < 0), 'n_gana': sum(1 for r in dat if r['v'] > 0),
            'n_pend': sum(1 for r in sel if r['tipo'] == 'pendiente'),
            'n_na': sum(1 for r in sel if r['tipo'] == 'no_aplica'),
            'anios': sorted({r['anio'] for r in dat if r['anio']})}


def medida_txt(sm):
    """La explicacion de la medida, la misma en todas las paginas."""
    res = resultados(sm)
    nom = {o['id']: o['nombre'].split(' (')[0] for o in sm['obras']}
    ej = [nom[k] for k, r in res.items() if r['tipo'] == 'dato' and r['base'] == 'ejercicio']
    b = balance(sm)
    return ('<b>Una sola medida en toda la herramienta.</b> Lo que cada obra gana o pierde en un año por sí misma, '
            '<b>antes del apoyo del presupuesto</b>: lo que ingresa por su operación menos lo que gasta, sin las transferencias '
            'federales. Cada obra entra con el año más reciente que publica (%s). %s Las ganancias restan a las pérdidas. '
            'Las %d obras que no publican su resultado no se estiman: quedan fuera de la suma, con su porqué, y las %d que no '
            'operan dicen «no aplica».'
            % (', '.join(str(a) for a in b['anios']),
               ('Donde solo se publica el resultado del ejercicio (%s), entra ese, y la obra lo dice.' % ', '.join(ej)) if ej else '',
               b['n_pend'], b['n_na']))
