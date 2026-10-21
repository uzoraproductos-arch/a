"""Los Expedientes de casos por aclarar: el capitulo «Los casos» de
«Expedientes de casos de la ASF» (expedientes.html).

Hasta el 09-10-2026 los diez expedientes se desplegaban dentro del Modo
Inspector de la portada (bloque 3); luego tuvieron pagina propia, y desde el
21-10-2026 (pedido del autor) son el primer capitulo de la aplicacion que
fusiono «Que encontro la ASF» con los Expedientes: la arma insp_asf.py con
bloque(), en la misma direccion. La pinta assets/auditor/js/expedientes.js
con las fichas de window.AUDIT_DB.expedientes: aqui no se escribe ni un
monto, solo el marco y los conceptos para leerlos.

Cada caso tiene su ancla, expedientes.html#exp-<id>; el motor manda ahi los
enlaces viejos (index.html?ir=expediente&ancla=<id>).
"""
import json

ARCHIVO = 'expedientes.html'
ESTILOS = ['expedientes.css']
SCRIPTS = ['expedientes.js']

# Los cuatro pasos de un expediente: conceptos, sin cifras.
PASOS = [
    ('🏛️', 'La ASF revisa', 'Cada año la Auditoría Superior de la Federación revisa la Cuenta Pública y publica un informe por auditoría.'),
    ('🧾', 'Pide comprobantes', 'Si el ente no demuestra en qué se fue un peso, ese peso queda «por aclarar».'),
    ('⚖️', 'Promueve acciones', 'Pliegos de observaciones, promociones de responsabilidad, avisos al SAT o denuncias de hechos.'),
    ('🔎', 'Tú lo verificas', 'Cada cifra enlaza al informe oficial. Ábrelo y compruébalo con tus propios ojos.'),
]

# Las palabras que aparecen en cada caso, en llano.
GLOSA = [
    ('Por aclarar', 'Dinero que el ente no pudo comprobar al cierre de la auditoría. No es un robo probado: es una cuenta que sigue abierta.'),
    ('Pliego de observaciones', 'La ASF presume un daño a la Hacienda Pública y exige que se repare o se justifique.'),
    ('Promoción de responsabilidad', 'La ASF pide al órgano interno de control que investigue a las personas servidoras públicas.'),
    ('Recuperado', 'Lo que el ente ya devolvió o justificó durante la auditoría.'),
]


def bloque():
    pasos = []
    for i, (ico, tit, txt) in enumerate(PASOS):
        if i:
            pasos.append('          <span class="ex-flecha" aria-hidden="true">➜</span>')
        pasos.append('          <div class="ex-paso"><span class="ex-paso-ico" aria-hidden="true">%s</span>'
                     '<b>%s</b><span>%s</span></div>' % (ico, tit, txt))
    glosa = '\n'.join('          <div><dt>%s</dt><dd>%s</dd></div>' % g for g in GLOSA)
    return '''<div class="ex-pagina">
      <section class="apartado-seccion" id="como-se-lee" aria-labelledby="como-se-lee-tit">
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="como-se-lee-tit">🧭 Cómo nace un expediente</h2>
          <p class="apartado-seccion-texto">Cuatro pasos, del informe a tus manos.</p>
        </div>
        <div class="ex-mapa">
{pasos}
        </div>
        <dl class="ex-glosa">
{glosa}
        </dl>
      </section>

      <section class="apartado-seccion" id="casos" aria-labelledby="casos-tit">
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="casos-tit">📂 Los casos</h2>
          <p class="apartado-seccion-texto">Elige un tema o pulsa un caso para ir directo a su expediente.</p>
        </div>
        <div class="ex-filtros" role="group" aria-label="Filtrar por tema">
          <span class="ex-conteo">Casos a la vista: <b id="exConteo">0</b></span>
          <div class="ex-chips" id="exChips"></div>
        </div>
        <div class="ex-indice" id="exIndice"></div>
      </section>

      <div id="exCasos" class="ex-casos">
        <noscript><p>Esta página arma los expedientes con JavaScript a partir de la base de datos de la plataforma. Actívalo para verlos.</p></noscript>
      </div>
      <script>window.EXPEDIENTES_DB = {exp_json};</script>
    </div>'''.format(pasos='\n'.join(pasos), glosa=glosa, exp_json=_exp_json())


def _exp_json():
    """Solo la coleccion de expedientes, para no descargar la base entera."""
    import auditorias
    return json.dumps(auditorias.db()['expedientes'], ensure_ascii=False,
                      separators=(',', ':')).replace('</', '<\\/')

