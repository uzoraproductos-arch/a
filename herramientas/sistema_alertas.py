#!/usr/bin/env python3
"""Los rangos del semáforo del Sistema de Alertas de Hacienda (Ronda 14, 24-11-2026).

Cierra el pendiente #7. Ninguna cifra se escribe aquí: los límites de los
rangos bajo, medio y alto salen de `docs/deuda/sistema-alertas-umbrales.json`
(Paquete de Datos 11), que copia los dos Acuerdos de la SHCP publicados en el
DOF, y se cotejaron a ojo contra las imágenes de esos PDF:

  - Reglamento del Sistema de Alertas, DOF 31-03-2017 (arts. 6, 13, 14 y 15).
  - Acuerdo de los rangos de las Entidades Federativas, DOF 30-06-2017.
  - Acuerdo 112/2017, rangos de los Municipios, DOF 31-10-2017.

Los tres PDF viven en `investigaciones/leyes/` y su huella SHA-256 se revisa
al generar: si un archivo cambia, o los límites del JSON no son continuos, la
generación se detiene.

La regla del art. 14 (cómo los tres rangos dan el color) se escribe aquí tal
como la dice el Reglamento. Tiene un hueco: con el indicador 1 en rango medio
y uno solo de los otros dos en alto, el art. 14 no dice qué nivel toca. Ese
caso no se rellena: `nivel()` devuelve None y se dice así.

`--prueba` aplica la regla a lo que publicó Hacienda (los 31 estados medidos
y los 629 municipios medidos de la Cuenta Pública 2025) y la compara con el
color que Hacienda les dio. Los indicadores vienen redondeados a un decimal,
así que un caso pegado a un límite podría no reproducirse; al 24-11-2026
se reproducen los 31 estados y 628 municipios (uno cae en el hueco), y
cualquier diferencia detiene la prueba.

    python3 herramientas/sistema_alertas.py --prueba
"""
import hashlib
import html
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = os.path.join(RAIZ, 'docs', 'deuda', 'sistema-alertas-umbrales.json')

# Cómo se llama cada indicador en corto (Reglamento, art. 6).
CORTO = {'i1': 'Deuda ÷ ingresos de libre disposición',
         'i2': 'Lo que pagó de deuda ÷ ingresos de libre disposición',
         'i3': 'Deudas de corto plazo, menos caja, ÷ ingresos totales'}
NIVELES = {'sostenible': ('Verde', 'Endeudamiento sostenible'),
           'observacion': ('Amarillo', 'Endeudamiento en observación'),
           'elevado': ('Rojo', 'Endeudamiento elevado')}
# El texto del art. 14 del Reglamento, copiado de su PDF (p. 3), y el del 15.
ART14 = [
    ('sostenible', 'el indicador de Deuda Pública y de Obligaciones sobre Ingresos de Libre Disposición se ubique en el rango bajo y '
                   'los indicadores restantes se ubiquen en el rango bajo, o uno en el rango medio y el otro en el rango bajo (fr. I)'),
    ('observacion', 'ese indicador se ubique en el rango bajo y los restantes se ubiquen en el rango medio, o uno en el rango alto y el otro '
                    'en un rango medio o bajo (fr. II, inciso a); o se ubique en el rango medio y los dos restantes en un rango medio o bajo (fr. II, inciso b)'),
    ('elevado', 'ese indicador se ubique en el rango alto (fr. III, inciso a), o en rango bajo o medio y los dos indicadores restantes '
                'se ubiquen en el rango alto (fr. III, inciso b)'),
]
ART15 = ('Quien incumpla el pago de algún financiamiento u obligación se clasifica automáticamente en endeudamiento elevado, '
         'y ahí se queda hasta que lo subsane (art. 15).')
HUECO = ('El art. 14 no dice qué nivel toca cuando el primer indicador está en rango medio y solo uno de los otros dos está en alto; '
         'en ese caso el color lo da Hacienda y no lo deducimos.')

_CACHE = []


def _sha(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for b in iter(lambda: f.read(1 << 16), b''):
            h.update(b)
    return h.hexdigest()


def carga():
    """El JSON del Paquete de Datos 11, con las huellas de sus PDF revisadas
    y los límites revisados (continuos, en orden y con su texto)."""
    if _CACHE:
        return _CACHE[0]
    S = json.load(open(ARCHIVO, encoding='utf-8'))
    for k, f in S['fuentes'].items():
        ruta = os.path.join(RAIZ, f['archivo_local'])
        if not os.path.exists(ruta):
            raise SystemExit('sistema_alertas: falta %s (%s)' % (f['archivo_local'], k))
        if _sha(ruta) != f['sha256']:
            raise SystemExit('sistema_alertas: la huella de %s no es la del JSON; vuelve a cotejar sus rangos' % f['archivo_local'])
    for nivel in ('entidades_federativas', 'municipios'):
        ids = [x['id'] for x in S[nivel]]
        if ids != ['i1', 'i2', 'i3']:
            raise SystemExit('sistema_alertas: %s trae %s, no los tres indicadores del art. 6' % (nivel, ids))
        for x in S[nivel]:
            b, m, a = x['bajo'], x['medio'], x['alto']
            if not (b['max_pct'] == m['min_exc_pct'] < m['max_pct'] == a['min_exc_pct']):
                raise SystemExit('sistema_alertas: los rangos de %s %s no son continuos' % (nivel, x['id']))
            for r, v in ((b, b['max_pct']), (a, a['min_exc_pct'])):
                if _num(v) not in r['texto']:
                    raise SystemExit('sistema_alertas: el texto «%s» de %s %s no dice %s' % (r['texto'], nivel, x['id'], v))
    _CACHE.append(S)
    return S


def _num(v):
    """Como escribe el número el JSON: «100», «7.5» o «60.0»."""
    return format(v, 'g') if v != int(v) else str(int(v))


def limites(nivel):
    """{'i1': (bajo_max, medio_max), ...} para 'e' (entidades) o 'm' (municipios)."""
    S = carga()
    L = S['entidades_federativas' if nivel == 'e' else 'municipios']
    return {x['id']: (x['bajo']['max_pct'], x['medio']['max_pct']) for x in L}


def rango(nivel, ind, v):
    b, m = limites(nivel)[ind]
    return 'bajo' if v <= b else ('medio' if v <= m else 'alto')


def nivel_de(r1, r2, r3):
    """El art. 14 al pie de la letra. None si el texto no lo dice."""
    otros = sorted([r2, r3])
    if r1 == 'bajo':
        if otros in (['bajo', 'bajo'], ['bajo', 'medio']):
            return 'sostenible'
        if otros == ['medio', 'medio'] or (otros.count('alto') == 1):
            return 'observacion'
        return 'elevado'   # los dos en alto (fr. III, b)
    if r1 == 'medio':
        if 'alto' not in otros:
            return 'observacion'
        if otros == ['alto', 'alto']:
            return 'elevado'
        return None        # el hueco
    return 'elevado'


def _pct(v):
    s = format(v, ',.1f').rstrip('0').rstrip('.')
    return s.replace('.', '.') + ' %'


def fuentes(nivel=None):
    """Las fichas de fuente {que, e, fu:{tx, url, sha256}} para el chat."""
    F = carga()['fuentes']
    def f(k, que):
        x = F[k]
        return {'que': que, 'e': 'oficial', 'fu': {'tx': '%s, DOF %s' % (x['titulo'], _fecha(x['dof'])), 'url': x['url'], 'sha256': x['sha256']}}
    L = [f('reglamento', 'Cómo los tres rangos dan el nivel de endeudamiento (Reglamento, arts. 14 y 15)')]
    if nivel in (None, 'e'):
        L.append(f('acuerdo_entidades', 'Límites de los rangos de las entidades federativas'))
    if nivel in (None, 'm'):
        L.append(f('acuerdo_municipios', 'Límites de los rangos de los municipios'))
    return L


def _fecha(iso):
    a, m, d = iso.split('-')
    return '%s-%s-%s' % (d, m, a)


def _chip(e):
    return '<span class="chip-estado est-%s">%s</span>' % (e, {'oficial': 'oficial', 'derivado': 'auditada', 'pendiente': 'pendiente'}[e])


def tabla_html(nivel, chip=None):
    """La tabla de los tres rangos de cada indicador, con su Acuerdo."""
    chip = chip or _chip
    S = carga()
    L = S['entidades_federativas' if nivel == 'e' else 'municipios']
    f = S['fuentes']['acuerdo_entidades' if nivel == 'e' else 'acuerdo_municipios']
    filas = ''.join('<tr><th scope="row">%d · %s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        i + 1, html.escape(CORTO[x['id']]), html.escape(x['bajo']['texto']), html.escape(x['medio']['texto']), html.escape(x['alto']['texto']))
        for i, x in enumerate(L))
    return ('<div class="tabla-scroll"><table class="sa-rangos"><caption>Rangos del Sistema de Alertas · %s %s</caption>'
            '<thead><tr><th scope="col">Indicador</th><th scope="col">Bajo</th><th scope="col">Medio</th><th scope="col">Alto</th></tr></thead>'
            '<tbody>%s</tbody></table></div>'
            '<p class="pl-piso-f">%s, DOF %s (<a href="%s" rel="noopener">PDF</a>; huella SHA-256 <code>%s…</code>).</p>') % (
        'entidades federativas' if nivel == 'e' else 'municipios', chip('oficial'), filas,
        html.escape(f['titulo']), _fecha(f['dof']), html.escape(f['url']), f['sha256'][:12])


def reglas_html():
    """El art. 14 y el 15, en sencillo, con su hueco dicho."""
    S = carga()
    r = S['fuentes']['reglamento']
    li = ''.join('<li><b>%s (%s)</b>: cuando %s.</li>' % (NIVELES[k][1], NIVELES[k][0].lower(), html.escape(t)) for k, t in ART14)
    return ('<p>Cómo dan el color los tres rangos (Reglamento del Sistema de Alertas, art. 14):</p><ul class="sa-reglas">%s</ul>'
            '<p>%s %s</p><p class="pl-piso-f">%s, DOF %s (<a href="%s" rel="noopener">PDF</a>; huella SHA-256 <code>%s…</code>).</p>') % (
        li, html.escape(ART15), html.escape(HUECO), html.escape(r['titulo']), _fecha(r['dof']), html.escape(r['url']), r['sha256'][:12])


def leyenda_html(nivel, chip=None):
    """Para el cajón «Cómo leer» de la deuda y la página de deuda de cada portal."""
    return ('<section class="sa-leyenda"><h4>📏 Los rangos del semáforo, con su Acuerdo</h4>%s%s'
            '<p class="pa-chico">El rango de cada indicador lo ponemos nosotros al comparar la cifra oficial con el límite del Acuerdo '
            '(«auditada»); el color del semáforo es el que publica Hacienda.</p></section>') % (tabla_html(nivel, chip), reglas_html())


def rango_txt(nivel, ind, v, chip=None):
    """«rango bajo (≤ 100%)», con chip derivado: comparar la cifra con el límite es cuenta nuestra."""
    chip = chip or _chip
    S = carga()
    x = next(y for y in S['entidades_federativas' if nivel == 'e' else 'municipios'] if y['id'] == ind)
    r = rango(nivel, ind, v)
    return 'rango %s (%s) %s' % (r, html.escape(x[r]['texto']), chip('derivado'))


def visual():
    """Lo que lee insp-visual.js (D.sda): los límites y sus fuentes, sin texto de más."""
    S = carga()
    def L(k):
        return [[x['bajo']['max_pct'], x['medio']['max_pct']] for x in S[k]]
    F = S['fuentes']
    return {'e': L('entidades_federativas'), 'm': L('municipios'),
            'fe': {'tx': 'Acuerdo de los rangos de las entidades federativas, DOF %s' % _fecha(F['acuerdo_entidades']['dof']), 'url': F['acuerdo_entidades']['url']},
            'fm': {'tx': 'Acuerdo 112/2017, rangos de los municipios, DOF %s' % _fecha(F['acuerdo_municipios']['dof']), 'url': F['acuerdo_municipios']['url']}}


def chat():
    """La respuesta del chat a «¿cuáles son los rangos del semáforo del Sistema de Alertas?»."""
    S = carga()
    E = S['entidades_federativas']
    h = ('<p>🚦 El <b>Sistema de Alertas</b> de Hacienda mide la deuda de cada estado y cada municipio con tres indicadores, pone cada uno en rango '
         '<b>bajo, medio o alto</b> con los límites que la SHCP publicó en el DOF, y con esos tres rangos da el color %s.</p>'
         '<p>Para los <b>estados</b>, la deuda ÷ ingresos de libre disposición está en rango bajo hasta el <b>%s</b> y en alto arriba del <b>%s</b>; '
         'para los <b>municipios</b>, el límite es más bajo: hasta <b>%s</b> y arriba de <b>%s</b>.</p>%s%s%s') % (
        _chip('oficial'), E[0]['bajo']['texto'].replace('≤ ', ''), E[0]['alto']['texto'].replace('> ', ''),
        S['municipios'][0]['bajo']['texto'].replace('≤ ', ''), S['municipios'][0]['alto']['texto'].replace('> ', ''),
        tabla_html('e'), tabla_html('m'), reglas_html())
    h += ('<p class="pa-chico">El semáforo no califica a un gobierno: dice cuánto le pesa la deuda inscrita en el Registro Público Único que paga con '
          'su dinero libre. Lo que se debe por otras vías (a proveedores, por ejemplo) no entra.</p>')
    ci = [{'v': E[0]['bajo']['texto'], 'etq': 'rango bajo de deuda ÷ ingresos de libre disposición (estados)', 'e': 'oficial'},
          {'v': S['municipios'][0]['bajo']['texto'], 'etq': 'rango bajo de deuda ÷ ingresos de libre disposición (municipios)', 'e': 'oficial'}]
    return {'tit': 'Los rangos del semáforo del Sistema de Alertas', 'h': h, 'fu': fuentes(), 'ci': ci,
            'ir': ['planisferio.html?d=deuda', 'la deuda en el Planisferio'],
            'sug': ['¿Cuánto debe Nuevo León?', '¿Qué municipios tienen deuda elevada?', '¿A quién le debe Chihuahua?']}


def _db():
    s = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


def _mun_sda():
    js = ('global.window={};require(%s);process.stdout.write(JSON.stringify(window.AUDIT_MUN_DEUDA.sda));'
          % json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-deuda.js')))
    return json.loads(subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True).stdout)


def prueba():
    carga()
    # La regla, caso por caso, contra el texto del art. 14.
    R = ('bajo', 'medio', 'alto')
    assert nivel_de('bajo', 'bajo', 'bajo') == 'sostenible' and nivel_de('bajo', 'medio', 'bajo') == 'sostenible'
    assert nivel_de('bajo', 'medio', 'medio') == 'observacion' and nivel_de('bajo', 'alto', 'bajo') == 'observacion'
    assert nivel_de('bajo', 'alto', 'alto') == 'elevado' and nivel_de('medio', 'alto', 'alto') == 'elevado'
    assert nivel_de('medio', 'medio', 'bajo') == 'observacion' and nivel_de('medio', 'alto', 'bajo') is None
    assert all(nivel_de('alto', a, b) == 'elevado' for a in R for b in R)
    huecos = [(a, b, c) for a in R for b in R for c in R if nivel_de(a, b, c) is None]
    assert sorted(huecos) == [('medio', 'alto', 'bajo'), ('medio', 'alto', 'medio'), ('medio', 'bajo', 'alto'), ('medio', 'medio', 'alto')], huecos
    # Contra lo que publicó Hacienda.
    color = {v[0]: k for k, v in NIVELES.items()}
    ok = dif = 0
    for e in _db()['estados']:
        if e.get('deudaSd') is None:
            continue
        n = nivel_de(rango('e', 'i1', e['deudaIld']), rango('e', 'i2', e['deudaSd']), rango('e', 'i3', e['deudaOcp']))
        if n == color[e['semaforoDeuda']]:
            ok += 1
        else:
            dif += 1
            print('  estado %s: la regla da %s, Hacienda %s' % (e['abbr'], n, e['semaforoDeuda']))
    print('estados: %d reproducen el color de Hacienda, %d no' % (ok, dif))
    if dif:
        raise SystemExit('sistema_alertas: la regla no reproduce el color de algún estado')
    M = _mun_sda()
    c = M['campos']
    i_s, i1, i2, i3 = (c.index(k) for k in ('sem', 'ildPct', 'sdPct', 'ocpPct'))
    sem = {1: 'sostenible', 2: 'observacion', 3: 'elevado'}
    okm = difm = hueco = 0
    for cve, r in sorted(M['m'].items()):
        if r[i_s] not in sem or r[i1] is None:
            continue
        n = nivel_de(rango('m', 'i1', r[i1]), rango('m', 'i2', r[i2]), rango('m', 'i3', r[i3]))
        if n is None:
            hueco += 1
        elif n == sem[r[i_s]]:
            okm += 1
        else:
            difm += 1
            if difm <= 10:
                print('  municipio %s: la regla da %s, Hacienda %s %s' % (cve, n, sem[r[i_s]], r[i1:i3 + 1]))
    print('municipios: %d reproducen el color de Hacienda, %d no, %d caen en el hueco del art. 14' % (okm, difm, hueco))
    if difm:
        raise SystemExit('sistema_alertas: la regla no reproduce el color de algún municipio (revisa si cambió el Acuerdo o el redondeo)')
    print('sistema_alertas: bien')


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        prueba()
    else:
        sys.exit(__doc__)
