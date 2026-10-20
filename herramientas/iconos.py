#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma assets/auditor/js/iconos.js: los emojis de la plataforma se ven como
íconos de trazo (decisión del autor, 20-10-2026).

Los textos siguen escritos con emojis (en las páginas, el motor y la base),
porque son cortos y se leen bien al editar. Al pintar la página, iconos.js
cambia cada emoji de la tabla por su ícono SVG de trazo, de un solo color, que
toma el color del texto y funciona en tema claro y oscuro. Los íconos son de
Lucide (licencia ISC, https://lucide.dev); su trazo va dentro del archivo, sin
pedir nada a otro servidor.

Cada renglón de ICONOS dice: emoji, ícono de Lucide, nombre en español (lo
lee el lector de pantalla cuando el emoji es todo el contenido de un botón o
un enlace) y, si el color es parte del significado (semáforos, alertas), su
clase de color. Un emoji nuevo que no esté en la tabla se queda como emoji:
agrégalo aquí y vuelve a correr el script.

Uso:
    npm pack lucide-static@1.49.0 && tar xzf lucide-static-1.49.0.tgz
    python3 herramientas/iconos.py package/icons
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'iconos.js')
VERSION_LUCIDE = '1.49.0'

# emoji, icono, nombre, color ('' = el del texto; 'r' = relleno de color)
ICONOS = [
    ('🏛️', 'landmark', 'institución'), ('🔒', 'lock', 'candado'), ('📢', 'megaphone', 'aviso'),
    ('⚖️', 'scale', 'balanza'), ('🏗️', 'construction', 'obra'), ('🔗', 'link', 'enlace'),
    ('🔍', 'search', 'buscar'), ('🔎', 'search', 'buscar'), ('💰', 'piggy-bank', 'dinero'),
    ('⚠️', 'triangle-alert', 'atención', 'ambar'), ('🗂️', 'folders', 'archivo'), ('💡', 'lightbulb', 'idea'),
    ('✏️', 'pencil', 'editar'), ('🧾', 'receipt', 'recibo'), ('🪐', 'orbit', 'órbita'),
    ('📜', 'scroll-text', 'documento'), ('🟢', 'circle', 'verde', 'verde r'), ('📊', 'chart-column', 'gráfica'),
    ('⏱️', 'timer', 'cronómetro'), ('🧭', 'compass', 'brújula'), ('📖', 'book-open', 'nota'),
    ('🏭', 'factory', 'industria'), ('🗺️', 'map', 'mapa'), ('📉', 'trending-down', 'baja'),
    ('🧮', 'calculator', 'cálculo'), ('🏢', 'building-2', 'edificio'), ('🏦', 'landmark', 'banco'),
    ('⚪', 'circle', 'sin dato', 'gris'), ('⚡', 'zap', 'rápido'), ('📈', 'trending-up', 'sube'),
    ('📚', 'library', 'biblioteca'), ('📄', 'file-text', 'documento'), ('🟡', 'circle', 'amarillo', 'ambar r'),
    ('📑', 'files', 'documentos'), ('🛡️', 'shield', 'protección'), ('📋', 'clipboard-list', 'lista'),
    ('🗳️', 'vote', 'voto'), ('🌎', 'earth', 'mundo'), ('⏳', 'hourglass', 'en espera'),
    ('🔴', 'circle', 'rojo', 'rojo r'), ('🛢️', 'barrel', 'petróleo'), ('💸', 'banknote-arrow-down', 'gasto'),
    ('📂', 'folder-open', 'carpeta'), ('🚆', 'train-front', 'tren'), ('🏥', 'hospital', 'hospital'),
    ('⛽', 'fuel', 'combustible'), ('🗑️', 'trash-2', 'borrar'), ('📏', 'ruler', 'medida'),
    ('🎯', 'target', 'objetivo'), ('🏘️', 'house', 'municipio'), ('🌐', 'globe', 'en línea'),
    ('💵', 'banknote', 'billete'), ('💊', 'pill', 'medicina'), ('📒', 'notebook-text', 'libreta'),
    ('🧱', 'brick-wall', 'muro'), ('📍', 'map-pin', 'ubicación'), ('✅', 'circle-check', 'listo', 'verde'),
    ('📅', 'calendar', 'fecha'), ('📡', 'radar', 'radar'), ('🤝', 'handshake', 'acuerdo'),
    ('⬇️', 'arrow-down', 'abajo'), ('🛫', 'plane-takeoff', 'aeropuerto'), ('🪙', 'coins', 'moneda'),
    ('🗓️', 'calendar-days', 'calendario'), ('👷', 'hard-hat', 'trabajador'), ('🧪', 'flask-conical', 'prueba'),
    ('🛟', 'life-buoy', 'salvavidas'), ('🫂', 'users-round', 'social'), ('🛣️', 'route', 'carretera'),
    ('📝', 'notebook-pen', 'nota'), ('🧰', 'toolbox', 'herramientas'), ('👑', 'crown', 'primer lugar'),
    ('💬', 'message-circle', 'comentario'), ('🚩', 'flag', 'alerta'), ('💳', 'credit-card', 'tarjeta'),
    ('⚔️', 'swords', 'duelo'), ('🔦', 'flashlight', 'punto ciego'), ('🖼️', 'image', 'imagen'),
    ('🌀', 'tornado', 'huracán'), ('🔄', 'refresh-cw', 'actualizar'), ('🎛️', 'sliders-horizontal', 'ajustes'),
    ('🌡️', 'thermometer', 'temperatura'), ('👥', 'users', 'personas'), ('🚈', 'tram-front', 'tren ligero'),
    ('🗼', 'tower-control', 'torre'), ('⚙️', 'settings', 'ajustes'), ('📣', 'megaphone', 'aviso'),
    ('💱', 'currency', 'tipo de cambio'), ('🖥️', 'monitor', 'computadora'), ('📰', 'newspaper', 'nota de prensa'),
    ('🔏', 'file-lock', 'documento reservado'), ('🚅', 'train-front', 'tren rápido'), ('📘', 'book', 'libro'),
    ('🧩', 'puzzle', 'pieza'), ('❓', 'circle-help', 'pregunta'), ('✈️', 'plane', 'avión'),
    ('🕰️', 'history', 'historia'), ('👁️', 'eye', 'ver'), ('🚪', 'door-open', 'puerta'),
    ('🇲🇽', 'flag', 'México'), ('💧', 'droplet', 'agua'), ('💼', 'briefcase', 'trabajo'),
    ('🌱', 'sprout', 'medio ambiente'), ('🚄', 'train-front', 'tren rápido'), ('🙋', 'hand', 'participa'),
    ('🦅', 'bird', 'Ejecutivo'), ('🟠', 'circle', 'naranja', 'naranja r'), ('⭐', 'star', 'destacado'),
    ('🍺', 'beer', 'pase'), ('💾', 'save', 'guardar'), ('📆', 'calendar-days', 'calendario'),
    ('🌳', 'tree-deciduous', 'árbol'), ('🏙️', 'building', 'ciudad'), ('📁', 'folder', 'carpeta'),
    ('🛒', 'shopping-cart', 'compras'), ('🕐', 'clock', 'hora'), ('🏠', 'house', 'casa'),
    ('🧑‍💼', 'user', 'servidor público'), ('🩺', 'stethoscope', 'salud'), ('🐷', 'piggy-bank', 'donar'),
    ('🎓', 'graduation-cap', 'educación'), ('🔁', 'repeat', 'repetir'), ('🎭', 'drama', 'cultura'),
    ('🌫️', 'cloud-fog', 'contaminación'), ('🌿', 'leaf', 'naturaleza'), ('⏸', 'pause', 'pausa'), ('📦', 'package', 'paquete'), ('⬆️', 'arrow-up', 'arriba'),
    ('🚱', 'droplet-off', 'sin agua'), ('🚧', 'construction', 'en obra'), ('📌', 'pin', 'fijado'),
    ('⏭', 'skip-forward', 'siguiente'), ('📥', 'download', 'descargar'),
    ('🤔', 'circle-help', 'duda'), ('⏰', 'alarm-clock', 'alarma'), ('🚢', 'ship', 'barco'),
    ('🌾', 'wheat', 'campo'), ('⚓', 'anchor', 'puerto'), ('🔓', 'lock-open', 'abierto'),
    ('⛔', 'octagon-x', 'prohibido', 'rojo'), ('🏷️', 'tag', 'etiqueta'), ('🪖', 'shield', 'fuerzas armadas'),
    ('💻', 'laptop', 'computadora'), ('🗣️', 'speech', 'voz'), ('✉️', 'mail', 'correo'),
    ('🏆', 'trophy', 'trofeo'), ('🚗', 'car', 'auto'), ('❌', 'circle-x', 'no', 'rojo'),
    ('👔', 'shirt', 'funcionario'), ('💥', 'bomb', 'impacto'), ('🌽', 'wheat', 'maíz'),
    ('🏖️', 'umbrella', 'vacaciones'), ('🚓', 'siren', 'policía'), ('🔬', 'microscope', 'análisis'),
    ('🔌', 'plug', 'electricidad'), ('🚫', 'ban', 'no permitido', 'rojo'), ('🎲', 'dices', 'al azar'),
    ('🔥', 'flame', 'fuego'), ('🚛', 'truck', 'camión'), ('⏯', 'circle-pause', 'pausa o seguir'),
    ('🛤️', 'train-track', 'vía'), ('🐒', 'hand-coins', 'reparto'),
    ('🧑‍🔧', 'wrench', 'técnico'), ('🖨️', 'printer', 'imprimir'), ('🕳️', 'circle-dashed', 'hueco'),
    ('🕊️', 'feather', 'paz'), ('♀️', 'venus', 'mujeres'), ('👍', 'thumbs-up', 'de acuerdo'),
    ('ℹ️', 'info', 'información'), ('🔻', 'triangle', 'baja', 'rojo r rot'), ('🔧', 'wrench', 'arreglo'),
    ('👆', 'pointer', 'toca'), ('🛠️', 'hammer', 'herramientas'), ('🚨', 'siren', 'alarma', 'rojo'),
    ('➡️', 'arrow-right', 'sigue'), ('📨', 'mail', 'correo'), ('🏫', 'school', 'escuela'),
    ('🌊', 'waves', 'agua'), ('📎', 'paperclip', 'anexo'), ('🌞', 'sun', 'sol'),
    ('👵', 'user-round', 'persona mayor'), ('🥇', 'medal', 'primer lugar', 'oro'), ('📗', 'book', 'libro'),
    ('💶', 'euro', 'euro'), ('🔮', 'telescope', 'proyección'), ('🥊', 'swords', 'cara a cara'),
    ('❔', 'circle-help', 'pregunta'), ('🐖', 'piggy-bank', 'alcancía'), ('🔢', 'hash', 'números'),
    ('📱', 'smartphone', 'celular'), ('☂️', 'umbrella', 'protección'), ('⭕', 'circle', 'círculo', 'rojo'),
    ('🧵', 'spool', 'hilo'), ('🕒', 'clock-3', 'hora'), ('👀', 'eye', 'mira'),
    ('🏚️', 'house', 'casa dañada'), ('🟦', 'square', 'azul', 'azul r'), ('✍️', 'signature', 'firma'),
    ('⏮', 'skip-back', 'anterior'), ('🌲', 'tree-pine', 'bosque'),
    ('🏜️', 'sun', 'desierto'), ('🌵', 'sun', 'frontera'), ('💯', 'badge-check', 'completo'),
    ('🏧', 'credit-card', 'cajero'), ('🌪️', 'tornado', 'tornado'), ('🔑', 'key', 'clave'),
    ('🚰', 'glass-water', 'agua potable'), ('🏁', 'flag', 'meta'), ('🥈', 'medal', 'segundo lugar', 'plata'),
    ('🎁', 'gift', 'regalo'), ('📭', 'mailbox', 'buzón'), ('👋', 'hand', 'hola'),
    ('🤠', 'user-round', 'vaquero'), ('👩‍🔬', 'microscope', 'ciencia'), ('🚦', 'traffic-cone', 'semáforo'),
    ('🧍', 'person-standing', 'persona'), ('👤', 'user', 'persona'), ('🔘', 'circle-dot', 'opción'),
    ('📕', 'book', 'libro'), ('👏', 'party-popper', 'bien'), ('🧑‍⚖️', 'gavel', 'juez'),
    ('🐕', 'dog', 'perro'), ('🗝️', 'key-round', 'llave'), ('⛏️', 'pickaxe', 'minería'),
    ('🧺', 'shopping-basket', 'canasta'), ('🎩', 'crown', 'élite'), ('📤', 'upload', 'enviar'),
    ('😬', 'frown', 'uy'), ('⚕️', 'heart-pulse', 'salud'), ('♿', 'accessibility', 'accesibilidad'),
    ('👩', 'user-round', 'mujer'), ('👴', 'user-round', 'persona mayor'), ('🎒', 'backpack', 'escolar'),
    ('👩‍🏫', 'presentation', 'maestra'), ('🎖️', 'award', 'condecoración'), ('✋', 'hand', 'alto'),
    ('📮', 'mailbox', 'buzón'), ('🧲', 'magnet', 'imán'), ('♻️', 'recycle', 'reciclaje'),
    ('🏡', 'house', 'casa'), ('🚜', 'tractor', 'campo'), ('🫀', 'heart-pulse', 'corazón'),
    ('🪪', 'id-card', 'credencial'), ('❄️', 'snowflake', 'frío'), ('🚚', 'truck', 'camión'),
    ('🎫', 'ticket', 'boleto'), ('🛬', 'plane-landing', 'llegada'), ('🚌', 'bus', 'autobús'),
    ('👮', 'shield-user', 'policía'), ('👨‍💻', 'laptop', 'programador'), ('🔀', 'shuffle', 'mezclar'),
    ('🌅', 'sunrise', 'amanecer'), ('🥧', 'chart-pie', 'pastel'), ('⏩', 'fast-forward', 'adelantar'),
    ('🎄', 'trees', 'temporada'), ('🍎', 'apple', 'manzana'), ('🚙', 'car', 'camioneta'),
    ('🔺', 'triangle', 'sube', 'rojo r'), ('✔️', 'check', 'sí', 'verde'), ('📐', 'drafting-compass', 'medida'),
    ('🥉', 'medal', 'tercer lugar', 'bronce'), ('🆕', 'sparkles', 'nuevo'), ('➕', 'plus', 'más'),
    ('➖', 'minus', 'menos'),
    # Con el selector U+FE0F obligatorio: sin él son signos de texto (▶ en los
    # botones de reproducir, que el motor compara) y se quedan como están.
    ('▶️', 'play', 'reproducir'), ('↩️', 'undo-2', 'regresar'),
]
ESTRICTOS = {'▶️', '↩️'}


PLANTILLA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iconos_plantilla.js'), encoding='utf-8').read()


def trazo(carpeta, nombre):
    """Lo de adentro del <svg> de Lucide, en una linea."""
    t = open(os.path.join(carpeta, nombre + '.svg'), encoding='utf-8').read()
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    m = re.search(r'<svg[^>]*>(.*)</svg>', t, re.S)
    return re.sub(r'\s+', ' ', m.group(1)).replace(' />', '/>').replace('> <', '><').strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    carpeta = sys.argv[1]
    vistos, mapa, trazos = set(), {}, {}
    for fila in ICONOS:
        emoji, icono, nombre = fila[:3]
        color = fila[3] if len(fila) > 3 else ''
        clave = emoji if emoji in ESTRICTOS else emoji.replace('\ufe0f', '')
        if clave in vistos:
            sys.exit('Emoji repetido en la tabla: ' + emoji)
        vistos.add(clave)
        if icono not in trazos:
            trazos[icono] = trazo(carpeta, icono)
        mapa[clave] = [icono, nombre] + ([color] if color else [])
    js = (PLANTILLA.replace('/*VERSION*/', VERSION_LUCIDE)
          .replace('/*MAPA*/{}', json.dumps(mapa, ensure_ascii=False, separators=(',', ':')))
          .replace('/*TRAZOS*/{}', json.dumps(trazos, ensure_ascii=False, separators=(',', ':'))))
    open(SALIDA, 'wb').write(js.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
    print('%d emojis, %d iconos, %d bytes -> %s' % (len(mapa), len(trazos), len(js.encode('utf-8')), SALIDA))


if __name__ == '__main__':
    sys.exit(main())
