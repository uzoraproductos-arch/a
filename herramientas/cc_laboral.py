# -*- coding: utf-8 -*-
"""Novena aplicación de la Calculadora Cívica: «Tu finiquito o tu
liquidación» (20-11-2026, pedido del autor: «construye el simulador
laboral», tras «en el simulador también me refería al estado de cuenta
cívico, ambiental, nómina, predial, laboral»).

Saca lo que le toca a una persona trabajadora al terminar su relación de
trabajo (apartado A del art. 123 constitucional, Ley Federal del Trabajo) y la
retención aproximada de ISR, cada renglón con su artículo. Cotejado el
20-11-2026 contra los textos vigentes de la Cámara de Diputados (huella
SHA-256 de cada PDF abajo):

  - LFT (última reforma DOF 14-05-2026):
    art. 79: vacaciones proporcionales si la relación termina antes del año;
    art. 76: doce días al cumplir el primer año, dos más por año hasta veinte
      y, desde el sexto, dos más por cada cinco;
    art. 80: prima vacacional no menor de 25 %;
    art. 87: aguinaldo de 15 días por lo menos, y su parte proporcional;
    art. 84 y 89: el salario para indemnizar incluye la cuota diaria y la
      parte proporcional de las prestaciones; el mensual se divide entre 30;
    art. 48: despido sin causa probada, tres meses de salario (los salarios
      vencidos dependen del juicio: no se calculan);
    arts. 49 y 50, fr. II y III: si el patrón no reinstala (o la persona
      rescinde por causa del patrón, arts. 51 y 52), además veinte días por
      año de servicios en la relación por tiempo indeterminado;
    art. 162: prima de antigüedad de doce días por año, a quien es separado
      con causa o sin ella y a quien se va por su voluntad con quince años o
      más; su salario entre uno y dos salarios mínimos (arts. 485 y 486).
  - LISR (última reforma DOF 13-11-2026, sin cambios en estos artículos), art. 93, fr. XIII y XIV: exentos
    hasta 90 veces por año de servicio lo de la separación (fracción de más
    de seis meses, año completo), 30 el aguinaldo y 15 la prima vacacional;
    la ley dice «salario mínimo» y desde la reforma de desindexación (CPEUM,
    DOF 27-01-2016, transitorio tercero) se lee como UMA;
    art. 96: la retención de lo de la separación usa la tasa del último
    sueldo mensual ordinario (o la tarifa, si lo pagado es menor).
  - RLISR, art. 174: la retención opcional del aguinaldo y la prima
    vacacional (÷ 365 × 30.4).

Segunda entrega (20-11-2026, «continúa con los pendientes a calcular»):
el subsidio para el empleo (decreto DOF 31-12-2025, `SUBSIDIO`); los
salarios vencidos y sus intereses como escenario (art. 48, párrafos segundo
y tercero), fuera del total; el reparto de utilidades (arts. 122 a 127), con
los datos del proyecto de la comisión mixta, también aparte; y el apartado B
(LFTSE, `LFTSE`): salario pendiente y aguinaldo de 40 días (art. 42 Bis); la
indemnización y los salarios caídos los fija el laudo (art. 43, fr. III y IV).

**Las reglas son `oficial` y la cuenta, `derivado`.** Lo nuestro se dice: los
años de 365 días, la parte del último año en proporción, el mes de 30 días,
el salario integrado con aguinaldo y prima vacacional, y que el salario y las
vacaciones se tasan como si fueran todo el ingreso del mes, sin el subsidio
para el empleo (ya no: ver la segunda entrega). **No es asesoría legal ni un
convenio**: lo que vale es lo que pacten ante el Centro de Conciliación o
resuelva el Tribunal. No aplica a contratos por obra determinada (el art. 50
no los nombra) ni a quien trabaja para un estado o un municipio.

Tercera entrega (20-11-2026, «continúa con los pendientes»): el tipo de
contrato (`TIPOS`). El eventual (art. 50, fr. I): la mitad de los salarios
del tiempo trabajado si fue menos de un año, o seis meses y veinte días por
año siguiente, en lugar de la fr. II; la causa `vence` (art. 53, fr. III); el
reparto con sesenta días o más (art. 127, fr. VII). La plataforma digital
(art. 50, fr. IV): sin finiquito (art. 291-F) y tres meses del promedio de
seis meses (art. 291-N). **Una ley ambigua no se interpreta para sacar una
cifra**: la prima de antigüedad fuera de planta (art. 162), y en plataformas
los veinte días por año del «tiempo efectivamente laborado», los vencidos y el
ISR van en `espera`, con su porqué, y no se suman. `calcula()` y la de `cc-laboral.js` son gemelas (`--prueba`).
Lo llama apartados.insp_nativa() (INSP_NATIVAS['cclaboral']).
"""
import datetime
import html
import json
import os
import subprocess
import sys

from presupuesto_modulos import chip
import cc_inmueble

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTILOS = ['cc-inmueble.css']
SCRIPTS = ['cc-laboral.js']

LFT = {'tx': 'Ley Federal del Trabajo, texto vigente (Cámara de Diputados, última reforma DOF 14-05-2026)',
       'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf',
       'sha256': '12f09393a1951a91c3f57f579bf611b034edf1a5f78cdbfb828e23ff3a9acbf7'}
RLISR = {'tx': 'Reglamento de la Ley del Impuesto sobre la Renta (Cámara de Diputados, última reforma DOF 06-05-2016)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LISR_060516.pdf',
         'sha256': '0538fd2fa3da9705370350b1e25a1656cc681d2c489545334079e1b35360d6e3'}
CPEUM = {'tx': 'Constitución Política de los Estados Unidos Mexicanos (Cámara de Diputados), decreto de desindexación del salario mínimo, DOF 27-01-2016, transitorio tercero',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf',
         'sha256': 'cefb525ae8dfc97a7da40597d2ee918fe254d4bfce88301ff3c9959ced9e6e65'}

LFTSE = {'tx': 'Ley Federal de los Trabajadores al Servicio del Estado, reglamentaria del apartado B del art. 123 (Cámara de Diputados, última reforma DOF 15-01-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFTSE.pdf',
         'sha256': '2055ea67ac6fb6642ef90d1970e8ebf9870a0cb40c71930aa99d12dd446870fe'}
SCJN = {'tx': 'SCJN, Segunda Sala: jurisprudencia 2a./J. 34/2017 (10a.), transcrita en la Gaceta del Semanario Judicial de la Federación, octubre de 2022 (Sección Primera, Jurisprudencia)',
        'url': 'https://www.scjn.gob.mx/sites/default/files/gaceta/documentos/tomos/2022-11/4_18_OCT_0.pdf',
        'sha256': '1f324f188355a67193fd633f6c520a0682a11fb416dbcf79dda96a5a21dc10ff'}
SCJN_ISR = {'tx': 'SCJN, tesis 2a. XXVIII/2017 (10a.), transcrita en el amparo directo en revisión 503/2022 (lista de la SCJN, agosto de 2022)',
            'url': 'https://www.scjn.gob.mx/sites/default/files/listas/documento_dos/2022-08/ADR-503-2022-01082022.pdf',
            'sha256': '7812c2643cd867128ede17866fadba801f36224ccf85d36898a6a867bb813cd7'}
SUBSIDIO = {'tx': 'Decreto por el que se modifica el diverso que otorga el subsidio para el empleo (DOF 31-12-2025, texto del SIDOF)',
            'url': 'https://sidof.segob.gob.mx/notas/docFuente/5777649',
            'sha256': 'c2ff90539073ecf0eeefc72bb570950edae32021e1891cfc0c7532ef68d5717f'}

# Cuándo toca cada concepto, por causa (LFT). Lo leen la página y el navegador.
CAUSAS = [
    ('renuncia', 'Renuncié o terminamos de común acuerdo', 'LFT, art. 53, fr. I; prima de antigüedad solo con 15 años o más (art. 162, fr. III)'),
    ('justificado', 'Me despidieron con una causa del art. 47', 'LFT, art. 47; prima de antigüedad (art. 162, fr. III)'),
    ('injustificado', 'Me despidieron sin causa y pido la indemnización', 'LFT, art. 48: tres meses de salario y prima de antigüedad'),
    ('sin_reinstalar', 'El patrón no me reinstala, o yo rescindí por su culpa', 'LFT, arts. 49 a 52: tres meses, veinte días por año y prima de antigüedad'),
    ('vence', 'Se acabó el plazo de mi contrato (o, en una plataforma, pasé 30 días sin actividad)', 'LFT, art. 53, fr. III, y art. 291-C: termina sin indemnización'),
]
# Tipo de contrato (solo apartado A). La obra determinada no entra: el art. 50 no la nombra.
TIPOS = [
    ('ind', 'Por tiempo indeterminado (de planta)', 'LFT, art. 50, fr. II'),
    ('det', 'Por tiempo determinado (eventual)', 'LFT, arts. 37 y 50, fr. I'),
    ('plat', 'Trabajo en una plataforma digital (reparto, transporte)', 'LFT, arts. 291-A a 291-U y 50, fr. IV'),
]
EJEMPLO = {'ing': '2019-03-01', 'sal': '2026-11-15', 'sd': 600, 'zona': 'gen', 'agd': 15, 'pv': 25, 'vacPend': 0, 'vacTom': 0, 'dp': 15,
           'causa': 'injustificado', 'agPag': False}


def esc(t):
    return html.escape(str(t))


def datos(base):
    cc = base['calculadora_civica']
    p = cc['parametros']
    tm = cc['tarifa_mensual']
    se = p['subsidio_empleo']
    return {'uma': p['uma']['diaria'], 'umam': p['uma']['mensual'], 'sub': {'pct': se['pct_uma'], 'tope': se['tope_ingreso_mensual']},
            'sm': {'gen': p['salario_minimo']['general'], 'fro': p['salario_minimo']['frontera_norte']},
            'tarifa': [[r['li'], r['ls'], r['cf'], r['pct']] for r in tm['renglones']],
            'causas': [[c[0], c[1], c[2]] for c in CAUSAS], 'tipos': [list(t) for t in TIPOS],
            'f': {'uma': p['uma']['fuente'], 'sm': p['salario_minimo']['fuente'], 'tarifa': '%s (%s)' % (tm['ley'], tm['fuente']), 'sub': se['fuente']}}


# ---- La cuenta (gemela de calcula() en cc-laboral.js) ----

def _dia(s):
    return datetime.date(*[int(x) for x in s.split('-')])


def vac_tabla(n):
    """Días de vacaciones del año de servicios n (LFT, art. 76)."""
    if n <= 0:
        return 0
    if n <= 5:
        return 12 + 2 * (n - 1)
    return 20 + 2 * ((n - 6) // 5 + 1)


def isr_tarifa(D, m):
    if m <= 0:
        return 0.0
    fila = D['tarifa'][0]
    for f in D['tarifa']:
        if f[0] <= m:
            fila = f
    li, _ls, cf, pct = fila
    return cf + max(0.0, m - li) * pct / 100.0


def calcula(D, x):
    ing, sal = _dia(x['ing']), _dia(x['sal'])
    if sal < ing:
        return {'error': 'La fecha de salida no puede ser antes de la de ingreso.'}
    sd = float(x['sd'])
    dias = (sal - ing).days + 1
    anios = dias / 365.0
    comp = int(dias // 365)
    dcur = dias - comp * 365
    B = (x.get('reg') or 'A') == 'B'
    tipo = 'ind' if B else (x.get('tipo') or 'ind')
    P = tipo == 'plat'
    if P:
        # Plataformas: el salario es el promedio de lo ingresado en los últimos seis meses (art. 291-N).
        sd = float(x.get('p6') or 0) / 6.0 / 30.0
    agd, pv = float(x.get('agd') or (40 if B else 15)), float(x.get('pv') or (30 if B else 25))
    vac_anio = 20 if B else vac_tabla(comp + 1)
    sdi = sd * (1 + (agd + vac_anio * pv / 100.0) / 365.0)
    if P:
        sdi = sd  # el pago por tarea ya trae lo proporcional de aguinaldo, vacaciones y prima (art. 291-F)
    r = {'dias': dias, 'anios': anios, 'sdi': sdi, 'vac_anio': vac_anio, 'conc': [], 'reg': 'B' if B else 'A', 'tipo': tipo, 'espera': []}
    c = r['conc']
    # Finiquito: lo que se debe siempre.
    dp = 0.0 if P else float(x.get('dp') or 0)
    if dp > 0:
        c.append(['salario', 'Días de salario que no te han pagado (%g × salario diario)' % dp, dp * sd, 'LFTSE, arts. 32 y 43' if B else 'LFT, art. 88'])
    if not B and not P:
        vprop = max(0.0, vac_anio * dcur / 365.0 - float(x.get('vacTom') or 0))
        vdias = vprop + float(x.get('vacPend') or 0)
        vac = vdias * sd
        if vac > 0:
            c.append(['vacaciones', 'Vacaciones: %.2f días (proporcionales del año en curso y pendientes)' % vdias, vac, 'LFT, arts. 76 y 79'])
            c.append(['prima_vac', 'Prima vacacional (%g %% de tus vacaciones)' % pv, vac * pv / 100.0, 'LFT, art. 80'])
    if not x.get('agPag') and not P:
        ini = max(ing, datetime.date(sal.year, 1, 1))
        dag = (sal - ini).days + 1
        ag = agd * dag / 365.0 * sd
        c.append(['aguinaldo', 'Aguinaldo proporcional (%g días × %d días trabajados este año ÷ 365)' % (agd, dag), ag, 'LFTSE, art. 42 Bis' if B else 'LFT, art. 87'])
    # Lo que depende de la causa (solo apartado A: la LFTSE deja la indemnización al laudo, art. 43, fr. III y IV).
    causa = x['causa']
    tope = 2 * D['sm'][x.get('zona') or 'gen']
    piso = D['sm'][x.get('zona') or 'gen']
    if tipo != 'ind' and causa != 'vence' and (causa != 'renuncia' or anios >= 15):
        # El art. 162 la da a «los trabajadores de planta»; si alcanza a un eventual o a una plataforma, la ley no lo dice claro.
        r['espera'].append(['prima_ant', 'Prima de antigüedad', 'LFT, art. 162: la ley la da a los trabajadores de planta; si te toca con un contrato eventual o en una plataforma no lo dice con claridad, y no la sumamos'])
    if not B and tipo == 'ind' and (causa in ('justificado', 'injustificado', 'sin_reinstalar') or (causa == 'renuncia' and anios >= 15)):
        bpa = min(max(sdi, piso), tope)
        c.append(['prima_ant', 'Prima de antigüedad: 12 días × %.2f años × %s de salario (entre uno y dos salarios mínimos)' % (anios, _p(bpa)),
                  12 * anios * bpa, 'LFT, arts. 162, 485 y 486'])
    if P and causa in ('injustificado', 'sin_reinstalar'):
        c.append(['ind3', 'Indemnización: tres meses de salario (la mitad de lo que ingresaste en seis meses)', 90 * sd, 'LFT, arts. 50, fr. IV, y 291-N'])
        r['espera'].append(['ind20', 'Veinte días por año de servicios', 'LFT, art. 50, fr. IV: se cuentan con el tiempo efectivamente laborado (art. 291-D), y la ley no dice cómo volver horas de trabajo en años'])
        if float(x.get('mj') or 0) > 0:
            r['espera'].append(['vencidos', 'Salarios vencidos e intereses', 'LFT, arts. 48 y 50, fr. IV: la ley no dice cuál es el salario de un día en una plataforma'])
    if not B and not P and causa in ('injustificado', 'sin_reinstalar'):
        c.append(['ind3', 'Indemnización: tres meses (90 días) de salario integrado', 90 * sdi, 'LFT, arts. 48, 50 (fr. III) y 89'])
    if not B and tipo == 'ind' and causa == 'sin_reinstalar':
        c.append(['ind20', 'Veinte días de salario integrado por cada año de servicios (%.2f años)' % anios, 20 * anios * sdi, 'LFT, arts. 49 y 50, fr. II'])
    if tipo == 'det' and causa == 'sin_reinstalar':
        if anios < 1:
            c.append(['ind50i', 'Salarios de la mitad del tiempo que trabajaste (%d días ÷ 2, con salario integrado)' % dias, dias / 2.0 * sdi, 'LFT, arts. 49, 50 (fr. I) y 89'])
        else:
            c.append(['ind50i', 'Seis meses (180 días) por el primer año y veinte días por cada año siguiente (%.2f años), con salario integrado' % (anios - 1),
                      (180 + 20 * (anios - 1)) * sdi, 'LFT, arts. 49, 50 (fr. I) y 89'])
    tot = sum(k[2] for k in c)
    # ISR aproximado (LISR arts. 93, 95 y 96; RLISR art. 174) y subsidio para el empleo (decreto DOF 31-12-2025).
    U = D['uma']
    m = float(x.get('mens') or 0) or sd * 30
    r['isr_pend'] = P  # en una plataforma, los «años de servicio» de la exención no se pueden contar sin interpretar
    isr_m = isr_tarifa(D, m)
    tasa_m = isr_m / m if m else 0.0
    val = {k[0]: k[2] for k in c}
    sep = val.get('prima_ant', 0) + val.get('ind3', 0) + val.get('ind20', 0) + val.get('ind50i', 0)
    anios_isr = comp + (1 if anios - comp > 0.5 else 0)
    ex_sep = min(sep, 90 * U * anios_isr)
    g_sep = sep - ex_sep
    ret_sep = 0.0
    if g_sep > 0:
        ret_sep = isr_tarifa(D, g_sep) if g_sep < m else g_sep * tasa_m

    def art174(g):
        if g <= 0:
            return 0.0
        R = g / 365.0 * 30.4
        dif = isr_tarifa(D, m + R) - isr_m
        return g * (dif / R)
    ag = val.get('aguinaldo', 0)
    ex_ag = min(ag, 30 * U)
    pvv = val.get('prima_vac', 0)
    ex_pv = min(pvv, 15 * U)
    ret_ag, ret_pv = art174(ag - ex_ag), art174(pvv - ex_pv)
    ordi = val.get('salario', 0) + val.get('vacaciones', 0)
    ret_ord = isr_tarifa(D, ordi)
    sub = 0.0
    if m <= D['sub']['tope']:
        sub = min(D['umam'] * D['sub']['pct'] / 100.0, ret_ord + ret_ag + ret_pv)
    isr = ret_sep + ret_ag + ret_pv + ret_ord - sub
    if P:
        isr, ret_sep, ex_sep = 0.0, 0.0, 0.0
    r.update({'total': tot, 'exento': ex_sep + ex_ag + ex_pv, 'isr': isr, 'neto': tot - isr, 'm': m, 'tasa_m': tasa_m, 'sub': sub,
              'isr_det': [ret_ord, ret_ag, ret_pv, ret_sep], 'ex_det': [ex_ag, ex_pv, ex_sep], 'anios_isr': anios_isr})
    # Escenario de juicio, fuera del total. Apartado A: LFT, art. 48, párrafos segundo y tercero.
    # Apartado B: LFTSE, art. 43, fr. III y IV, sin tope (jurisprudencia 2a./J. 34/2017).
    mj = int(float(x.get('mj') or 0))
    r['juicio'] = []
    if B and mj > 0 and causa in ('injustificado', 'sin_reinstalar'):
        r['juicio'].append(['caidos', 'Salarios caídos: %d meses × 30 días × tu salario, sin tope (corren hasta que se cumpla el laudo)' % mj,
                            mj * 30 * sd, 'LFTSE, art. 43, fr. III y IV; SCJN, 2a./J. 34/2017'])
    if not B and not P and mj > 0 and causa in ('injustificado', 'sin_reinstalar'):
        r['juicio'].append(['vencidos', 'Salarios vencidos: %d meses × 30 días × salario integrado (hasta 12 meses)' % min(mj, 12),
                            min(mj, 12) * 30 * sdi, 'LFT, art. 48, segundo párrafo'])
        if mj > 12:
            r['juicio'].append(['intereses', 'Intereses: 2 %% mensual sobre quince meses de salario, por %d meses después del mes 12' % (mj - 12),
                                15 * 30 * sdi * 0.02 * (mj - 12), 'LFT, art. 48, tercer párrafo'])
    r['total_juicio'] = tot + sum(k[2] for k in r['juicio'])
    # ISR de los salarios vencidos o caídos: prestación por la terminación del vínculo (SCJN, 2a. XXVIII/2017), con la
    # mecánica del art. 95 (la misma de la separación) y sin exención (lectura nuestra: hay criterios encontrados).
    # Los intereses del art. 48 no se tasan aquí.
    v = sum(k[2] for k in r['juicio'] if k[0] in ('vencidos', 'caidos'))
    r['isr_juicio'] = (isr_tarifa(D, v) if v < m else v * tasa_m) if v > 0 else 0.0
    r['neto_juicio'] = r['total_juicio'] - isr - r['isr_juicio']
    # Reparto de utilidades (LFT, arts. 123, 124 y 127, fr. VIII): aparte, se paga en su fecha (art. 122).
    r['ptu'] = None
    pu, pdt, pst, pd = (float(x.get(k) or 0) for k in ('ptuU', 'ptuDT', 'ptuST', 'ptuD'))
    if tipo == 'det' and pd < 60:
        pu = 0  # los eventuales participan si trabajaron 60 días o más en el año (art. 127, fr. VII)
    if not B and not P and pu > 0 and pdt > 0 and pst > 0 and pd > 0:
        ps = float(x.get('ptuS') or 0) or sd * pd
        p_d, p_s = pu / 2.0 * pd / pdt, pu / 2.0 * ps / pst
        bruto = p_d + p_s
        tope_p = max(90 * sd, float(x.get('ptuP') or 0))
        ptu = min(bruto, tope_p)
        ex_p = min(ptu, 15 * U)
        ret_p = art174(ptu - ex_p)
        r['ptu'] = {'dias': p_d, 'sal': p_s, 'bruto': bruto, 'tope': tope_p, 'ptu': ptu, 'ex': ex_p, 'isr': ret_p, 'neto': ptu - ret_p}
    return r


def _p(v):
    return '$' + format(round(v, 2), ',.2f')


def construir(base, ref):
    D = datos(base)
    L = cc_inmueble.LISR
    hoy = datetime.date.today().isoformat()
    lft = lambda a: '<a href="%s">LFT, %s</a>' % (esc(LFT['url']), esc(a))
    lftse = lambda a: '<a href="%s">LFTSE, %s</a>' % (esc(LFTSE['url']), esc(a))
    lisr = lambda a: '<a href="%s">LISR, %s</a>' % (esc(L['url']), esc(a))
    tipos = ''.join('<option value="%s">%s</option>' % (k, esc(t)) for k, t, _r in TIPOS)
    causas = ''.join('<option value="%s"%s>%s</option>' % (k, ' selected' if k == 'renuncia' else '', esc(t)) for k, t, _r in CAUSAS)
    huella = lambda d: '<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(d['url']), esc(d['tx']), d['sha256'][:12])
    return '''<div class="ci" id="clRaiz">
  <section class="ci-arranque" aria-labelledby="clTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="clTit">Tu finiquito o tu liquidación: ¿cuánto te toca?</h2>
    <p class="ci-txt">Escribe cuándo entraste, cuándo sales, tu salario y por qué termina tu trabajo. La página saca, renglón por renglón y con su artículo, <b>lo que siempre te deben</b> (salario, vacaciones, prima vacacional y aguinaldo: el finiquito) y, según la causa, <b>la indemnización y la prima de antigüedad</b> (la liquidación), con la parte exenta de ISR y la retención aproximada.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que escribes no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="clForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Tu relación de trabajo</legend>
      <div class="ci-fila">
        <div><label class="ci-et" for="clIng">Fecha en que entraste</label><input class="ci-in" id="clIng" type="date" value="2022-01-10"></div>
        <div><label class="ci-et" for="clSal">Fecha en que sales</label><input class="ci-in" id="clSal" type="date" value="{hoy}"></div>
      </div>
      <label class="ci-et" for="clReg">Quién te paga</label>
      <select class="ci-in" id="clReg"><option value="A">Una empresa o una persona (apartado A: Ley Federal del Trabajo)</option><option value="B">El gobierno federal (apartado B: Ley Federal de los Trabajadores al Servicio del Estado)</option></select>
      <p class="ci-pista" id="clRegLey"></p>
      <div id="clTipoCaja">
      <label class="ci-et" for="clTipo">Tu contrato</label>
      <select class="ci-in" id="clTipo">{tipos}</select>
      <p class="ci-pista" id="clTipoLey"></p>
      </div>
      <div id="clSdCaja">
      <label class="ci-et" for="clSd">Tu salario (pesos, antes de descuentos)</label>
      <input class="ci-in" id="clSd" inputmode="decimal" autocomplete="off" placeholder="Ej.: 12,000">
      <label class="ci-et" for="clPer">Cada cuándo</label><select class="ci-in" id="clPer"><option value="mes">Al mes</option><option value="dia">Al día</option></select>
      </div>
      <div id="clP6Caja" hidden>
      <label class="ci-et" for="clP6">Lo que ingresaste en la plataforma en los últimos seis meses (pesos, sin propinas)</label>
      <input class="ci-in" id="clP6" inputmode="decimal" autocomplete="off" placeholder="Ej.: 60,000">
      </div>
      <label class="ci-et" for="clZona">Dónde trabajas</label><select class="ci-in" id="clZona"><option value="gen">Resto del país</option><option value="fro">Zona libre de la frontera norte</option></select>
      <label class="ci-et" for="clCausa">Por qué termina</label>
      <select class="ci-in" id="clCausa">{causas}</select>
      <p class="ci-pista" id="clCausaLey"></p>
    </fieldset>

    <fieldset class="ci-grupo" id="clPresta">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> Lo que ya te pagaron y tus prestaciones <small>(opcional)</small></legend>
      <label class="ci-et" for="clDp">Días trabajados que todavía no te pagan</label>
      <input class="ci-in" id="clDp" inputmode="decimal" autocomplete="off" placeholder="Ej.: 15">
      <div class="ci-fila">
        <div><label class="ci-et" for="clVt">Días de vacaciones que ya tomaste este año de servicio</label><input class="ci-in" id="clVt" inputmode="decimal" autocomplete="off" placeholder="0"></div>
        <div><label class="ci-et" for="clVp">Días de vacaciones de años anteriores que no tomaste</label><input class="ci-in" id="clVp" inputmode="decimal" autocomplete="off" placeholder="0"></div>
      </div>
      <div class="ci-fila">
        <div><label class="ci-et" for="clAg">Días de aguinaldo de tu contrato</label><input class="ci-in" id="clAg" inputmode="decimal" autocomplete="off" value="15"></div>
        <div><label class="ci-et" for="clPv">Prima vacacional (%)</label><input class="ci-in" id="clPv" inputmode="decimal" autocomplete="off" value="25"></div>
      </div>
      <label class="ci-check"><input type="checkbox" id="clAgPag"> Ya me pagaron el aguinaldo de este año</label>
    </fieldset>
    <fieldset class="ci-grupo" id="clExtras">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Si vas a juicio y tu reparto de utilidades <small>(opcional; el reparto, solo en el apartado A)</small></legend>
      <label class="ci-et" for="clMj">Si te despidieron sin causa y vas a juicio: ¿cuántos meses supones que dura? (escenario)</label>
      <input class="ci-in" id="clMj" inputmode="numeric" autocomplete="off" placeholder="Ej.: 18">
      <div id="clPtuCaja">
      <p class="ci-pista">Los datos del reparto vienen en el proyecto que la comisión mixta fija en un lugar visible de la empresa ({a125}).</p>
      <div class="ci-fila">
        <div><label class="ci-et" for="clPtuU">Utilidad que se reparte entre todos (pesos)</label><input class="ci-in" id="clPtuU" inputmode="decimal" autocomplete="off" placeholder="Ej.: 1,200,000"></div>
        <div><label class="ci-et" for="clPtuD">Días que trabajaste ese año</label><input class="ci-in" id="clPtuD" inputmode="decimal" autocomplete="off" placeholder="Ej.: 365"></div>
      </div>
      <div class="ci-fila">
        <div><label class="ci-et" for="clPtuDT">Días trabajados por todo el personal</label><input class="ci-in" id="clPtuDT" inputmode="decimal" autocomplete="off" placeholder="Ej.: 18,250"></div>
        <div><label class="ci-et" for="clPtuST">Salarios de todo el personal ese año (pesos)</label><input class="ci-in" id="clPtuST" inputmode="decimal" autocomplete="off" placeholder="Ej.: 9,500,000"></div>
      </div>
      <div class="ci-fila">
        <div><label class="ci-et" for="clPtuS">Tus salarios de ese año <small>(si lo dejas vacío: tu salario diario × tus días)</small></label><input class="ci-in" id="clPtuS" inputmode="decimal" autocomplete="off"></div>
        <div><label class="ci-et" for="clPtuP">Promedio de tu reparto en los últimos tres años <small>(opcional)</small></label><input class="ci-in" id="clPtuP" inputmode="decimal" autocomplete="off"></div>
      </div>
      </div>
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Saca la cuenta</button></p>
  </form>

  <section class="ci-res" id="clRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">4</span> Lo que te toca, renglón por renglón {chip_d}</h2>
    <div class="ci-total" id="clTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Cómo se llega a la cifra</caption>
      <thead><tr><th scope="col">Concepto</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="clPasos"></tbody></table></div>
    <div id="clExtra"></div>
    <p class="ci-nota" id="clNota"></p>
  </section>

  <aside class="ci-aviso" aria-labelledby="clLeeTit">
    <h2 class="ci-tit" id="clLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>El finiquito siempre se paga</b>, sin importar por qué termina el trabajo: los días que no te han pagado, tus <b>vacaciones</b> (las del año en curso en proporción y las que no tomaste: {a76}, {a79}) con su <b>prima vacacional</b> de al menos 25 % ({a80}) y la parte proporcional del <b>aguinaldo</b>, de al menos 15 días ({a87}).</li>
      <li><b>La prima de antigüedad</b> es de 12 días por año ({a162}): se paga a quien despiden, con causa o sin ella, y a quien se va por su voluntad con 15 años o más. Su salario no baja de un salario mínimo ni pasa de dos ({a486}).</li>
      <li><b>La indemnización</b> depende de la causa: si te despiden sin una causa probada, tres meses de salario ({a48}); si el patrón no te reinstala o tú terminas por su culpa, además veinte días por cada año ({a50}, {a51}). Se paga con el <b>salario integrado</b>: tu salario diario más la parte de aguinaldo y prima vacacional ({a89}).</li>
      <li><b>El ISR</b>: no pagas por lo de la separación hasta 90 UMA por año de servicio; por el aguinaldo, hasta 30, y por la prima vacacional, hasta 15 ({a93}). La ley todavía dice «salario mínimo», y desde 2016 esas referencias se leen como UMA ({cpeum}). Lo demás se retiene: lo de la separación con la tasa de tu último sueldo mensual ({a96}) y el aguinaldo y la prima con el art. 174 del Reglamento ({r174}). Si tu sueldo del mes no pasa de {sub_tope}, se resta el <b>subsidio para el empleo</b>: el {sub_pct} % de la UMA mensual, nunca sobre lo de la separación y sin entregarte lo que sobre ({sub}).</li>
      <li><b>Si vas a juicio</b> y el patrón no prueba la causa, además te toca lo que no ganaste: los <b>salarios vencidos</b> desde el despido, hasta doce meses, y si el juicio sigue, un <b>interés del 2 % mensual</b> sobre quince meses de salario ({a48b}). Si trabajas para el gobierno federal, los <b>salarios caídos no tienen tope</b>: corren hasta que se cumpla el laudo ({b43}; la Suprema Corte dijo que el tope de doce meses de la LFT no se les aplica: {j34}), y no hay interés del 2 %. Lo damos aparte, como escenario: depende de cuánto dure y de lo que resuelva el Tribunal. <b>Su ISR</b>: la Suprema Corte dijo que no son salario ordinario sino una prestación por la terminación del trabajo, que se grava cuando la cobras ({t28}); por eso los tasamos como lo de la separación ({a96}), sin exención, porque hay criterios encontrados sobre si les toca. El ISR de los intereses no lo calculamos.</li>
      <li><b>El reparto de utilidades</b> no es parte del finiquito: se paga dentro de los sesenta días siguientes a la fecha en que la empresa debe pagar su impuesto anual ({a122}), y por eso va aparte. La mitad se reparte por los días trabajados y la otra mitad por los salarios ({a123}); el salario es solo la cuota diaria ({a124}), y lo tuyo no pasa de tres meses de salario o del promedio de los últimos tres años, lo que te convenga más ({a127}). Exento de ISR hasta 15 UMA ({a93}). Directivos, administradores y gerentes generales no participan, y quien trabaja en el hogar tampoco.</li>
      <li><b>Si tu contrato es por tiempo determinado</b> (eventual), el finiquito es el mismo. Si el patrón no te reinstala o tú rescindes por su culpa, en lugar de los veinte días por año te toca la mitad de los salarios del tiempo que trabajaste, si fue menos de un año, o seis meses por el primer año y veinte días por cada uno de los siguientes ({a50i}); los tres meses van además ({a50iii}). Al vencer el plazo, el trabajo termina sin indemnización ({a53}), salvo que el trabajo siga: entonces el contrato se prorroga ({a39}). La <b>prima de antigüedad</b> la ley se la da a los trabajadores de planta ({a162}): con un contrato eventual no lo dice claro, así que la dejamos <b>en espera</b>, sin sumarla. Participas del reparto si trabajaste sesenta días o más en el año ({a127vii}).</li>
      <li><b>Si trabajas en una plataforma digital</b> (reparto, transporte), tu pago por tarea ya trae en proporción el aguinaldo, las vacaciones, la prima y el descanso ({a291f}): no hay finiquito que sumar. Si te despiden sin causa, te tocan tres meses de salario, y el salario es el promedio de lo que ingresaste en los últimos seis meses ({a291n}); los veinte días por año se cuentan con el tiempo efectivamente laborado ({a50iv}, {a291d}), y como la ley no dice cómo volver horas de trabajo en años, quedan <b>en espera</b>, igual que los salarios vencidos y el ISR. Si pasas treinta días sin actividad, la relación termina sin indemnización ({a291c}).</li>
      <li><b>Si trabajas para el gobierno federal</b> (apartado B), su ley da aguinaldo de 40 días por lo menos ({b42}), dos periodos de diez días de vacaciones con prima del 30 % ({b30}, {b40}) y deja la indemnización al laudo ({b43}); no trae prima de antigüedad. Por eso la cuenta saca el salario pendiente, el aguinaldo proporcional y, como escenario, los salarios caídos: lo demás lo fija el Tribunal Federal de Conciliación y Arbitraje.</li>
    </ol>
    <p><b>Lo que esta cuenta supone:</b> años de 365 días, la parte del último año en proporción, el mes de 30 días ({a89b}), y que el salario y las vacaciones se tasan como si fueran todo tu ingreso del mes, con el subsidio completo del mes; los salarios vencidos con el salario integrado y el interés simple, sumado al pagar; los caídos del apartado B con tu salario; su ISR sin exención; los «seis meses» del contrato eventual como 180 días y los años que siguen al primero en proporción; los «tres meses» de una plataforma como la mitad de lo que ingresaste en seis meses; la «parte proporcional» del aguinaldo del apartado B por días; y los tres meses del tope del reparto como 90 días de tu salario. Todo eso es nuestro (<span class="est-chip est-derivado">auditada</span>).</p>
    <p><b>Lo que no hace:</b> no es asesoría legal ni un convenio. Lo que vale es lo que firmen ante el Centro de Conciliación o resuelva el Tribunal. No calcula el ISR de los intereses del juicio ni la indemnización del apartado B, que fija el laudo. No suma lo que dejamos en espera: la prima de antigüedad de un contrato eventual o de una plataforma ({a162}) y, en una plataforma, los veinte días por año, los salarios vencidos y el ISR. No aplica a quien trabaja para un estado o un municipio (le rige la ley de su estado) ni a un contrato por obra determinada: el art. 50 no lo nombra ({a50i}). Si tienes dudas, la Procuraduría Federal de la Defensa del Trabajo asesora gratis.</p>
    <p class="ci-fuentes">Fuentes: {f_lft} · {f_lftse} · {f_j34} · {f_t28} · {f_sub} · {f_lisr} · {f_rlisr} · {f_cpeum} · UMA: {f_uma} · Salario mínimo: {f_sm} · Tarifa: {f_tarifa} {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-ticket-retienen.html">💼 Lo que te retienen y tu nómina completa</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="clDatos">{datos}</script>
</div>'''.format(
        hoy=hoy, causas=causas, tipos=tipos, a50iii=lft('art. 50, fr. III'), a53=lft('art. 53, fr. III'), a39=lft('arts. 37 y 39'),
        a127vii=lft('art. 127, fr. VII'), a291f=lft('art. 291-F'), a291n=lft('art. 291-N'), a291d=lft('art. 291-D'), a291c=lft('arts. 291-C y 49, fr. VI'), chip_d=chip('derivado'), chip_o=chip('oficial'),
        a76=lft('art. 76'), a79=lft('art. 79'), a80=lft('art. 80'), a87=lft('art. 87'), a162=lft('art. 162'), a486=lft('arts. 485 y 486'),
        a48=lft('art. 48'), a50=lft('arts. 49 y 50, fr. II y III'), a51=lft('arts. 51 y 52'), a89=lft('arts. 84 y 89'), a89b=lft('art. 89'),
        a125=lft('art. 125'), a48b=lft('art. 48, segundo y tercer párrafos'), a122=lft('art. 122'), a123=lft('art. 123'), a124=lft('art. 124'),
        a127=lft('art. 127, fr. I, VI y VIII'),
        j34='<a href="%s">jurisprudencia 2a./J. 34/2017</a>' % esc(SCJN['url']), t28='<a href="%s">tesis 2a. XXVIII/2017</a>' % esc(SCJN_ISR['url']),
        b42=lftse('art. 42 Bis'), b30=lftse('art. 30'), b40=lftse('art. 40'), b43=lftse('art. 43, fr. III y IV'),
        sub='<a href="%s">decreto del subsidio para el empleo, DOF 31-12-2025</a>' % esc(SUBSIDIO['url']),
        sub_tope=_p(D['sub']['tope']), sub_pct=('%g' % D['sub']['pct']), a50i=lft('art. 50, fr. I'), a50iv=lft('art. 50, fr. IV'),
        a93=lisr('art. 93, fr. XIII y XIV'), a96=lisr('arts. 95 y 96'),
        r174='<a href="%s">RLISR, art. 174</a>' % esc(RLISR['url']),
        cpeum='<a href="%s">CPEUM, decreto DOF 27-01-2016, transitorio tercero</a>' % esc(CPEUM['url']),
        f_lft=huella(LFT), f_lisr=huella(L), f_rlisr=huella(RLISR), f_cpeum=huella(CPEUM), f_lftse=huella(LFTSE), f_j34=huella(SCJN), f_t28=huella(SCJN_ISR), f_sub=huella(SUBSIDIO),
        f_uma=esc(D['f']['uma']), f_sm=esc(D['f']['sm']), f_tarifa=esc(D['f']['tarifa']),
        datos=cc_inmueble._json(D))


def prueba():
    """Python y el navegador dan lo mismo en casos fijos."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import auditorias
    D = datos(auditorias.db())
    casos = []
    for causa in ('renuncia', 'justificado', 'injustificado', 'sin_reinstalar'):
        for ing, sal, sd in (('2019-03-01', '2026-11-15', 600), ('2026-02-01', '2026-06-30', 280), ('2008-01-15', '2026-11-20', 2500),
                             ('2010-06-01', '2026-01-31', 15000 / 30.0)):
            casos.append(dict(EJEMPLO, ing=ing, sal=sal, sd=sd, causa=causa))
    casos.append(dict(EJEMPLO, agPag=True, vacPend=6, vacTom=3, zona='fro', agd=30, pv=50))
    # Juicio, reparto de utilidades, apartado B y subsidio.
    for mj in (6, 12, 18, 30):
        casos.append(dict(EJEMPLO, mj=mj, causa='sin_reinstalar' if mj > 12 else 'injustificado'))
    PTU = dict(ptuU=1200000, ptuD=365, ptuDT=18250, ptuST=9500000)
    casos += [dict(EJEMPLO, causa='renuncia', **PTU), dict(EJEMPLO, causa='renuncia', sd=2500, **PTU),
              dict(EJEMPLO, causa='renuncia', ptuS=150000, ptuP=40000, **PTU)]
    for causa in ('renuncia', 'injustificado'):
        casos.append(dict(EJEMPLO, reg='B', agd=40, pv=30, causa=causa, mj=18, **PTU))
    casos += [dict(EJEMPLO, reg='B', agd=40, causa='injustificado', mj=40, sd=9000 / 30.0, mens=9000),
              dict(EJEMPLO, causa='injustificado', mj=1, sd=200)]
    casos.append(dict(EJEMPLO, sd=250, dp=10, causa='renuncia'))
    # Contrato eventual (art. 50, fr. I) y plataformas (arts. 50, fr. IV, 291-F y 291-N).
    for causa in ('renuncia', 'justificado', 'injustificado', 'sin_reinstalar', 'vence'):
        casos.append(dict(EJEMPLO, tipo='det', causa=causa, mj=14, ptuD=50, **{k: v for k, v in PTU.items() if k != 'ptuD'}))
        casos.append(dict(EJEMPLO, tipo='det', causa=causa, ing='2026-05-01', **PTU))
        casos.append(dict(EJEMPLO, tipo='plat', causa=causa, p6=60000, mj=8, **PTU))
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'cc-laboral.js')
    prog = ("global.window={};global.document={getElementById:function(){return null}};require(%s);"
            "var D=%s;console.log(JSON.stringify(%s.map(function(x){var r=window.AuditorLaboral.calcula(D,x);"
            "return [r.total,r.isr,r.exento,r.sdi,r.conc.length,r.sub,r.total_juicio,r.ptu?r.ptu.ptu:0,r.ptu?r.ptu.isr:0,r.isr_juicio,r.neto_juicio,r.espera.length];})));" % (json.dumps(js), json.dumps(D), json.dumps(casos)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    nav = json.loads(r.stdout)
    mal = 0
    for x, n in zip(casos, nav):
        p = calcula(D, x)
        t = p['ptu'] or {}
        py = [p['total'], p['isr'], p['exento'], p['sdi'], len(p['conc']), p['sub'], p['total_juicio'], t.get('ptu', 0), t.get('isr', 0), p['isr_juicio'], p['neto_juicio'], len(p['espera'])]
        if any(abs(a - b) > 0.005 for a, b in zip(py, n)):
            mal += 1
            print('✗', x['causa'], x['ing'], x['sal'], 'Python', py, 'navegador', n)
    # Reglas a mano: la tabla de vacaciones del art. 76 y que la causa decide los conceptos.
    if [vac_tabla(n) for n in (1, 2, 5, 6, 10, 11, 16)] != [12, 14, 20, 22, 22, 24, 26]:
        mal += 1
        print('✗ la tabla de vacaciones del art. 76')
    kinds = lambda c: {k[0] for k in calcula(D, dict(EJEMPLO, causa=c))['conc']}
    if 'prima_ant' in kinds('renuncia') or 'ind3' in kinds('justificado') or 'ind20' in kinds('injustificado') or not {'prima_ant', 'ind3', 'ind20'} <= kinds('sin_reinstalar'):
        mal += 1
        print('✗ la causa no decide bien los conceptos')
    # El art. 48: doce meses de vencidos y, después, 2 % mensual sobre quince meses.
    j = calcula(D, dict(EJEMPLO, mj=18))
    sdi = j['sdi']
    if abs(j['total_juicio'] - j['total'] - (360 * sdi + 450 * sdi * 0.02 * 6)) > 0.01:
        mal += 1
        print('✗ los salarios vencidos y sus intereses del art. 48')
    # El apartado B no lleva prima de antigüedad ni indemnización; sus caídos no tienen tope ni interés; el subsidio no pasa del tope.
    b = calcula(D, dict(EJEMPLO, reg='B', agd=40, causa='injustificado'))
    b30 = calcula(D, dict(EJEMPLO, reg='B', agd=40, causa='injustificado', mj=30))
    if {k[0] for k in b['conc']} - {'salario', 'aguinaldo'} or b['juicio'] or b['ptu'] or \
            [k[0] for k in b30['juicio']] != ['caidos'] or abs(b30['juicio'][0][2] - 900 * EJEMPLO['sd']) > 0.01:
        mal += 1
        print('✗ el apartado B saca conceptos del apartado A')
    # Eventual: mitad del tiempo si es menos de un año; seis meses más veinte días por año siguiente; sin prima de antigüedad.
    d1 = calcula(D, dict(EJEMPLO, tipo='det', causa='sin_reinstalar', ing='2026-05-01'))
    d2 = calcula(D, dict(EJEMPLO, tipo='det', causa='sin_reinstalar'))
    v1 = {k[0]: k[2] for k in d1['conc']}
    v2 = {k[0]: k[2] for k in d2['conc']}
    if abs(v1['ind50i'] - d1['dias'] / 2 * d1['sdi']) > 0.01 or abs(v2['ind50i'] - (180 + 20 * (d2['anios'] - 1)) * d2['sdi']) > 0.01 or \
            'prima_ant' in v2 or 'ind20' in v2 or 'ind3' not in v2 or [k[0] for k in d2['espera']] != ['prima_ant'] or \
            {k[0] for k in calcula(D, dict(EJEMPLO, tipo='det', causa='vence'))['conc']} - {'salario', 'vacaciones', 'prima_vac', 'aguinaldo'}:
        mal += 1
        print('✗ el contrato eventual del art. 50, fr. I')
    pl = calcula(D, dict(EJEMPLO, tipo='plat', causa='injustificado', p6=60000, mj=6))
    if [k[0] for k in pl['conc']] != ['ind3'] or abs(pl['conc'][0][2] - 30000) > 0.01 or pl['isr'] != 0 or pl['juicio'] or \
            [k[0] for k in pl['espera']] != ['prima_ant', 'ind20', 'vencidos']:
        mal += 1
        print('✗ la plataforma digital del art. 50, fr. IV')
    if calcula(D, dict(EJEMPLO, sd=D['sub']['tope'] / 30 + 1))['sub'] != 0:
        mal += 1
        print('✗ el subsidio se aplica arriba del tope del decreto')
    if mal:
        print('Simulador laboral: %d diferencias' % mal)
        return 1
    print('Simulador laboral: %d casos iguales en Python y en el navegador; la tabla del art. 76, las cuatro causas, el art. 48, el apartado B (caídos sin tope), el tope del subsidio, el contrato eventual y las plataformas en orden' % len(casos))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
