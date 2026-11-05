"""El IMSS y el ISSSTE en cada entidad (pedido del autor, 03-11-2026: «que
también se integre una dimensión más, que sería de salud pública… sería IMSS
e ISSSTE»).

Dos documentos que cada institución publica para todos, sin solicitud de
acceso (AGENTS.md, §0 ter):

1. IMSS, Memoria Estadística 2025, los mismos archivos de Excel que ya coteja
   gestion_salud.py (su huella SHA-256 tiene que ser la de MEM, o se detiene).
   Cuadros por OOAD (Órgano de Operación Administrativa Desconcentrada, la
   antigua delegación; hay 35 porque la Ciudad de México, el Estado de México
   y Veracruz tienen dos cada uno):
     II.10   población derechohabiente adscrita a unidad de medicina familiar
     IV.3    consultas de 2025: total, de especialidad y de urgencias
     IV.5    hospitalización de 2025: egresos e intervenciones quirúrgicas
     XIII.11 camas en servicio (suma y censables), consultorios y quirófanos
   La Memoria avisa que las Unidades Médicas de Alta Especialidad se cuentan
   en la OOAD donde están: ahí se atiende también a gente de otros estados.

2. Secretaría de Salud, DGIS, «Recursos en Salud Sectorial» 2025 (datos
   abiertos, un renglón por establecimiento con su CLUES). Es el único
   registro que pone al IMSS y al ISSSTE con la misma regla, por entidad:
   establecimientos, camas del área de hospitalización, médicos (generales,
   especialistas y odontólogos), personal de enfermería en contacto con el
   paciente y consultorios. Su nota de cierre dice cuántos establecimientos
   reportó cada institución (5,734 el IMSS, 1,135 el ISSSTE): si el archivo
   no los trae, se detiene. Desde 2025 el IMSS de la DGIS incluye las
   unidades del antiguo programa IMSS-Bienestar (IMSS-Coplamar), por eso no
   se mezcla con la Memoria.

Lo que el ISSSTE no deja cotejar: cuántos derechohabientes tiene en cada
estado y cuántas consultas, egresos y cirugías dio. Su anuario estadístico
(issste.gob.mx/datosabiertos/anuarios) no respondió el 27-10-2026 ni el
03-11-2026; queda en la ficha «salud-issste-servicios».

Escribe docs/salud/imss-issste-estados-2025.json, con la huella de cada
archivo y los totales nacionales de cada cuadro. Idempotente.

    python3 herramientas/anclar_salud_estados.py <carpeta con los Excel de la Memoria> Recursos_Salud_Sectorial_2025.zip
"""
import csv
import hashlib
import io
import json
import os
import sys
import unicodedata
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gestion_salud as gs  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'salud', 'imss-issste-estados-2025.json')

# Las 32 entidades en el orden de la clave del INEGI (la de la DGIS).
ENT = ['AGS', 'BC', 'BCS', 'CAM', 'COAH', 'COL', 'CHIS', 'CHIH', 'CDMX', 'DGO', 'GTO', 'GRO', 'HGO', 'JAL', 'MÉX', 'MICH',
       'MOR', 'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER', 'YUC', 'ZAC']
# La OOAD de la Memoria, por su nombre sin acentos ni espacios dobles.
OOAD = {'aguascalientes': 'AGS', 'baja california': 'BC', 'baja california sur': 'BCS', 'campeche': 'CAM', 'coahuila': 'COAH',
        'colima': 'COL', 'chiapas': 'CHIS', 'chihuahua': 'CHIH', 'cdmx norte': 'CDMX', 'cdmx sur': 'CDMX', 'durango': 'DGO',
        'guanajuato': 'GTO', 'guerrero': 'GRO', 'hidalgo': 'HGO', 'jalisco': 'JAL', 'mexico oriente': 'MÉX', 'mexico poniente': 'MÉX',
        'michoacan': 'MICH', 'morelos': 'MOR', 'nayarit': 'NAY', 'nuevo leon': 'NL', 'oaxaca': 'OAX', 'puebla': 'PUE',
        'queretaro': 'QRO', 'quintana roo': 'QROO', 'san luis potosi': 'SLP', 'sinaloa': 'SIN', 'sonora': 'SON', 'tabasco': 'TAB',
        'tamaulipas': 'TAM', 'tlaxcala': 'TLAX', 'veracruz norte': 'VER', 'veracruz sur': 'VER', 'yucatan': 'YUC', 'zacatecas': 'ZAC'}

# Cómo se escribe cada OOAD de las entidades que tienen dos.
NOMBRE = {'cdmx norte': 'CDMX Norte', 'cdmx sur': 'CDMX Sur', 'mexico oriente': 'México Oriente', 'mexico poniente': 'México Poniente',
          'veracruz norte': 'Veracruz Norte', 'veracruz sur': 'Veracruz Sur'}

DGIS = {'tx': 'Secretaría de Salud, Dirección General de Información en Salud, Recursos en Salud Sectorial 2025 (datos abiertos)',
        'url': 'http://www.dgis.salud.gob.mx/descargas/datosabiertos/recursosSalud/Recursos_Salud_Sectorial_2025.zip',
        'pagina': 'http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_recursos_gobmx.html'}
# La nota de cierre que viene en el mismo ZIP («Notas cierre sectorial 2025.pdf», cuadro de la nota 1).
INST = {'imss': ('INSTITUTO MEXICANO DEL SEGURO SOCIAL', 5734), 'issste': ('INSTITUTO DE SEGURIDAD Y SERVICIOS SOCIALES DE LOS TRABAJADORES DEL ESTADO', 1135)}
# Y su nota 2: establecimientos que no reportaron personal.
SIN_PERSONAL = {'imss': 276, 'issste': 88}
COL_DGIS = {'u': None, 'cam': 'TOTAL CAMAS AREA HOSPITALIZACIÓN', 'med': 'Total médicos generales especialistas y odonólogos',
            'enf': 'Total enfermeras en contacto con el paciente', 'cons': 'TOTAL DE CONSULTORIOS'}


def plano(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    return ' '.join(s.split())


def sha(ruta):
    return hashlib.sha256(open(ruta, 'rb').read()).hexdigest()


def hoja(ruta, nombre):
    import openpyxl
    return list(openpyxl.load_workbook(ruta, read_only=True, data_only=True)[nombre].iter_rows(values_only=True))


def ooad(filas, desde, hasta, cols, total_fila):
    """{OOAD: [valores]} de un cuadro, y el total nacional del propio cuadro.
    Se detiene si las 35 OOAD no suman ese total."""
    out = {}
    for r in filas[desde:hasta]:
        if r[0] is None or not str(r[0]).strip():
            continue
        k = plano(r[0])
        if k not in OOAD:
            raise SystemExit('anclar_salud_estados: OOAD desconocida %r' % r[0])
        out[k] = [int(r[c]) for c in cols]
    if len(out) != 35:
        raise SystemExit('anclar_salud_estados: se esperaban 35 OOAD y hay %d' % len(out))
    tot = [int(filas[total_fila][c]) for c in cols]
    for i, c in enumerate(cols):
        if sum(v[i] for v in out.values()) != tot[i]:
            raise SystemExit('anclar_salud_estados: las OOAD no suman el total del cuadro (columna %d)' % c)
    return out, tot


def memoria(carpeta):
    arch = {}
    for cap, nombre in (('II', '02-PoblacionDerechohabiente.xlsx'), ('IV', '04-PrestacionesMedicas.xlsx'),
                        ('XIII', '13-RecursosHumanosMaterialesFinancieros.xlsx')):
        ruta = os.path.join(carpeta, nombre)
        if sha(ruta) != gs.MEM[cap]['sha256']:
            raise SystemExit('anclar_salud_estados: %s no es el archivo que coteja gestion_salud.py (huella distinta)' % nombre)
        arch[cap] = ruta
    # II.10: la columna 1 es la población adscrita; la fila 8, el total nacional.
    f = hoja(arch['II'], 'II.10')
    if 'adscrita' not in plano(f[2][0]) or '2025' not in str(f[2][0]):
        raise SystemExit('anclar_salud_estados: II.10 cambió de título')
    ads, t_ads = ooad(f, 9, 44, [1], 7)
    # IV.3: cinco bloques de 21 años (2005-2025); 2025 es la última columna de cada uno.
    f = hoja(arch['IV'], 'IV.3.')
    # El cuadro escribe sus encabezados con letras separadas («E s p e c i a l i d a d»).
    if [f[5][c] for c in (21, 43, 65, 87)] != [2025] * 4 or 'especialidad' not in plano(f[4][45]).replace(' ', '') or 'urgencias' not in plano(f[4][67]).replace(' ', ''):
        raise SystemExit('anclar_salud_estados: IV.3 cambió de forma')
    con, t_con = ooad(f, 9, 44, [21, 65, 87], 7)
    # IV.5: los bloques «Egresos» (67) e «Intervenciones Quirúrgicas» (89).
    f = hoja(arch['IV'], 'IV.5')
    if [f[5][c] for c in (87, 109)] != [2025] * 2 or 'egresos' not in plano(f[3][67]) or 'quirurgicas' not in plano(f[3][89]):
        raise SystemExit('anclar_salud_estados: IV.5 cambió de forma')
    hos, t_hos = ooad(f, 9, 44, [87, 109], 7)
    # XIII.11: camas (suma y censables), consultorios y quirófanos.
    f = hoja(arch['XIII'], 'XIII.11')
    if 'camas' not in plano(f[3][1]) or 'consultorios' not in plano(f[3][6]) or 'quirofanos' not in plano(f[3][8]):
        raise SystemExit('anclar_salud_estados: XIII.11 cambió de forma')
    rec, t_rec = ooad(f, 10, 45, [1, 2, 6, 8], 8)
    # Los totales tienen que ser los que ya publica la plataforma (gestion_salud.py).
    srv = {s[0]: s[3] for s in gs.SERV}
    rc = {r[0]: r[2] for r in gs.REC}
    if (t_ads[0] != gs.ADSCRITA[1] or t_con[0] != srv['Consultas, en total'] or t_con[1] != srv['· de especialidad']
            or t_con[2] != srv['· de urgencias'] or t_hos[0] != srv['Egresos hospitalarios'] or t_hos[1] != srv['Intervenciones quirúrgicas']
            or t_rec[0] != rc['Camas en servicio'] or t_rec[1] != rc['· censables (de hospitalización)'] or t_rec[2] != rc['Consultorios']
            or t_rec[3] != rc['Quirófanos']):
        raise SystemExit('anclar_salud_estados: los totales de los cuadros por OOAD no son los nacionales de gestion_salud.py')
    campos = ['ads', 'con', 'esp', 'urg', 'egr', 'iq', 'cam', 'camc', 'cons', 'quir']
    por = {k: ads[k] + con[k] + hos[k] + rec[k] for k in ads}
    return campos, por, dict(zip(campos, t_ads + t_con + t_hos + t_rec))


def dgis(zip_ruta):
    z = zipfile.ZipFile(zip_ruta)
    nom = [n for n in z.namelist() if n.lower().endswith('.csv')]
    if len(nom) != 1:
        raise SystemExit('anclar_salud_estados: el ZIP de la DGIS debe traer un solo CSV')
    r = csv.reader(io.TextIOWrapper(z.open(nom[0]), encoding='latin-1'))
    h = next(r)
    ix = {k: (h.index(v) if v else None) for k, v in COL_DGIS.items()}
    i_inst, i_ent, i_anio = h.index('Institución'), h.index('Clave Estado'), h.index('AÑO')
    out = {k: {a: dict.fromkeys(COL_DGIS, 0) for a in ENT} for k in INST}
    for x in r:
        if not any(c.strip() for c in x):
            continue          # el archivo trae renglones vacíos al final
        if x[i_anio] != '2025':
            raise SystemExit('anclar_salud_estados: un renglón de la DGIS no es de 2025')
        for k, (inst, _) in INST.items():
            if x[i_inst].strip() == inst:
                a = ENT[int(x[i_ent]) - 1]
                out[k][a]['u'] += 1
                for c, i in ix.items():
                    if i is not None:
                        v = x[i].strip().replace(',', '')
                        out[k][a][c] += int(float(v)) if v else 0
    for k, (_, n) in INST.items():
        if sum(v['u'] for v in out[k].values()) != n:
            raise SystemExit('anclar_salud_estados: la DGIS no trae los %d establecimientos de su nota de cierre (%s)' % (n, k))
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    campos, por, tot = memoria(sys.argv[1])
    ent = {a: dict.fromkeys(campos, 0) for a in ENT}
    det = {}
    for k, v in por.items():
        a = OOAD[k]
        for c, x in zip(campos, v):
            ent[a][c] += x
        det.setdefault(a, []).append(k)
    dg = dgis(sys.argv[2])
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    doc = {
        'nota': 'Lo escribe herramientas/anclar_salud_estados.py; no se edita a mano.',
        'memoria': {'tx': 'IMSS, Memoria Estadística 2025', 'url': gs.MEMORIA,
                    'cuadros': {'ads': 'II.10', 'con': 'IV.3', 'esp': 'IV.3', 'urg': 'IV.3', 'egr': 'IV.5', 'iq': 'IV.5',
                                'cam': 'XIII.11', 'camc': 'XIII.11', 'cons': 'XIII.11', 'quir': 'XIII.11'},
                    'archivos': {c: {'url': gs.MEM[c]['url'], 'sha256': gs.MEM[c]['sha256']} for c in ('II', 'IV', 'XIII')},
                    'campos': campos, 'total': tot,
                    'ooad': {a: [NOMBRE[k] for k in ks] for a, ks in det.items() if len(ks) > 1},
                    'porOoad': {NOMBRE[k]: dict(zip(campos, v)) for k, v in por.items() if len(det[OOAD[k]]) > 1},
                    'ent': ent},
        'dgis': dict(DGIS, sha256=sha(sys.argv[2]), establecimientos={k: n for k, (_, n) in INST.items()}, sinPersonal=SIN_PERSONAL,
                     campos=list(COL_DGIS), columnas=COL_DGIS, ent=dg),
    }
    with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    print('anclar_salud_estados: %s (IMSS %d OOAD en 32 entidades; DGIS IMSS %d y ISSSTE %d establecimientos)' % (
        os.path.relpath(SALIDA, RAIZ), len(por), INST['imss'][1], INST['issste'][1]))


if __name__ == '__main__':
    main()
