#!/usr/bin/env python3
"""Los bloques de servicios.html (Ronda 24, decisión del autor, 25-11-2026; reordenados en la Ronda 30, 27-11-2026:
un solo encabezado con la regla del cobro, los planes con su botón, la banda del código y el catálogo como mostrador
con filtro por perfil y por objetivo, que reúne «¿A quién va dirigido?» y «Los servicios»). Lo que sigue describe
las piezas; el orden lo pone apartados.py.

1. ¿Qué puedes hacer y para qué te sirve? (cuatro tarjetas, `QUE_HACES`).
2. ¿A quién va dirigido? (cuatro perfiles, `GRUPOS`, que reúnen los diez de `PERFILES` de apartados.py: **un perfil
   nuevo de PERFILES necesita aquí su grupo**, o la generación se detiene).
3. Qué es gratis y los planes, con el Precio Fundador: **los montos salen solo de monetizacion.PRECIO_FUNDADOR** y van
   dentro de su marca (<!--precio-fundador-->); apartados.pagina() detiene la generación si aparece uno fuera.
4. ¿Tienes un código promocional o de cortesía? (lleva a canjea-tu-codigo.html).
5. El catálogo de los servicios por objetivo (las familias de `LINEAS`), cada uno con «Gratis» o «Con tokens / Plan»
   (`ACCESO`: **un servicio nuevo necesita ahí su renglón**).

Sin emojis: íconos SVG de trazo (auditor_bento.ico). Los pagos en línea siguen apagados: hoy se opera con códigos
piloto y promocionales; la página lo dice junto a los botones.
"""
import html

from auditor_bento import ico

CANJE = 'canjea-tu-codigo.html'
COTIZA = 'servicios-cotiza.html'
AUDITOR = 'herramienta-inspector-pregunta.html'

# (ícono, título, para qué te sirve, liga dentro de Servicios, texto de la liga)
QUE_HACES = [
    ('mapa', 'El dinero público, con sus documentos oficiales',
     'Lo que le entra y lo que gasta tu estado o tu municipio, su deuda, sus contratos y lo que la ASF dejó por aclarar, cada cifra con su fuente.',
     'servicios-revisa.html?s=radiografia', 'Revisa un gobierno'),
    ('escudo', 'Blindaje 69-B, Cero CIEC',
     'Tus proveedores y tus facturas XML contra la lista 69-B del SAT, el Directorio de Sancionados, la OFAC y la ONU, leídos en tu navegador. '
     'Nunca te pedimos la Contraseña del SAT.', 'servicios-revisa.html?s=contrapartes', 'Revisa tu cartera'),
    ('casa', 'Revisión patrimonial inmobiliaria',
     'Antes de comprar o rentar: el predial según la ley de su municipio, el Índice SHF de la vivienda y con quién firmas.',
     'servicios-revisa.html?s=simulacion', 'Simula tu caso'),
    ('documento', 'Dictámenes verificables con huella SHA-256',
     'Cada revisión cierra con un dictamen con folio y huella SHA-256: se repite la consulta y se comprueba que nada cambió. '
     'No es un documento oficial ni un peritaje.', 'servicios-revisa.html?s=revision', 'Genera un dictamen'),
]
# (ícono, nombre, para qué, [nombres de PERFILES de apartados.py])
GRUPOS = [
    ('usuario', 'Ciudadanos y familias', 'Saber en qué se va tu dinero, revisar el predial antes de comprar y entender a tu municipio.',
     ['Ciudadanía']),
    ('maletin', 'Empresas, PyMEs y contadores', 'Antes de pagarle a un proveedor o de aceptar a un cliente: la 69-B, tus facturas y tu nómina.',
     ['Contaduría y despachos contables', 'Empresas y áreas de compras', 'Derecho y cumplimiento']),
    ('pluma', 'Periodistas, investigadores y ONG', 'Cotejar una nota, seguir una promesa de gasto y armar un expediente con sus documentos.',
     ['Periodismo e investigación', 'Universidades y academia', 'Auditoría, control interno y auditoría forense']),
    ('edificio', 'Despachos y gobiernos locales', 'La radiografía de un gobierno, la entrega-recepción y talleres para tu equipo.',
     ['Gobiernos y dependencias', 'Regidurías, congresos y su asesoría', 'Candidaturas y equipos de campaña']),
]
# Cada servicio: 'gratis' (lo haces tú en la plataforma, sin costo; el encargo a la medida se cotiza) o 'tokens'.
ACCESO = {
    'diligencia': 'gratis', 'contrapartes': 'gratis', 'radiografia': 'gratis', 'escenarios': 'gratis',
    'seguimiento': 'tokens', 'facturas': 'tokens', 'nomina': 'tokens', 'gobernanza': 'tokens', 'temporada': 'tokens',
    'entrega': 'tokens', 'revision': 'tokens', 'expediente': 'tokens', 'capacitacion': 'tokens', 'licencia': 'tokens',
    'simulacion': 'tokens',
}
# Ronda 30: el nombre corto de cada grupo de GRUPOS, para el filtro «Soy» del catálogo (mismo orden).
GRUPOS_CORTO = ['Ciudadanos', 'Empresas y contadores', 'Periodistas e investigadores', 'Gobiernos y despachos']
ICO_LINEA = {'prevencion': 'escudo', 'electoral': 'edificio', 'formacion': 'pluma', 'investigacion': 'lupa', 'simuladores': 'casa'}


def _e(x):
    return html.escape(x, quote=True)


def revisa(servicios, perfiles, lineas):
    nom = [p[1] for p in perfiles]
    agrupados = [n for g in GRUPOS for n in g[3]]
    if sorted(agrupados) != sorted(nom):
        raise SystemExit('servicios_planes.py: GRUPOS no reúne exactamente los perfiles de PERFILES (faltan: %s; sobran: %s)'
                         % (', '.join(set(nom) - set(agrupados)) or '—', ', '.join(set(agrupados) - set(nom)) or '—'))
    ids = {s[0] for s in servicios}
    if set(ACCESO) != ids or set(ACCESO.values()) - {'gratis', 'tokens'}:
        raise SystemExit('servicios_planes.py: ACCESO no trae los mismos servicios que SERVICIOS')
    if set(ICO_LINEA) != {l[0] for l in lineas}:
        raise SystemExit('servicios_planes.py: cada línea de LINEAS necesita su ícono en ICO_LINEA')
    if len(GRUPOS_CORTO) != len(GRUPOS):
        raise SystemExit('servicios_planes.py: cada grupo de GRUPOS necesita su nombre corto en GRUPOS_CORTO')
    for q in QUE_HACES:
        sid = q[3].split('s=')[1]
        if sid not in ids:
            raise SystemExit('servicios_planes.py: %s no es un servicio' % q[3])


def hero(contadores, operan=True):
    """El único encabezado de la página (Ronda 30): la promesa, los dos botones, la regla del cobro y la tira de la base."""
    tira = ''.join('<li><b>%s</b> <span>%s</span></li>' % (format(v, ','), html.escape(et))
                   for k, v, et, *_ in contadores if k in ('69b', 'contratos', 'municipios', 'predial'))
    return '''<div class="svp-hero">
          <p class="svp-pre">%s Servicios y Planes</p>
          <p class="svp-hero-tit">Lo que dicen los documentos, antes de que decidas.</p>
          <p class="svp-hero-tx">Antes de pagarle a un proveedor, de comprar una casa, de votar o de recibir un gobierno: cruzamos la lista 69-B del SAT,
          los contratos públicos, la ASF y la ley.</p>
          <p class="svp-hero-acc"><a class="svp-btn svp-btn-of" href="#precio-fundador">Ver qué es gratis y los planes %s</a>
          <a class="svp-btn" href="#necesitas">Ver los servicios</a></p>
          %s
          <a class="svp-tira" href="base-al-dia.html"><ul>%s</ul><span>La base, al día: conteos de sus archivos <span class="est-chip est-derivado">auditada</span></span></a>
        </div>''' % (ico('maletin', 16), ico('flecha', 16), regla(operan), tira)


def regla(operan=True):
    """La regla del cobro, una sola en toda la sección (Ronda 30): revisarlo tú, con plan o por encargo."""
    import monetizacion as mo
    enc = ('Lo hacemos nosotros y se cotiza por escrito antes de empezar. Hoy, con un código de acceso vigente.' if operan
           else 'Lo hacemos nosotros y se cotiza por escrito. Se abre con el lanzamiento de la plataforma.')
    return ('<ul class="svp-regla" aria-label="Cómo se cobra">'
            '<li>%s<span><b>Revísalo tú</b> Gratis o con tokens, aquí mismo: %d gratis cada mes.</span></li>'
            '<li>%s<span><b>Con un plan</b> Más tokens cada mes, con Precio Fundador.</span></li>'
            '<li>%s<span><b>Por encargo</b> %s</span></li></ul>') % (
        ico('lupa', 18), mo.PRECIO_FUNDADOR['libre']['bienvenida'], ico('boleto', 18), ico('documento', 18), enc)


def nav():
    """La tira de secciones, fija arriba al bajar (Ronda 30)."""
    return ('<nav class="svp-nav" aria-label="En esta página"><a href="#precio-fundador">Planes</a><a href="#necesitas">Servicios</a>'
            '<a href="#arriesgas">Lo que arriesgas</a><a href="#preguntas-f">Preguntas</a></nav>')


def que_haces():
    return '<div class="svp-cuatro svp-cuatro-c">\n%s\n        </div>' % '\n'.join(
        '          <a class="svp-card" href="%s"><span class="svp-ico">%s</span><b>%s</b><span>%s</span>'
        '<span class="svp-ir">%s %s</span></a>' % (_e(liga), ico(i, 22), html.escape(t), html.escape(tx), html.escape(ir), ico('flecha', 14))
        for i, t, tx, liga, ir in QUE_HACES)


def precios():
    """Los planes, cada uno con su botón (Ronda 30, decisión del autor). Los pagos en línea siguen apagados: los botones
    de pago llevan a «Solicitar código» de la entrada, con el plan anotado (?interes=), y la página lo dice."""
    import monetizacion as mo
    from urllib.parse import quote
    F, M = mo.PRECIO_FUNDADOR, mo.MARCA_PRECIO
    L = F['libre']
    lis = lambda xs: ''.join('<li>%s<span>%s</span></li>' % (ico('check', 16), html.escape(x)) for x in xs)
    pide = lambda que, txt, of=False: ('<a class="svp-btn svp-plan-btn%s" href="%s?pedir=1&amp;interes=%s" data-directa="seo">%s</a>'
                                       % (' svp-btn-of' if of else '', CANJE, quote(que), html.escape(txt)))
    libre = ('<article class="svp-plan"><h3>%s</h3><p class="svp-precio">%s <small>%s</small></p>'
             '<ul>%s<li>%s<span>%d tokens gratis cada mes, en tu navegador, sin cuenta ni tarjeta</span></li></ul>'
             '<a class="svp-btn svp-plan-btn svp-btn-mar" href="%s">Empezar gratis</a></article>') % (
        L['nombre'], mo.pesos(0), html.escape(L['nota'].lower()), lis(L['incluye']), ico('check', 16), L['bienvenida'], AUDITOR)
    paq = ('<article class="svp-plan"><h3>Paquetes de tokens</h3><p class="svp-precio">Pago único <small>sin mensualidad</small></p><ul>%s</ul>'
           '<p class="svp-plan-n">Para cuando se te acaban los tokens gratis del mes. Lo que gasta cada acción está en la tabla de abajo.</p>%s</article>') % (
        ''.join('<li>%s<span><b>%s</b> · %d tokens</span></li>' % (ico('check', 16), mo.pesos(p['precio']), p['tokens']) for p in F['paquetes']),
        pide('Paquete de tokens', 'Solicitar código de recarga'))
    planes = ''.join(
        ('<article class="svp-plan%s"><p class="svp-fund">Precio Fundador</p><h3>%s</h3><p class="svp-precio">%s <small>al mes</small></p>'
         '<p class="svp-plan-n">Congelado para los primeros %d · regular %s al mes · anual %s (dos meses gratis)</p>'
         '<p class="svp-para">%s</p><ul>%s</ul>%s</article>') % (
            ' svp-plan-dest' if j == 0 else '', html.escape(p['nombre']), mo.pesos(p['precio']), F['fundadores'], mo.pesos(p['regular']),
            mo.pesos(p['anual']), html.escape(p['para']), lis(p['incluye']), pide(p['nombre'], 'Apartar Precio Fundador', j == 0))
        for j, p in enumerate(F['planes']))
    med = F['medida']
    medida = ('<article class="svp-plan"><h3>%s</h3><p class="svp-precio">A medida <small>desde %s al mes</small></p><ul>%s</ul>'
              '<p class="svp-plan-n">Para dependencias, ayuntamientos y corporativos: se arma contigo y se cotiza por escrito.</p>'
              '<a class="svp-btn svp-plan-btn" href="%s">Solicitar cotización</a></article>') % (
        html.escape(med['nombre']), mo.pesos(med['desde']), lis(med['incluye']), COTIZA)
    consumo = ''.join('<tr><th scope="row">%s</th><td>%d token%s</td></tr>' % (html.escape(q), t, '' if t == 1 else 's')
                      for _k, q, t in F['consumo'])
    # Ronda 27A: lo que nunca gasta tokens, junto a la tabla (la billetera, tokens.js, lee la misma lista).
    gratis = ''.join('<tr class="svp-gratis"><th scope="row">%s</th><td>Gratis</td></tr>' % html.escape(g) for g in F['gratis'])
    tabla = lambda cap, cab2, filas: ('<table><caption>%s</caption><thead><tr><th scope="col">Acción</th><th scope="col">%s</th></tr></thead>'
                                      '<tbody>%s</tbody></table>') % (cap, cab2, filas)
    return '''%s<div class="svp-planes">
          %s
          %s
          %s
          %s
        </div>
        <p class="svp-nota svp-hoy">%s <span><b>Hoy se opera con códigos piloto y promocionales: nada se cobra en esta página.</b> Los botones de los paquetes y
        de los planes abren la solicitud de tu código, con lo que elegiste ya anotado; los pagos en línea se activan después.
        ¿Ya tienes código? <a href="%s" data-directa="seo">Canjéalo</a>.</span></p>
        <details class="svp-consumo">
          <summary>%s Lo que gasta cada acción y lo que siempre es gratis</summary>
          <div class="svp-consumo-dos">
            %s
            %s
          </div>
          <p class="svp-nota">Precios en pesos mexicanos, publicados por decisión del autor el %s. Tu saldo vive en tu navegador; un código de recarga
          le suma tokens.</p>
        </details>%s''' % (
        M[0], libre, paq, planes, medida, ico('llave', 18), CANJE, ico('boleto', 18),
        tabla('Lo que gasta tokens', 'Tokens', consumo), tabla('Lo que siempre es gratis', 'Costo', gratis), F['decision'], M[1])


def codigo():
    return '''<div class="svp-codigo">
          <span class="svp-ico svp-ico-oro">%s</span>
          <p><b>¿Tienes un código promocional o de cortesía?</b> Si eres cliente frecuente, invitado o participaste en un piloto, tu código
          suma tokens o abre los encargos. Se canjea en la entrada, en un paso.</p>
          <a class="svp-btn svp-btn-of" href="%s" data-directa="seo">%s Canjear mi código</a>
        </div>''' % (ico('boleto', 22), CANJE, ico('llave', 16))


def catalogo(servicios, lineas, cobro, perfiles, sf):
    """El mostrador (Ronda 30): los servicios en tarjetas, con dos filtros que se combinan, «Soy» (los grupos de GRUPOS)
    y «Busco» (las familias de LINEAS). Sin JavaScript se ven todos. La etiqueta de cada uno sale de ACCESO y de la
    tabla del Precio Fundador: nunca se escribe un número aquí."""
    import monetizacion as mo
    por = {p[1]: p for p in perfiles}
    de_grupo = [{sid for n in g[3] for sid in por[n][4]} for g in GRUPOS]
    nom_l = {l[0]: l[2] for l in lineas}
    orden = [l[0] for l in lineas]
    tok = mo.consumo('servicio')
    chips = lambda grupo, ops: ''.join(
        '<button type="button" class="svp-chip" data-svp-f="%s" data-v="%s" aria-pressed="%s">%s</button>' % (
            grupo, v, 'true' if v == '' else 'false', html.escape(t)) for v, t in ops)
    filtros = ('<div class="svp-filtros" id="svpFiltros">'
               '<p class="svp-filtro"><span id="svpFG">Soy</span><span class="svp-chips" role="group" aria-labelledby="svpFG">%s</span></p>'
               '<p class="svp-filtro"><span id="svpFL">Busco</span><span class="svp-chips" role="group" aria-labelledby="svpFL">%s</span></p>'
               '<p class="svp-cuenta" id="svpCuenta" aria-live="polite">%d servicios</p></div>') % (
        chips('g', [('', 'Todos')] + [('g%d' % i, c) for i, c in enumerate(GRUPOS_CORTO)]),
        chips('l', [('', 'Todo')] + [(lid, nom_l[lid]) for lid in orden]), len(servicios))
    tarjetas = []
    for s in sorted(servicios, key=lambda x: orden.index(x[6])):
        sid = s[0]
        gs = ' '.join('g%d' % i for i, d in enumerate(de_grupo) if sid in d)
        libre = ACCESO[sid] == 'gratis'
        tarjetas.append(
            '          <li class="svp-srv" data-g="%s" data-l="%s"><span class="svp-srv-l">%s %s</span>'
            '<a class="svp-srv-n" href="%s">%s</a><p class="svp-srv-tx">%s</p>'
            '<p class="svp-srv-pie"><em class="svp-et%s">%s</em><span>Por encargo: %s</span></p>'
            '<p class="svp-srv-acc"><a class="svp-srv-ir" href="%s" aria-label="Revisar: %s">Revisar %s</a>'
            '<a class="svp-srv-ficha" href="servicio-%s.html" aria-label="Ficha de %s">Ver su ficha</a></p></li>' % (
                gs, s[6], ico(ICO_LINEA[s[6]], 16), html.escape(nom_l[s[6]]), _e(sf.revisa_liga(sid)), html.escape(s[2]), html.escape(s[3]),
                ' svp-et-libre' if libre else '', 'Gratis' if libre else '%d tokens' % tok,
                html.escape(cobro[sid][0].lower() + cobro[sid][1:]), _e(sf.revisa_liga(sid)), _e(s[2]), ico('flecha', 14), sid, _e(s[2])))
    return ('%s\n        <ul class="svp-mostrador" id="svpMostrador">\n%s\n        </ul>\n'
            '        <p class="svp-vacio" id="svpVacio" hidden>Ningún servicio con esos dos filtros. <button type="button" class="svp-chip" id="svpTodos">Ver todos</button></p>\n'
            '        <p class="svp-nota"><b>Gratis</b> o <b>%d tokens</b> es lo que gasta revisarlo tú, aquí mismo, en su Inspector. <b>Por encargo</b> lo hacemos '
            'nosotros y se cotiza por escrito antes de empezar. Revisar no te libra de nada ni cumple por ti ante una autoridad: te da las señales, con su '
            'documento, para que decidas. Cada perfil, con su fundamento, en <a href="servicios-tu-perfil.html">Tu perfil</a>.</p>') % (
        filtros, '\n'.join(tarjetas), tok)
