"""Integración única del Inspector; preserva los saltos originales y guarda respaldo."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'backups' / '20260923-inspector-previo'

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Ancla no única: ' + old[:90])
    return text.replace(old, new, 1)

def nl(text):
    return text.replace('\r\n', '\n').replace('\n', '\r\n')

html_path = ROOT / 'index.html'
engine_path = ROOT / 'assets/js/audit-engine.js'
html_original = html_path.read_bytes().decode('utf-8')
engine_original = engine_path.read_bytes().decode('utf-8')
if 'id="inspectorWorkspace"' in html_original:
    raise SystemExit('El Inspector ya está integrado; no repetir la migración.')

start = html_original.index('    <div id="tab-panel-verificador"')
end = html_original.index('    </div><!-- FIN PESTAÑA 6 -->', start) + len('    </div><!-- FIN PESTAÑA 6 -->')
html = html_original[:start] + nl('''    <div id="tab-panel-verificador" class="tab-panel">
      <div id="inspectorWorkspace" class="iw-workspace">
        <p>Preparando el cuaderno del Inspector…</p>
      </div>
    </div><!-- FIN PESTAÑA 6 -->''') + html_original[end:]
html = once(html, '  <link rel="stylesheet" href="assets/css/auditavision.css?v=20260922c">', nl('''  <link rel="stylesheet" href="assets/css/auditavision.css?v=20260922c">
  <link rel="stylesheet" href="assets/css/inspector-workspace.css?v=20260922c">'''))
html = once(html, '  <script src="assets/js/audit-engine.js?v=20260922c"></script>', nl('''  <script src="assets/js/inspector-model.js?v=20260922c"></script>
  <script src="assets/js/inspector-workspace.js?v=20260922c"></script>
  <script src="assets/js/audit-engine.js?v=20260922c"></script>'''))
html = once(html, '<div id="tab-panel-comunidad" class="tab-panel">', nl('''<div id="tab-panel-comunidad" class="tab-panel">
      <section class="section-hero">
        <h2>Investigar y conversar sobre un expediente</h2>
        <p>La nueva mesa del Inspector reúne preguntas, fuentes y réplicas por caso. Esta primera versión guarda las aportaciones sólo en este navegador.</p>
        <button type="button" class="jerarquia-btn" data-iw-open="dialogo">Abrir la mesa ciudadana del Inspector</button>
      </section>'''))

start = engine_original.index('  function initFactCheckModule() {')
end = engine_original.index('  // ==========================================================================\r\n  // INICIALIZACIÓN GLOBAL', start)
compat = '''  // Compatibilidad con enlaces antiguos. Los dictámenes prefijados se retiraron.
  function initFactCheckModule() { window.InspectorWorkspace?.init(); }
  function renderFactCheckModule() { window.InspectorWorkspace?.init(); }
  function selectFactCheckPreset() { window.InspectorWorkspace?.open('notas'); }
  function onFactCheckDependenciaChange() { window.InspectorWorkspace?.open('vigilar'); }
  function handleFactCheckFileSelect() { window.InspectorWorkspace?.open('notas'); }
  function evaluarNoticiaForense() { window.InspectorWorkspace?.open('notas'); }
  function resetNoticiaForense() { window.InspectorWorkspace?.open('notas'); }
  function toggleHoverFactCheck() { /* No hay evaluaciones por pasar el cursor. */ }
  function handleFactCheckHover() { /* La revisión requiere evidencia explícita. */ }
  function copiarDictamenForense() { window.InspectorWorkspace?.open('notas'); }

'''
engine = engine_original[:start] + nl(compat) + engine_original[end:]
engine = once(engine, '      initInspectorExplorador();', '      // El nuevo seguimiento no publica índices con insumos sin verificar.')
engine = once(engine, "t: '6. Modo Inspector (Auditoría Forense Hacendaria en Vivo)',", "t: '6. Modo Inspector · Evidencia, seguimiento y conversación',")
old_description = "d: 'Una cifra dicha en una nota de prensa o en un discurso puede contrastarse. Pega una liga, un PDF o una declaración y este módulo la confronta contra los ingresos aprobados (PEF y LIF), el gasto devengado, las auditorías de la ASF y las cuentas públicas que aún están pendientes de rendir.'"
engine = once(engine, old_description, "d: 'Registra una afirmación, reúne documentos y propone una conclusión con fuentes y límites. Sigue dependencias y conversa por expediente en un cuaderno local; no se emiten dictámenes automáticos.'")
engine = once(engine, 'const AUTOLINK_OMITIR_CLASES = new Set([', "const AUTOLINK_OMITIR_CLASES = new Set([\r\n    'iw-workspace',")

# La suma no permite inferir pérdidas totales ni obligaciones personales.
start = engine.index("        '<div class=\"cc-vivo-tira\">' +")
end = engine.index("        '<ul class=\"cc-relojes\">' +",start)
engine = engine[:start] + nl('''        '<p class="cc-rel-personal">Estas magnitudes se presentan por separado: pueden solaparse y no constituyen un total de dinero perdido. La distribución por habitante o contribuyente es ilustrativa; no es una deuda personal exigible.</p>' +

''') + engine[end:]
start = engine.index("        '<div class=\"cc-rel-total\">' +")
end = engine.index("        '<div class=\"cc-sobrecosto\">' +",start)
engine = engine[:start] + engine[end:]
for declaration in [
    '    const totalPais = relojes.reduce((a, r) => a + r.anualPais, 0);\r\n',
    '    const totalSeg = relojes.reduce((a, r) => a + r.porSegundoPais, 0);\r\n',
    '    const totalPersona = relojes.reduce((a, r) => a + r.anualPersona, 0);\r\n',
    '    const totalCadencia = relojes.reduce((a, r) => a + r.enCadencia, 0);\r\n'
]: engine = once(engine,declaration,'')
engine = once(engine, 'dropdown.innerHTML = `<div style="padding:12px; font-size:12px; color:var(--text-dim); text-align:center;">No se hallaron coincidencias para "${q}"</div>`;', 'dropdown.textContent = `No se hallaron coincidencias para "${q}"`;')

for old,new,name in [(html_original,html,'index.html'),(engine_original,engine,'audit-engine.js')]:
    if len(re.findall(r'\r(?!\n)',old)) != len(re.findall(r'\r(?!\n)',new)):
        raise ValueError('Cambió el número de CR aislados de ' + name)
BACKUP.mkdir(parents=True,exist_ok=False)
for path in [html_path,engine_path,ROOT/'CONTEXT.md',ROOT/'herramientas/sello.py']:
    dest = BACKUP / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,dest)
html_path.write_bytes(html.encode('utf-8'))
engine_path.write_bytes(engine.encode('utf-8'))
print('Inspector integrado. Respaldo local: ' + str(BACKUP))
