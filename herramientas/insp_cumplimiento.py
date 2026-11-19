# -*- coding: utf-8 -*-
"""«¿Cumples con tus papeles?», el autodiagnóstico de cumplimiento documental
(19-11-2026; entrega 2 del servicio «Gobernanza documental y cumplimiento»,
pedido del autor: «continúa con el dos»).

Qué hace: según quién eres (negocio, sociedad, comerciante, patrón, actividad
vulnerable o gobierno), te hace una pregunta por cada obligación de la ley que
te alcanza, contestas «sí», «no» o «no sé», y te devuelve cuántas tienes al
corriente por área y lo que falta, cada cosa con su artículo y qué hacer.

Cada pregunta sale de una obligación escrita en el texto vigente de la Cámara de
Diputados (las mismas leyes y huellas que LEYES de insp_conservacion.py), con su
cita al pie de la letra, cotejada el 19-11-2026:

  - CFF, art. 28, frs. III y IV (contabilidad electrónica, comprobantes en el
    domicilio fiscal, envío mensual) y art. 30 (cuánto y desde cuándo).
  - Código de Comercio, arts. 38, 46 bis y 49.
  - LSS, art. 15, frs. I y II; LFT, arts. 804 y 805.
  - LFPIORPI, art. 18, frs. I, III, IV, IV Bis y VI (reformadas DOF 16-07-2025).
  - LFPDPPP (DOF 20-03-2025), arts. 10, 14, 18, 19, 29 y 31.
  - Ley General de Archivos, arts. 11, frs. II, IV y V, y 13.

**Las preguntas son `oficial` (cada una dice la ley); el resultado, `derivado`**:
es tu respuesta contada, nunca una calificación, una certificación ni una
auditoría. No es asesoría ni sustituye a tu contador o a tu abogado. La cuenta
la hace el navegador (`insp-cumplimiento.js`) y nada se guarda ni se envía;
`resumen()` es su gemela y `--prueba` las compara.
Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspcumplimiento']).
"""
import html
import json
import os
import subprocess
import sys

from presupuesto_modulos import chip
from insp_conservacion import LEYES, ley_liga

ESTILOS = ['cc-inmueble.css', 'insp-conservacion.css', 'insp-cumplimiento.css']
SCRIPTS = ['insp-cumplimiento.js']
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quién eres. «todos» es cualquier negocio o empresa (lleva contabilidad y trata
# datos personales de sus clientes o trabajadores).
PERFILES = [('moral', 'Soy una sociedad (persona moral)'), ('comerciante', 'Tengo un negocio: soy comerciante'),
            ('patron', 'Tengo trabajadores'), ('pld', 'Hago una actividad vulnerable (LFPIORPI)'),
            ('gobierno', 'Soy una dependencia, un municipio o un sujeto obligado de la Ley General de Archivos')]
QUIENES = {'todos'} | {k for k, _ in PERFILES}

AREAS = [('fiscal', '🧾', 'Fiscal'), ('mercantil', '🏪', 'Mercantil'), ('laboral', '👷', 'Laboral y seguridad social'),
         ('pld', '🛡️', 'Prevención de lavado'), ('datos', '🔒', 'Datos personales'), ('archivos', '🏢', 'Archivos públicos')]

# Cada pregunta: id, área, a quién alcanza, la pregunta, ley y artículo, la cita
# (copiada del texto vigente), qué hacer si no, y la aplicación de la plataforma
# que ayuda (si la hay).
PREGUNTAS = [
    dict(id='f_electronica', area='fiscal', quien='todos',
         q='¿Llevas tu contabilidad en medios electrónicos y tienes sus comprobantes disponibles en tu domicilio fiscal?',
         ley='cff', art='art. 28, fr. III',
         cita='Los registros o asientos que integran la contabilidad se llevarán en medios electrónicos conforme lo establezcan el Reglamento de este Código y las disposiciones de carácter general que emita el Servicio de Administración Tributaria. La documentación comprobatoria de dichos registros o asientos deberá estar disponible en el domicilio fiscal del contribuyente',
         falta='Pide a tu contador que la contabilidad quede en un sistema electrónico y define dónde viven los comprobantes (el XML de cada factura) para tenerlos a la mano en tu domicilio fiscal.',
         app=('📑', 'Lee tus facturas', 'herramienta-inspector-factura.html')),
    dict(id='f_mensual', area='fiscal', quien='todos',
         q='Si te toca, ¿envías cada mes tu información contable al SAT?',
         ley='cff', art='art. 28, fr. IV',
         cita='Ingresarán de forma mensual su información contable a través de la página de Internet del Servicio de Administración Tributaria, de conformidad con reglas de carácter general que se emitan para tal efecto',
         falta='Quién lo envía y cómo lo dicen las reglas de carácter general del SAT, y no todos los regímenes lo envían: confírmalo con tu contador. Si te toca y no lo haces, es lo primero que conviene corregir.'),
    dict(id='f_plazo', area='fiscal', quien='todos',
         q='¿Sabes hasta qué fecha guardas lo de cada año (5 años desde la declaración anual, no desde la factura)?',
         ley='cff', art='art. 30, tercer párrafo',
         cita='deberán conservarse durante un plazo de cinco años, contado a partir de la fecha en la que se presentaron o debieron haberse presentado las declaraciones con ellas relacionadas',
         falta='Saca tu calendario: lo de cada ejercicio, con la fecha mínima y su artículo. Si no conservas tu contabilidad el plazo de ley, el SAT puede revisarte 10 años en lugar de 5 (CFF, art. 67).',
         app=('🗄️', '¿Hasta cuándo guardas tus papeles?', 'herramienta-inspector-conservacion.html')),
    dict(id='f_sociedad', area='fiscal', quien='moral',
         q='¿Guardas el acta constitutiva, cada movimiento de capital y las declaraciones de la sociedad mientras exista?',
         ley='cff', art='art. 30, tercer a sexto párrafos',
         cita='dicha documentación deberá conservarse por todo el tiempo en el que subsista la sociedad o contrato de que se trate',
         falta='Junta en un solo expediente el acta, las asambleas de capital, fusión o escisión, las constancias de dividendos y las declaraciones: nada de eso se destruye a los 5 años.',
         app=('🗄️', '¿Hasta cuándo guardas tus papeles?', 'herramienta-inspector-conservacion.html')),
    dict(id='m_libros', area='mercantil', quien='comerciante',
         q='¿Conservas los libros, registros y comprobantes de tu negocio al menos 10 años?',
         ley='ccom', art='arts. 38 y 46',
         cita='Todo comerciante está obligado a conservar los libros, registros y documentos de su negocio por un plazo mínimo de diez años',
         falta='Ajusta tu calendario a 10 años: el Código de Comercio pide el doble que el SAT, y toda sociedad mercantil es comerciante (art. 3o.).',
         app=('🗄️', '¿Hasta cuándo guardas tus papeles?', 'herramienta-inspector-conservacion.html')),
    dict(id='m_contratos', area='mercantil', quien='comerciante',
         q='¿Guardas al menos 10 años los originales de tus contratos, incluidos los correos y mensajes con que cerraste un trato?',
         ley='ccom', art='art. 49',
         cita='están obligados a conservar por un plazo mínimo de diez años los originales de aquellas cartas, telegramas, mensajes de datos o cualesquiera otros documentos en que se consignen contratos, convenios o compromisos',
         falta='Define dónde se archivan los contratos y los correos que los cierran, y que nadie los borre al limpiar el buzón.'),
    dict(id='m_digital', area='mercantil', quien='comerciante',
         q='Si guardas en digital, ¿lo haces con la norma oficial mexicana de digitalización y conservación de mensajes de datos?',
         ley='ccom', art='art. 46 bis',
         cita='siempre y cuando, en estos últimos medios, se observe lo establecido en la norma oficial mexicana sobre digitalización y conservación de mensajes de datos que para tal efecto emita la Secretaría',
         falta='Escanear y tirar el papel no basta: revisa con tu proveedor de archivo que cumpla esa norma, o conserva el original.'),
    dict(id='l_imss', area='laboral', quien='patron',
         q='¿Inscribes a tus trabajadores en el IMSS y le avisas sus altas, bajas y cambios de salario en no más de 5 días hábiles?',
         ley='lss', art='art. 15, fr. I',
         cita='Registrarse e inscribir a sus trabajadores en el Instituto, comunicar sus altas y bajas, las modificaciones de su salario y los demás datos, dentro de plazos no mayores de cinco días hábiles',
         falta='Pon una fecha fija para mover los avisos al IMSS cada vez que alguien entra, sale o cambia de sueldo.',
         app=('🧮', 'Tu nómina completa', 'herramienta-calculadora-ticket.html')),
    dict(id='l_nomina', area='laboral', quien='patron',
         q='¿Llevas nóminas o listas de raya con los días trabajados y los salarios, y las guardas los 5 años siguientes al de su fecha?',
         ley='lss', art='art. 15, fr. II',
         cita='Llevar registros, tales como nóminas y listas de raya en las que se asiente invariablemente el número de días trabajados y los salarios percibidos por sus trabajadores, además de otros datos que exijan la presente Ley y sus reglamentos. Es obligatorio conservar estos registros durante los cinco años siguientes al de su fecha',
         falta='Archiva cada nómina con sus recibos (el XML de nómina) por año, y cuenta los 5 años desde el 31 de diciembre de su año.',
         app=('📑', 'Revisa un recibo de nómina', 'herramienta-inspector-factura.html')),
    dict(id='l_juicio', area='laboral', quien='patron',
         q='¿Conservas los contratos, los recibos de salario y los controles de asistencia hasta un año después de que alguien deja de trabajar contigo?',
         ley='lft', art='arts. 804 y 805',
         cita='El incumplimiento a lo dispuesto por el artículo anterior, establecerá la presunción de ser ciertos los hechos que el actor exprese en su demanda, en relación con tales documentos, salvo la prueba en contrario',
         falta='Sin esos papeles, en un juicio se presume cierto lo que diga quien te demanda. Guarda el expediente de cada persona que sale, al menos un año (y los recibos, lo que pidan el IMSS y el SAT).'),
    dict(id='p_padron', area='pld', quien='pld',
         q='¿Estás dado de alta en el Padrón de personas que realizan actividades vulnerables, y lo tienes al día?',
         ley='lfpiorpi', art='art. 18, fr. IV Bis (adicionada DOF 16-07-2025)',
         cita='Realizar su alta y registro o, en su caso, modificación o baja del Padrón de personas que realizan Actividades Vulnerables, a través del Portal en Internet',
         falta='Es una fracción nueva (julio de 2025): revisa en el portal de prevención de lavado del SAT que tu alta exista y que tus datos estén actualizados.'),
    dict(id='p_identifica', area='pld', quien='pld',
         q='¿Identificas a cada cliente con documentos oficiales y guardas copia?',
         ley='lfpiorpi', art='art. 18, fr. I',
         cita='Identificar y conocer de manera directa a las personas Clientes o Usuarias con quienes realicen la Actividad Vulnerable y verificar su identidad basándose en documentos u otros medios de identificación con reconocimiento oficial, así como recabar copia de los mismos',
         falta='Arma un expediente por cliente antes de la operación: identificación oficial, comprobante y su copia.',
         app=('🛡️', 'Revisa a tu contraparte', 'herramienta-inspector-padron.html')),
    dict(id='p_beneficiario', area='pld', quien='pld',
         q='¿Recabas los datos del beneficiario controlador de tus clientes (o la declaración de que no lo hay)?',
         ley='lfpiorpi', art='art. 18, fr. III',
         cita='recabar documentos u otros medios de identificación con reconocimiento oficial que permita identificar a su Beneficiario Controlador',
         falta='Agrega al expediente quién es el dueño real detrás de una sociedad o un fideicomiso; si es persona física, su declaración firmada.'),
    dict(id='p_custodia', area='pld', quien='pld',
         q='¿Custodias el expediente y los registros de cada operación al menos 10 años desde que se realizó?',
         ley='lfpiorpi', art='art. 18, fr. IV',
         cita='por al menos un plazo de diez años contado a partir de la fecha de la realización de la Actividad Vulnerable',
         falta='Guarda cada expediente en el domicilio que registraste ante Hacienda, físico o electrónico, y no lo destruyas antes de 10 años; un recurso o juicio interrumpe el plazo.',
         app=('🗄️', '¿Hasta cuándo guardas tus papeles?', 'herramienta-inspector-conservacion.html')),
    dict(id='p_avisos', area='pld', quien='pld',
         q='¿Presentas tus avisos y, ante una sospecha, el aviso dentro de las 24 horas siguientes?',
         ley='lfpiorpi', art='art. 18, fr. VI',
         cita='deberán presentar Aviso dentro de las 24 horas siguientes en que tuvieron conocimiento de dicha información o se generó la sospecha, incluso si el acto u operación no se celebró',
         falta='Define quién en tu empresa presenta los avisos y cómo se entera a tiempo de una sospecha: el plazo es de horas, no de días.'),
    dict(id='d_aviso', area='datos', quien='todos',
         q='¿Tienes un aviso de privacidad que diga qué datos personales tratas y para qué?',
         ley='lfpdppp', art='art. 14',
         cita='El responsable tendrá la obligación de informar a la persona titular, a través del aviso de privacidad, la existencia y características principales del tratamiento al que serán sometidos sus datos personales',
         falta='Redacta tu aviso con lo que pide el art. 15 (quién eres, qué datos, para qué, cómo ejercer los derechos) y ponlo donde recabas los datos.',
         app=('🔒', 'Nuestro aviso, como ejemplo', 'aviso-de-privacidad.html')),
    dict(id='d_seguridad', area='datos', quien='todos',
         q='¿Tienes medidas de seguridad administrativas, técnicas y físicas para los datos personales que guardas?',
         ley='lfpdppp', art='art. 18',
         cita='Todo responsable deberá establecer y mantener medidas de seguridad administrativas, técnicas y físicas que permitan proteger los datos personales contra daño, pérdida, alteración, destrucción o el uso, acceso o tratamiento no autorizado',
         falta='Empieza por lo básico: quién tiene acceso a cada archivo, contraseñas y doble factor, respaldos, y el archivero con llave. Anótalo.',
         app=('🔒', 'Cómo lo hacemos nosotros', 'aviso-de-privacidad.html#seguridad')),
    dict(id='d_vulneracion', area='datos', quien='todos',
         q='¿Sabes qué harías si se pierden, se filtran o roban datos personales que tienes (y que debes avisar de inmediato a quien afecte)?',
         ley='lfpdppp', art='art. 19',
         cita='Las vulneraciones de seguridad ocurridas en cualquier fase del tratamiento de datos personales que afecten de forma significativa los derechos patrimoniales o morales de las personas titulares le serán informadas de forma inmediata por el responsable',
         falta='Escribe un protocolo de una página: quién decide, cómo se cierra la puerta, cómo se avisa y qué se anota.',
         app=('🔒', 'Nuestro protocolo, como ejemplo', 'aviso-de-privacidad.html#vulneraciones')),
    dict(id='d_arco', area='datos', quien='todos',
         q='¿Tienes una persona o un área que atienda las solicitudes de acceso, rectificación, cancelación u oposición (ARCO)?',
         ley='lfpdppp', art='art. 29',
         cita='designará a una persona, o departamento de datos personales, quien dará trámite a las solicitudes de las personas titulares, para el ejercicio de los derechos a que se refiere la presente Ley',
         falta='Nombra a alguien y pon su correo en tu aviso de privacidad.'),
    dict(id='d_plazo', area='datos', quien='todos',
         q='¿Contestas una solicitud ARCO en no más de 20 días?',
         ley='lfpdppp', art='art. 31',
         cita='El responsable comunicará a la persona titular, en un plazo máximo de veinte días, contados desde la fecha en que se recibió la solicitud para el ejercicio de los derechos ARCO, la determinación adoptada',
         falta='Lleva un registro de cada solicitud con su fecha de entrada y de respuesta; si procede, tienes 15 días más para hacerla efectiva.'),
    dict(id='d_supresion', area='datos', quien='todos',
         q='Cuando vence el plazo de conservación, ¿bloqueas y luego suprimes los datos personales, en lugar de guardarlos «por si acaso»?',
         ley='lfpdppp', art='art. 10',
         cita='deberán ser suprimidos previo bloqueo, en su caso, y una vez que concluya el plazo de conservación de los mismos',
         falta='Usa tu calendario de conservación también para borrar: al vencer el plazo más largo, se aparta (bloqueo) y después se suprime. Guardar de más también incumple.',
         app=('🗄️', '¿Hasta cuándo guardas tus papeles?', 'herramienta-inspector-conservacion.html')),
    dict(id='a_sistema', area='archivos', quien='gobierno',
         q='¿Tienes un sistema institucional de archivos y llevas los procesos de gestión documental?',
         ley='lga', art='art. 11, fr. II',
         cita='Establecer un sistema institucional para la administración de sus archivos y llevar a cabo los procesos de gestión documental',
         falta='El art. 21 de la misma ley dice quiénes lo integran (un área coordinadora de archivos y las áreas de correspondencia, archivo de trámite, archivo de concentración y, en su caso, archivo histórico).'),
    dict(id='a_instrumentos', area='archivos', quien='gobierno',
         q='¿Tienes al día tu cuadro general de clasificación, tu catálogo de disposición documental y tus inventarios?',
         ley='lga', art='art. 13',
         cita='contarán al menos con los siguientes: I. Cuadro general de clasificación archivística; II. Catálogo de disposición documental, y III. Inventarios documentales',
         falta='Sin catálogo de disposición documental no hay plazos de conservación, y un documento sin plazo no se puede dar de baja.'),
    dict(id='a_grupo', area='archivos', quien='gobierno',
         q='¿Tienes un grupo interdisciplinario que ayude a valorar los documentos?',
         ley='lga', art='art. 11, fr. V',
         cita='Conformar un grupo interdisciplinario en términos de las disposiciones reglamentarias, que coadyuve en la valoración documental',
         falta='Conviene formarlo antes de fijar plazos o dar de baja series: es quien valora qué se guarda y cuánto.'),
    dict(id='a_registro', area='archivos', quien='gobierno',
         q='¿Inscribiste en el Registro Nacional de Archivos la existencia y ubicación de los archivos que resguardas?',
         ley='lga', art='art. 11, fr. IV',
         cita='Inscribir en el Registro Nacional la existencia y ubicación de archivos bajo su resguardo',
         falta='El Registro Nacional de Archivos lo lleva el Archivo General de la Nación: revisa ahí tu inscripción.'),
]

# Lo que casi nadie dice del «¿cumplo?».
CIEGOS = [
    ('Contestar «sí» no es estar auditado', 'Esto cuenta lo que tú respondes; no revisa tus papeles. Un «sí» que no puedes enseñar con un documento vale como «no sé».'),
    ('«No sé» también es una respuesta', 'Lo marcamos aparte del «no»: es lo primero que conviene preguntar a tu contador, a tu abogado o a tu área de cumplimiento.'),
    ('Una sociedad mercantil es comerciante', 'Si marcas «sociedad», marca también «comerciante»: el Código de Comercio le pide 10 años (art. 3o.).'),
    ('Los datos personales se te aplican aunque no vendas datos', 'Basta con tener los de tus clientes o tus trabajadores para ser responsable ante la LFPDPPP.'),
    ('No cubre todo', 'Faltan leyes de un sector (bancos, seguros, salud, aduanas, hidrocarburos), las normas estatales y lo que te pida un contrato o una autoridad en un caso concreto.'),
]


def esc(t):
    return html.escape(str(t))


# ---- La cuenta (gemela de resumen() de insp-cumplimiento.js) ----

def aplica(perfil, p):
    return p['quien'] == 'todos' or p['quien'] in perfil


def resumen(perfil, resp):
    """`perfil`: lista de claves de PERFILES; `resp`: {id: 'si'|'no'|'nose'}.
    Devuelve lo contado por área y la lista de lo que falta, en el orden de
    PREGUNTAS. Sin contestar no es «no»: va aparte."""
    perfil = set(perfil)
    out = {'aplican': 0, 'si': 0, 'no': 0, 'nose': 0, 'sin': 0, 'areas': {}, 'falta': []}
    for p in PREGUNTAS:
        if not aplica(perfil, p):
            continue
        r = resp.get(p['id'])
        k = r if r in ('si', 'no', 'nose') else 'sin'
        out['aplican'] += 1
        out[k] += 1
        a = out['areas'].setdefault(p['area'], {'aplican': 0, 'si': 0})
        a['aplican'] += 1
        if k == 'si':
            a['si'] += 1
        elif k in ('no', 'nose'):
            out['falta'].append([p['id'], k])
    return out


def datos():
    return {'preguntas': [{k: p[k] for k in ('id', 'area', 'quien')} for p in PREGUNTAS],
            'areas': [[k, ic, n] for k, ic, n in AREAS]}


def construir(base, ref):
    perf = ''.join('<label class="cs-op"><input type="checkbox" name="cuP" value="%s"> %s</label>' % (k, esc(t)) for k, t in PERFILES)
    bloques = []
    for k, ic, nombre in AREAS:
        filas = []
        for p in PREGUNTAS:
            if p['area'] != k:
                continue
            ops = ''.join('<label class="cu-r"><input type="radio" name="cu-%s" value="%s"> %s</label>' % (p['id'], v, t)
                          for v, t in (('si', 'Sí'), ('no', 'No'), ('nose', 'No sé')))
            app = ''
            if p.get('app'):
                ai, at, au = p['app']
                app = '<p class="cu-app"><a href="%s"><span aria-hidden="true">%s</span> %s</a></p>' % (esc(au), ai, esc(at))
            filas.append(
                '<li class="cu-q" id="cu-{id}" data-q="{quien}"><p class="cu-preg">{q}</p><div class="cu-ops" role="radiogroup" aria-label="{q}">{ops}</div>'
                '<details class="cs-cita"><summary>Qué dice la ley: {liga}</summary><blockquote>«…{cita}…»</blockquote>'
                '<p class="cu-falta"><b>Si no:</b> {falta}</p>{app}</details></li>'.format(
                    id=p['id'], quien=p['quien'], q=esc(p['q']), ops=ops, liga=ley_liga(p['ley'], p['art']),
                    cita=esc(p['cita']), falta=esc(p['falta']), app=app))
        bloques.append('<fieldset class="ci-grupo cu-area" data-area="%s"><legend class="ci-tit"><span aria-hidden="true">%s</span> %s</legend><ol class="cu-lista">%s</ol></fieldset>'
                       % (k, ic, esc(nombre), ''.join(filas)))
    ciegos = ''.join('<li><b>%s.</b> %s</li>' % (esc(t), esc(x)) for t, x in CIEGOS)
    usadas = []
    for p in PREGUNTAS:
        if p['ley'] not in usadas:
            usadas.append(p['ley'])
    fuentes = ' · '.join('<a href="%s">%s</a>, última reforma %s (huella SHA-256 <code>%s…</code>)' % (esc(LEYES[k][3]), esc(LEYES[k][0]), esc(LEYES[k][2]), LEYES[k][4][:12])
                         for k in usadas)
    return '''<div class="ci cs cu" id="cuRaiz">
  <section class="ci-arranque" aria-labelledby="cuTit">
    <p class="ci-kicker">Modo Inspector · gobernanza documental</p>
    <h2 class="ci-grande" id="cuTit">¿Cumples con tus papeles?</h2>
    <p class="ci-txt">Un autodiagnóstico de {n} preguntas, una por cada obligación de la ley sobre tus documentos y los datos personales que guardas: fiscal, mercantil, laboral, prevención de lavado, datos personales y archivos públicos. Contesta lo que te toca y te decimos <b>qué tienes al corriente y qué falta</b>, cada cosa con su artículo y qué hacer.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que contestas no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="cuForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Quién eres</legend>
      <div class="cs-ops">{perf}</div>
      <p class="ci-pista">Las preguntas fiscales y de datos personales son para cualquier negocio; las demás aparecen según lo que marques. Una sociedad mercantil también es comerciante (Código de Comercio, art. 3o.): marca las dos.</p>
    </fieldset>
    <p class="ci-tit cu-paso"><span class="ci-n" aria-hidden="true">2</span> Contesta: sí, no o no sé</p>
    {bloques}
    <p class="ci-acciones"><button type="submit" class="ci-boton">Dame mi diagnóstico</button></p>
  </form>

  <section class="ci-res" id="cuRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Tu diagnóstico {chip_d}</h2>
    <div class="ci-total" id="cuTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Lo que contestaste, por área</caption>
      <thead><tr><th scope="col">Área</th><th scope="col">Al corriente</th><th scope="col">Avance</th></tr></thead>
      <tbody id="cuAreas"></tbody></table></div>
    <h3 class="ci-tit">Lo que falta, con su artículo</h3>
    <ol class="ci-lista" id="cuFalta"></ol>
    <p class="ci-acciones"><button type="button" class="ci-boton cu-sec" id="cuImprime">🖨️ Imprímelo</button></p>
    <p class="ci-nota">Es tu respuesta contada (auditada), no una calificación, una certificación ni una auditoría de tus papeles. Para que alguien lo revise contra tus documentos: <a href="servicio-gobernanza.html">🗄️ el servicio de gobernanza documental</a>.</p>
  </section>

  <aside class="ci-aviso" aria-labelledby="cuCiegoTit">
    <h2 class="ci-tit" id="cuCiegoTit"><span aria-hidden="true">👁️</span> Lo que casi nadie te dice</h2>
    <ol class="ci-lista">{ciegos}</ol>
    <p><b>Lo que este autodiagnóstico no hace:</b> no es asesoría ni sustituye a tu contador o a tu abogado; no revisa tus documentos ni dice que cumples ante ninguna autoridad. Cada pregunta cita su artículo {chip_o}; el resultado solo cuenta tus respuestas.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: {fuentes} {chip_o}.</p>
    <p class="ci-hermanas">Sigue con el Modo Inspector: <a href="herramienta-inspector-conservacion.html">🗄️ ¿Hasta cuándo guardas tus papeles?</a> · <a href="herramienta-inspector-padron.html">🛡️ Revisa a tu contraparte</a> · <a href="servicio-gobernanza.html">🗄️ El servicio de gobernanza documental</a></p>
  </aside>
  <script type="application/json" id="cuDatos">{datos}</script>
</div>'''.format(n=len(PREGUNTAS), perf=perf, bloques=''.join(bloques), ciegos=ciegos, fuentes=fuentes,
                 chip_d=chip('derivado'), chip_o=chip('oficial'),
                 datos=json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'))


# ---- Prueba: la cuenta del navegador y la de aquí dan lo mismo ----

CASOS = [
    ([], {}),
    ([], {'f_electronica': 'si', 'f_mensual': 'no', 'f_plazo': 'nose', 'd_aviso': 'si', 'p_padron': 'no'}),
    (['moral', 'comerciante', 'patron'], {p['id']: 'si' for p in PREGUNTAS}),
    (['pld', 'gobierno'], {p['id']: ('no' if i % 3 else 'nose') for i, p in enumerate(PREGUNTAS)}),
    (['moral', 'comerciante', 'patron', 'pld', 'gobierno'], {'m_libros': 'si', 'a_grupo': 'no', 'x': 'si'}),
]


def prueba():
    mal = 0
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'insp-cumplimiento.js')
    prog = ("global.window={};global.document={addEventListener:function(){}};require(%s);var D=%s;"
            "var c=%s;console.log(JSON.stringify(c.map(function(x){return window.AuditorCumple.resumen(D.preguntas,x[0],x[1]);})));"
            % (json.dumps(js), json.dumps(datos(), ensure_ascii=False), json.dumps(CASOS)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    for c, n in zip(CASOS, json.loads(r.stdout)):
        py = resumen(*c)
        if py != n:
            mal += 1
            print('✗', c[0], 'Python', py, 'navegador', n)
    areas = {k for k, _, _ in AREAS}
    ids = set()
    for p in PREGUNTAS:
        if p['ley'] not in LEYES or p['quien'] not in QUIENES or p['area'] not in areas or len(p['cita']) < 30 or p['id'] in ids:
            mal += 1
            print('✗ pregunta', p['id'])
        ids.add(p['id'])
        if p.get('app') and not os.path.exists(os.path.join(RAIZ, p['app'][2].split('#')[0])):
            mal += 1
            print('✗ la pregunta %s liga a una página que no existe: %s' % (p['id'], p['app'][2]))
    # Un caso a mano: sin perfil, solo fiscal general (3) y datos (6) = 9.
    if resumen([], {})['aplican'] != 9 or resumen([], {})['sin'] != 9:
        mal += 1
        print('✗ sin perfil deberían aplicar 9 preguntas')
    if mal:
        print('%d diferencias en el autodiagnóstico de cumplimiento' % mal)
        return 1
    print('✓ Autodiagnóstico de cumplimiento: %d casos iguales en Python y en el navegador, %d preguntas con su ley' % (len(CASOS), len(PREGUNTAS)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
