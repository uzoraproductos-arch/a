# -*- coding: utf-8 -*-
"""Undécima aplicación del Modo Inspector: «Revisa a tu contraparte», el
padrón de contrapartes (18-11-2026; pedido del autor: «que nuestra base de
datos quede muy bien integrada… para llevar a cabo todo este compliance de
prevención de lavado de dinero… verificar a los clientes de nuestros
clientes… que no estén en estas listas»).

Una sola ficha por RFC con todo lo que la plataforma sabe: las listas del SAT
(art. 69, 17-H Bis, 69-B y 69-B Bis), el Directorio de Sancionados, la OFAC,
la ONU y los contratos de ComprasMX. La página no trae cifras propias: la
tabla de las listas se lee de docs/listas/listas.json (anclar_listas.py) y de
los metadatos de cada archivo; la búsqueda la hace en el navegador
assets/auditor/js/padron.js, el mismo módulo que usa el chat.

Reglas (AGENTS.md §2 y §2 bis): una coincidencia es una señal para revisar,
nunca una acusación; de las personas físicas no se publica el nombre (las
listas del SAT las guardan por la huella de su RFC), y lo que no es público
(la Lista de Personas Bloqueadas de la UIF) se dice con su nombre.
"""
import html
import json
import os

import insp_efos
from presupuesto_modulos import chip

ESTILOS = ['insp-efos.css', 'insp-padron.css']
SCRIPTS = ['padron.js', 'insp-padron.js', 'insp-padron-lote.js']

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTAS = os.path.join(RAIZ, 'docs', 'listas', 'listas.json')
SANCIONADOS = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sancionados.js')


def listas():
    """Los metadatos de las listas, ya cuadrados por anclar_listas.py."""
    m = json.load(open(LISTAS, encoding='utf-8'))
    for k, f in m['sat'].items():
        if f['morales'] + f['fisicas'] != f['rfc']:
            raise SystemExit('insp_padron: la lista %s no cuadra entre empresas y personas' % k)
    return m


def _sancionados():
    t = open(SANCIONADOS, encoding='utf-8').read()
    d = json.loads(t[t.index('{'):t.rindex('}') + 1])
    return {k: d[k] for k in ('corte', 'fuente', 'url', 'sha256')}, len(d['r'])


def _n(v):
    return format(v, ',')


def _fecha(f):
    p = f.split('-')
    return '/'.join(reversed(p)) if len(p) == 3 else f


def filas():
    """[(lista, qué quiere decir, fundamento, corte, registros, huella, url)] de todo lo que revisa el padrón."""
    m = listas()
    out = []
    for k in m['orden']:
        f = m['sat'][k]
        cuenta = '%s RFC (%s empresas y %s personas físicas)' % (_n(f['rfc']), _n(f['morales']), _n(f['fisicas']))
        out.append((f['n'], f['que'], f['fund'], f['corte'] or 'el SAT no lo fecha; bajada el ' + _fecha(f['descarga']), cuenta, f['sha256'], f['pagina']))
    b = insp_efos.meta()
    out.append(('Lista 69-B (operaciones inexistentes)', 'Quienes el SAT presume o declara emisores de facturas por operaciones que no existieron.',
                'CFF, art. 69-B', b['corte'], '%s contribuyentes' % _n(b['total']), b['sha256'], b['url']))
    s, ns = _sancionados()
    out.append(('Directorio de Proveedores y Contratistas Sancionados', 'Empresas que una dependencia sancionó o inhabilitó como proveedoras o contratistas del gobierno.',
                'LAASSP, LOPSRM y LGRA', _fecha(s['corte']), '%s empresas' % _n(ns), s['sha256'], s['url']))
    o, u = m['ofac'], m['onu']
    out.append((o['n'], o['que'], o['fund'], 'bajada el ' + _fecha(o['corte']), '%s registros (%s con domicilio en México; %s traen RFC)' % (_n(o['registros']), _n(o['mexico']), _n(o['conRfc'])),
                o['sha256'], o['pagina']))
    out.append((u['n'], u['que'], u['fund'], _fecha(u['corte']), '%s registros (%s personas y %s entidades)' % (_n(u['registros']), _n(u['personas']), _n(u['entidades'])),
                u['sha256'], u['pagina']))
    return out


NO_REVISA = [
    ('Lista de Personas Bloqueadas de la UIF', 'La Unidad de Inteligencia Financiera de Hacienda no la publica: solo la comparte con quienes la ley obliga a '
     'reportar (bancos y quienes realizan actividades vulnerables), en su acceso del SAT. Si es tu caso, consúltala ahí.'),
    ('Personas políticamente expuestas', 'Hacienda dice qué cargos hacen a alguien «persona políticamente expuesta», pero no publica una lista con nombres. '
     'Aquí no armamos una: los cargos públicos y sus sueldos están en la Enciclopedia.'),
    ('El nombre de las personas físicas', 'No lo publicamos (AGENTS.md, regla de personas privadas). Las listas del SAT las guardamos por la huella de su RFC: '
     'con el RFC exacto te decimos si coincide, nunca quién es.'),
    ('Registro Nacional de Obligaciones Alimentarias', 'No se copia ni se consulta aquí: protege a menores de edad. Se pide un certificado en su portal oficial.'),
]


def construir(base, ref):
    m = listas()
    fl = filas()
    tabla = ''.join('<tr><th scope="row">%s<small>%s</small></th><td>%s</td><td>Corte: %s<br>%s %s</td><td><code title="%s">%s…</code></td></tr>' % (
        html.escape(a), html.escape(b), html.escape(c), html.escape(d), html.escape(e), chip('oficial'), html.escape(h), html.escape(h[:12]))
        for a, b, c, d, e, h, _u in fl)
    fuentes = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s ↗</a></li>' % (html.escape(u), html.escape(a)) for a, _b, _c, _d, _e, _h, u in fl)
    no = ''.join('<li><b>%s.</b> %s</li>' % (html.escape(a), html.escape(b)) for a, b in NO_REVISA)
    return '''
<div class="ef pd" id="pd">
  <section class="ef-hero" aria-labelledby="pd-tit">
    <h2 class="ef-hero-tit" id="pd-tit">¿Con quién estás tratando?</h2>
    <p class="ef-hero-txt">Escribe el <b>RFC</b> de tu cliente, tu proveedor o el cliente de tu cliente, y te decimos en una sola ficha si aparece en <b>%(nlistas)d listas oficiales</b> %(chip_of)s:
      las del SAT, el Directorio de Sancionados, la OFAC y la ONU, y si tiene contratos con el gobierno. Con un <b>nombre</b> buscamos en la OFAC y la ONU.</p>
    <form class="ef-busca" id="pdForm" role="search" action="herramienta-inspector-padron.html" method="get">
      <label class="ef-lbl" for="pdQ">RFC (uno o varios) o nombre</label>
      <div class="ef-busca-fila">
        <input type="search" id="pdQ" name="q" class="ef-input" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="AAA010101AAA">
        <button type="submit" class="ef-btn">🔎 Revisar</button>
      </div>
    </form>
    <p class="cf-privado">🔒 La búsqueda se hace en tu navegador: no guardamos ni vemos lo que escribes.</p>
    <div id="pdRes" class="pd-res" aria-live="polite"></div>
  </section>

  <section class="ef-sec" id="lote" aria-labelledby="pd-lote-tit">
    <h2 id="pd-lote-tit">📂 Revisa un lote o tus facturas</h2>
    <p>Sube un <b>CSV o TXT</b> con la lista de tus clientes o proveedores (hasta 2,000 RFC; basta con que cada renglón traiga el RFC), o tus <b>facturas en XML</b>.
      Con las facturas te digo quién te factura, a quién le facturas y <b>por cuenta de quién</b>: los RFC «a cuenta de terceros» de cada concepto (CFDI 4.0).
      El resultado es una <b>matriz</b>: una fila por RFC y una columna por lista, que puedes descargar en CSV.</p>
    <div class="pd-suelta" id="pdSuelta">
      <label class="ef-lbl" for="pdArch">Tu archivo (CSV, TXT o facturas XML; puedes elegir varios)</label>
      <input type="file" id="pdArch" class="pd-archivo" accept=".csv,.txt,.xml,text/csv,text/plain,text/xml,application/xml" multiple>
      <p class="pd-chico">o arrástralos aquí</p>
    </div>
    <details class="pd-pegar"><summary>O pega la columna de RFC desde Excel</summary>
      <label class="ef-lbl" for="pdPega">RFC, uno por renglón</label>
      <textarea id="pdPega" class="ef-input pd-pega" rows="5" spellcheck="false" autocapitalize="characters"></textarea>
      <button type="button" class="ef-btn" id="pdLoteBtn">🔎 Revisar el lote</button>
    </details>
    <p class="cf-privado">🔒 Tus archivos se leen en tu navegador: no se suben a ningún lado.</p>
    <div id="pdLote" class="pd-res" aria-live="polite"></div>
  </section>

  <section class="ef-sec" aria-labelledby="pd-listas">
    <h2 id="pd-listas">📚 Las listas que revisamos</h2>
    <p>Cada una se baja de su fuente oficial con la huella SHA-256 del archivo, y si sus columnas cambian o sus cuentas no cuadran, la plataforma se detiene antes de publicarla.
      En total, <b>%(rfc)s RFC</b> en las listas del SAT del artículo 69, el 17-H Bis y el 69-B Bis (%(mor)s de empresas y %(fis)s de personas físicas).</p>
    <div class="leg-tabla-caja"><table class="leg-tabla"><caption>Lo que revisa el padrón de contrapartes</caption>
      <thead><tr><th scope="col">Lista y qué quiere decir</th><th scope="col">Fundamento</th><th scope="col">Corte y registros</th><th scope="col">Huella</th></tr></thead>
      <tbody>%(tabla)s</tbody></table></div>
    <details class="pd-fuentes"><summary>Las fuentes oficiales</summary><ul>%(fuentes)s</ul></details>
  </section>

  <section class="ef-sec" aria-labelledby="pd-leer">
    <h2 id="pd-leer">⚖️ Cómo leer el resultado</h2>
    <ul class="pd-lista">
      <li>⛔ <b>Señal fuerte:</b> definitivo en la 69-B, sentencia por delito fiscal, OFAC u ONU.</li>
      <li>⚠️ <b>Señal para revisar:</b> presunto en la 69-B, no localizado, crédito firme o exigible, sello digital sin efectos, sancionado como proveedor.</li>
      <li>ℹ️ <b>Antecedente:</b> un crédito que el SAT canceló por incosteable o por insolvencia.</li>
      <li>✅ <b>Salió:</b> desvirtuó la presunción o un tribunal le dio la razón.</li>
    </ul>
    <p>Ninguna señal es una acusación ni se suma en una calificación: las del SAT son determinaciones administrativas, no condenas, y coincidir en un nombre no es ser la misma persona.
      No aparecer tampoco certifica a nadie. Lo que sigue es <b>revisar el documento</b> y, si tu actividad es vulnerable, documentarlo en tu expediente de identificación del cliente.</p>
  </section>

  <section class="ef-sec" aria-labelledby="pd-no">
    <h2 id="pd-no">🚫 Lo que no revisamos, y por qué</h2>
    <ul>%(no)s</ul>
    <p>¿Necesitas revisarlo cada mes, con más de 2,000 contrapartes o con el expediente de identificación de cada cliente? <a href="servicios.html">Pide un servicio</a>; el
      <a href="herramienta-inspector-factura.html">Lector de facturas</a> también cruza a cada emisor con la lista 69-B.</p>
  </section>
</div>''' % {'nlistas': len(fl), 'chip_of': chip('oficial'), 'rfc': _n(m['rfc']), 'mor': _n(m['morales']), 'fis': _n(m['fisicas']),
             'tabla': tabla, 'fuentes': fuentes, 'no': no}
