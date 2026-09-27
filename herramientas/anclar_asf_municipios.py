"""Ancla los 83 municipios de la base a su auditoría de la ASF (CP 2024).

Antes, cada municipio traía un monto «observado por la ASF», un estatus y una
lista de «obras fiscalizadas» sin ninguna fuente, y los montos no coincidían
con los de la ASF (Tijuana: $285 mdp en la base, $0 por aclarar en la matriz).
Aquí se sustituyen por los de la auditoría integral de cada municipio en la
Matriz de Datos Básicos de la Cuenta Pública 2024 (tercera entrega),
ya extraída en investigaciones/datos-matriz-asf2024.json.

- observacionesASF = (recuperaciones + por aclarar) / 1000, en mdp: la misma
  definición de «observado» que usa la serie nacional de la plataforma.
- El estatus se reescribe con los datos de la matriz, y la lista de obras se
  vacía: no había documento que la sostuviera.
- La auditoría integral no es necesariamente la única que la ASF hizo al
  municipio; el texto lo dice.

Idempotente.   python3 herramientas/anclar_asf_municipios.py
"""
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js'
MATRIZ = RAIZ / 'investigaciones' / 'datos-matriz-asf2024.json'

ALIAS = {'Veracruz (Puerto)': 'Veracruz',
         'Juchitán de Zaragoza': 'Heroica Ciudad de Juchitán de Zaragoza',
         'Chilpancingo (Capital)': 'Chilpancingo de los Bravo'}
ESTADO = {'Coahuila': 'Coahuila de Zaragoza', 'Michoacán': 'Michoacán de Ocampo',
          'Veracruz': 'Veracruz de Ignacio de la Llave'}
ENTREGA = {1: 'primera', 2: 'segunda', 3: 'tercera'}


def norm(x):
    x = unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z ]', ' ', x)).strip()


def mdp(miles):
    return round(float(miles) / 1000, 1)


def pesos(v):
    return '${:,.1f} mdp'.format(v)


def valor(v, sangria):
    if isinstance(v, list):
        if not v:
            return '[]'
        pad = ' ' * (sangria + 2)
        return '[\r\n' + ',\r\n'.join(pad + json.dumps(x, ensure_ascii=False) for x in v) + '\r\n' + ' ' * sangria + ']'
    return json.dumps(v, ensure_ascii=False)


def cuerpo(obj, sangria):
    pad = ' ' * sangria
    return (' ' * (sangria - 2) + '{\r\n' +
            ',\r\n'.join(pad + '"%s": %s' % (k, valor(v, sangria)) for k, v in obj.items()) +
            '\r\n' + ' ' * (sangria - 2) + '}')


def main():
    auditorias = json.loads(MATRIZ.read_text(encoding='utf-8'))['auditorias_integrales_municipales']
    indice = {}
    for a in auditorias:
        indice.setdefault(norm(a['institucion']), []).append(a)

    b = BASE.read_bytes().decode('utf-8')
    cambios = 0
    pos = 0
    while True:
        i = b.find('"municipios": [', pos)
        if i < 0:
            break
        # nombre del estado: el "name" más cercano hacia atrás
        estado = re.findall(r'"name": "([^"]+)"', b[:i])[-1]
        fin_lista = b.index('\r\n      ]', i)
        j = i
        while True:
            k = b.find('\r\n        {', j, fin_lista)
            if k < 0:
                break
            a0 = k + 2
            z = b.index('\r\n        }', a0) + len('\r\n        }')
            obj = json.loads(b[a0:z])
            mun = obj['nombre']
            base = ALIAS.get(mun, re.sub(r'\(.*?\)', '', mun).strip())
            pref = 'Alcaldía ' if estado == 'Ciudad de México' else 'Municipio de '
            c = indice.get(norm(pref + base + ', ' + ESTADO.get(estado, estado)), [])
            if len(c) != 1:
                sys.exit('Sin auditoría única para %s, %s (%d); no toco nada.' % (mun, estado, len(c)))
            a = c[0]
            por_aclarar, recup = mdp(a['por_aclarar_miles']), mdp(a['recuperaciones_miles'])
            obs = round(por_aclarar + recup, 1)
            r, ac = a['resultados_con_observaciones'], a['acciones_total']
            estatus = ('Auditoría integral n.º %d de la ASF a la Cuenta Pública 2024 (%s entrega): '
                       '%d %s con observación y %d %s; %s por aclarar'
                       % (a['auditoria_numero'], ENTREGA.get(a['entrega'], ''),
                          r, 'resultado' if r == 1 else 'resultados',
                          ac, 'acción promovida' if ac == 1 else 'acciones promovidas', pesos(por_aclarar)))
            estatus += (' y %s recuperados.' % pesos(recup)) if recup else '.'
            if obs == 0:
                estatus += ' Sin monto pendiente de aclarar al corte del informe.'
            nuevo = dict(obj)
            nuevo['observacionesASF'] = obs
            nuevo['estatusAuditoria'] = estatus
            nuevo['proyectosAuditados'] = []
            nuevo['asfAuditoria'] = a['auditoria_numero']
            nuevo['asfFuente'] = ('ASF, Matriz de Datos Básicos de la Cuenta Pública 2024, informe consolidado, '
                                  'pp. %s. La auditoría integral puede no ser la única que la ASF practicó al municipio.'
                                  % '-'.join(str(p) for p in a.get('paginas', [])))
            nuevo['asfEstado'] = 'oficial'
            if nuevo != obj:
                texto = cuerpo(nuevo, 10)
                b = b[:k + 2] + texto + b[z:]
                fin_lista = b.index('\r\n      ]', i)
                z = k + 2 + len(texto)
                cambios += 1
            j = z
        pos = fin_lista
    BASE.write_bytes(b.encode('utf-8'))
    print('municipios anclados a la ASF: %d' % cambios)


if __name__ == '__main__':
    main()
