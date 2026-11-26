#!/usr/bin/env python3
"""Los cinco bloques de servicios.html (Ronda 24, decisión del autor, 25-11-2026).

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
    for q in QUE_HACES:
        sid = q[3].split('s=')[1]
        if sid not in ids:
            raise SystemExit('servicios_planes.py: %s no es un servicio' % q[3])


def hero(contadores):
    tira = ''.join('<li><b>%s</b> <span>%s</span></li>' % (format(v, ','), html.escape(et))
                   for k, v, et, *_ in contadores if k in ('69b', 'contratos', 'municipios', 'predial'))
    return '''<div class="svp-hero">
          <p class="svp-pre">%s Servicios y Planes</p>
          <p class="svp-hero-tit">Lo que dicen los documentos, antes de que decidas.</p>
          <p class="svp-hero-tx">Antes de pagarle a un proveedor, de comprar una casa, de votar o de recibir un gobierno: cruzamos la lista 69-B del SAT,
          los contratos públicos, la ASF y la ley. La consulta es libre; cuando quieras ir más a fondo, usas tokens o un plan.</p>
          <p class="svp-hero-acc"><a class="svp-btn svp-btn-of" href="#precio-fundador">Ver qué es gratis y los planes %s</a>
          <a class="svp-btn" href="#necesitas">Ver los servicios</a></p>
          <a class="svp-tira" href="base-al-dia.html"><ul>%s</ul><span>La base, al día: conteos de sus archivos <span class="est-chip est-derivado">auditada</span></span></a>
        </div>''' % (ico('maletin', 16), ico('flecha', 16), tira)


def que_haces():
    return '<div class="svp-cuatro">\n%s\n        </div>' % '\n'.join(
        '          <a class="svp-card" href="%s"><span class="svp-ico">%s</span><b>%s</b><span>%s</span>'
        '<span class="svp-ir">%s %s</span></a>' % (_e(liga), ico(i, 22), html.escape(t), html.escape(tx), html.escape(ir), ico('flecha', 14))
        for i, t, tx, liga, ir in QUE_HACES)


def para_quien(servicios, perfiles, sf):
    nom = {s[0]: s[2] for s in servicios}
    por = {p[1]: p for p in perfiles}
    tarjetas = []
    for i, t, tx, grupo in GRUPOS:
        svs = []
        for n in grupo:
            for sid in por[n][4]:
                if sid not in svs:
                    svs.append(sid)
        tarjetas.append(
            '          <article class="svp-card svp-perfil"><span class="svp-ico">%s</span><h3>%s</h3><p>%s</p>'
            '<p class="svp-sub">%s</p><ul>%s</ul></article>' % (
                ico(i, 22), html.escape(t), html.escape(tx), html.escape(' · '.join(grupo)),
                ''.join('<li><a href="%s">%s</a></li>' % (_e(sf.revisa_liga(s)), html.escape(nom[s])) for s in svs[:4])))
    return ('<div class="svp-cuatro">\n%s\n        </div>\n'
            '        <p class="svp-nota">Revisar no te libra de nada ni cumple por ti ante una autoridad: te da las señales, con su documento, '
            'para que decidas. Cada perfil, con su fundamento, en <a href="servicios-tu-perfil.html">Tu perfil</a>.</p>') % '\n'.join(tarjetas)


def precios():
    import monetizacion as mo
    F, M = mo.PRECIO_FUNDADOR, mo.MARCA_PRECIO
    L = F['libre']
    lis = lambda xs: ''.join('<li>%s<span>%s</span></li>' % (ico('check', 16), html.escape(x)) for x in xs)
    libre = ('<article class="svp-plan"><h3>%s</h3><p class="svp-precio">%s <small>%s</small></p>'
             '<ul>%s<li>%s<span>%d tokens de bienvenida al llegar, en tu navegador, sin cuenta ni tarjeta</span></li></ul></article>') % (
        L['nombre'], mo.pesos(0), html.escape(L['nota'].lower()), lis(L['incluye']), ico('check', 16), L['bienvenida'])
    paq = ('<article class="svp-plan"><h3>Paquetes de tokens</h3><p class="svp-precio">Pago único</p><ul>%s</ul>'
           '<p class="svp-plan-n">Lo que gasta cada acción está en la tabla de abajo.</p></article>') % ''.join(
        '<li>%s<span><b>%s</b> · %d tokens</span></li>' % (ico('check', 16), mo.pesos(p['precio']), p['tokens']) for p in F['paquetes'])
    planes = ''.join(
        ('<article class="svp-plan%s"><p class="svp-fund">Precio Fundador</p><h3>%s</h3><p class="svp-precio">%s <small>al mes</small></p>'
         '<p class="svp-plan-n">Congelado para los primeros %d · regular %s al mes · anual %s (dos meses gratis)</p>'
         '<p class="svp-para">%s</p><ul>%s</ul></article>') % (
            ' svp-plan-dest' if j == 0 else '', html.escape(p['nombre']), mo.pesos(p['precio']), F['fundadores'], mo.pesos(p['regular']),
            mo.pesos(p['anual']), html.escape(p['para']), lis(p['incluye']))
        for j, p in enumerate(F['planes']))
    med = F['medida']
    medida = ('<article class="svp-plan"><h3>%s</h3><p class="svp-precio">A medida <small>desde %s al mes</small></p><ul>%s</ul></article>') % (
        html.escape(med['nombre']), mo.pesos(med['desde']), lis(med['incluye']))
    consumo = ''.join('<tr><th scope="row">%s</th><td>%d token%s</td></tr>' % (html.escape(q), t, '' if t == 1 else 's')
                      for _k, q, t in F['consumo'])
    # Ronda 27A: lo que nunca gasta tokens, en la misma tabla (la billetera, tokens.js, lee la misma lista).
    consumo += ''.join('<tr class="svp-gratis"><th scope="row">%s</th><td>Gratis</td></tr>' % html.escape(g) for g in F['gratis'])
    return '''%s<div class="svp-planes">
          %s
          %s
          %s
          %s
        </div>
        <div class="svp-consumo">
          <table>
            <caption>Lo que gasta cada acción</caption>
            <thead><tr><th scope="col">Acción</th><th scope="col">Tokens</th></tr></thead>
            <tbody>%s</tbody>
          </table>
          <p class="svp-nota">Precios en pesos mexicanos, publicados por decisión del autor el %s. Mientras se activan los pagos en línea, hoy se opera
          con códigos piloto y promocionales: nada se cobra en esta página. Tu saldo vive en tu navegador; un código de recarga le suma tokens.</p>
        </div>
        <p class="svp-acc"><a class="svp-btn svp-btn-of" href="%s">Empezar gratis</a>
        <a class="svp-btn" href="%s" data-directa="seo">%s Canjear código / Solicitar acceso</a></p>%s''' % (
        M[0], libre, paq, planes, medida, consumo, F['decision'], AUDITOR, CANJE, ico('llave', 16), M[1])


def codigo():
    return '''<div class="svp-codigo">
          <span class="svp-ico svp-ico-oro">%s</span>
          <div>
            <p class="svp-codigo-tit">¿Tienes un código promocional o de cortesía?</p>
            <p>Si eres cliente frecuente, invitado o participaste en un piloto, tu código desbloquea los servicios privados y las promociones
            exclusivas. Se canjea en la entrada, en un paso.</p>
          </div>
          <a class="svp-btn svp-btn-of" href="%s" data-directa="seo">%s Canjear mi código promocional</a>
        </div>''' % (ico('boleto', 26), CANJE, ico('llave', 16))


def catalogo(servicios, lineas, cobro, sf):
    filas = []
    for lid, _emo, tit, tx in lineas:
        svs = [s for s in servicios if s[6] == lid]
        filas.append('''          <section class="svp-linea" aria-labelledby="svpL-%s">
            <h3 id="svpL-%s"><span class="svp-ico">%s</span>%s</h3>
            <p class="svp-linea-tx">%s</p>
            <ul>%s</ul>
          </section>''' % (lid, lid, ico(ICO_LINEA[lid], 20), html.escape(tit), html.escape(tx), ''.join(
            '<li><a href="%s"><b>%s</b><span>%s</span><small>%s</small></a><em class="svp-et%s">%s</em></li>' % (
                _e(sf.revisa_liga(s[0])), html.escape(s[2]), html.escape(s[3]), html.escape(cobro[s[0]]),
                ' svp-et-libre' if ACCESO[s[0]] == 'gratis' else '', 'Gratis' if ACCESO[s[0]] == 'gratis' else 'Con tokens / Plan')
            for s in svs)))
    return ('<div class="svp-catal">\n%s\n        </div>\n'
            '        <p class="svp-nota"><b>Gratis</b>: lo revisas tú en la plataforma, sin costo. <b>Con tokens / Plan</b>: lo que va más a fondo. '
            'Un encargo a la medida se cotiza por escrito antes de empezar. Toca un servicio para abrir su Inspector.</p>') % '\n'.join(filas)
