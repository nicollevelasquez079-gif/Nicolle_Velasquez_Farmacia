const API = "/api/v1";
let token = null, me = {}, rows = [], cur = "inicio";

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const money = n => "L. " + Number(n || 0).toLocaleString("es-HN", {minimumFractionDigits: 2, maximumFractionDigits: 2});
const fdate = d => new Date(d + "T00:00:00").toLocaleDateString("es-HN");
const ahora = () => new Date(Date.now() - new Date().getTimezoneOffset() * 6e4).toISOString().slice(0, 19);

/* ============ API ============ */
async function api(path, opts = {}) {
  const r = await fetch(API + path, {
    ...opts,
    headers: {"Content-Type": "application/json", ...(token ? {Authorization: "Bearer " + token} : {})}
  });
  if (r.status === 401 && token) { logout(); throw new Error("Tu sesión venció. Entrá de nuevo."); }
  const d = await r.json().catch(() => null);
  if (!r.ok) {
    const det = d?.detail;
    throw new Error(Array.isArray(det) ? det.map(x => x.loc.slice(-1) + ": " + x.msg).join(", ") : det || "Error " + r.status);
  }
  return d;
}

function toast(msg) {
  const t = $("toast");
  t.textContent = msg; t.style.display = "block";
  clearTimeout(t._h); t._h = setTimeout(() => t.style.display = "none", 2600);
}

/* ============ Qué se puede crear y cómo se llama cada campo ============ */
const ENT = {
  productos: {t: "Productos", s: "producto", ic: "💊", f: [
    {k: "nombre", l: "Nombre"},
    {k: "categoria_id", l: "Categoría", ref: "categorias", lab: "nombre"},
    {k: "precio", l: "Precio (L.)", type: "number", step: "0.01", money: 1},
    {k: "stock", hide: 1, def: 0},   // el stock real se calcula con los lotes
    {k: "requiere_receta", l: "Requiere receta", type: "checkbox"}]},
  categorias: {t: "Categorías", s: "categoría", ic: "🗂️", f: [
    {k: "nombre", l: "Nombre"},
    {k: "descripcion", l: "Descripción", opt: 1}]},
  proveedores: {t: "Proveedores", s: "proveedor", ic: "🚚", f: [
    {k: "razon_social", l: "Razón social"},
    {k: "ruc", l: "RUC"},
    {k: "contacto", l: "Contacto"},
    {k: "telefono", l: "Teléfono", opt: 1}]},
  clientes: {t: "Clientes", s: "cliente", ic: "👥", f: [
    {k: "nombre", l: "Nombre"},
    {k: "identidad", l: "Identidad"},
    {k: "telefono", l: "Teléfono"}]},
  lotes: {t: "Lotes y vencimientos", s: "lote", ic: "📅", f: [
    {k: "producto_id", l: "Producto", ref: "productos", lab: "nombre"},
    {k: "numero_lote", l: "N.º de lote"},
    {k: "proveedor_id", l: "Proveedor", ref: "proveedores", lab: "razon_social"},
    {k: "fecha_vencimiento", l: "Vence", type: "date"},
    {k: "cantidad", l: "Cantidad", type: "number"},
    {k: "precio_compra", l: "Precio de compra (L.)", type: "number", step: "0.01", money: 1}]},
  ventas: {t: "Ventas", s: "venta", nuevo: "Nueva venta", ic: "🛒", noEdit: 1, noDel: 1, custom: ventaForm, f: [
    {k: "fecha", l: "Fecha", type: "datetime"},
    {k: "cliente_id", l: "Cliente", ref: "clientes", lab: "nombre"},
    {k: "total", l: "Total", money: 1}]},
  usuarios: {t: "Usuarios", s: "usuario", ic: "⚙️", noEdit: 1, f: [
    {k: "username", l: "Usuario"},
    {k: "password", l: "Contraseña", type: "password", nolist: 1},
    {k: "rol", l: "Rol", opts: ["empleado", "admin"]}]}
};

/* ============ Navegación ============ */
document.querySelectorAll("[data-v]").forEach(b => b.onclick = () => go(b.dataset.v));

function go(v) {
  cur = v;
  document.querySelectorAll("nav [data-v]").forEach(b => b.classList.toggle("on", b.dataset.v === v));
  $("v-inicio").hidden = v !== "inicio";
  $("v-gen").hidden = v === "inicio";
  window.scrollTo(0, 0);
  v === "inicio" ? cargar() : verGen(v);
}

/* ============ Login / Logout ============ */
$("f").onsubmit = async e => {
  e.preventDefault();
  $("err").textContent = "";
  try {
    me = await api("/auth/login", {method: "POST", body: JSON.stringify({usuario: $("u").value, clave: $("c").value})});
    token = me.access_token;
    $("nom").textContent = me.usuario; $("rol").textContent = me.rol;
        const esAdmin = ["admin", "administrador"].includes(String(me.rol).toLowerCase());
    document.querySelector('nav [data-v="usuarios"]').style.display = esAdmin ? "" : "none";
    $("login").style.display = "none";
    go("inicio");
  } catch (x) { $("err").textContent = x.message; }
};
function logout() { token = null; $("c").value = ""; $("login").style.display = "grid"; }
$("logout").onclick = logout;

/* ============ Listados con crear / editar / eliminar ============ */
async function loadRefs(E) {
  const out = {};
  await Promise.all([...new Set(E.f.filter(f => f.ref).map(f => f.ref))].map(async n => {
    const lab = E.f.find(f => f.ref === n).lab;
    out[n] = Object.fromEntries((await api("/" + n + "/")).map(r => [r.id, r[lab]]));
  }));
  return out;
}

function cell(f, v, refs) {
  if (f.ref) return esc(refs[f.ref]?.[v] ?? "—");
  if (f.type === "checkbox") return v ? "Sí" : "No";
  if (f.money) return money(v);
  if (f.type === "date") return fdate(v);
  if (f.type === "datetime") return esc(new Date(v).toLocaleString("es-HN", {dateStyle: "short", timeStyle: "short"}));
  return esc(v);
}

async function verGen(key) {
  const E = ENT[key];
  $("gt").textContent = E.ic + " " + E.t;
  $("gnew").textContent = "＋ " + (E.nuevo || "Nuevo " + E.s);
    $("gnew").onclick = () => E.custom ? E.custom() : formEnt(key);

  $("gcsv")?.remove();
  $("gnew").insertAdjacentHTML("beforebegin",
    key === "usuarios"
      ? '<button id="gcsv" class="ghost" type="button">💾 Respaldar ahora</button>'
      : '<button id="gcsv" class="ghost" type="button">⬇ CSV</button>');
  $("gcsv").onclick = () => key === "usuarios" ? respaldarAhora() : exportarCSV(key);
  
  $("gq").value = "";
  $("gb").innerHTML = '<div class="empty">Cargando…</div>';
  try {
    const [data, refs] = await Promise.all([api("/" + key + "/"), loadRefs(E)]);
    rows = data.sort((a, b) => a.id - b.id);
    const cols = E.f.filter(f => !f.hide && !f.nolist);
    const act = !E.noEdit || !E.noDel;
    $("gb").innerHTML = rows.length
      ? `<table><tr><th>#</th>${cols.map(f => `<th>${f.l}</th>`).join("")}${act ? "<th></th>" : ""}</tr>` +
        rows.map(r => {
          const tds = cols.map(f => cell(f, r[f.k], refs));
          return `<tr data-id="${r.id}" data-q="${esc(tds.join(" ").toLowerCase())}"><td>${r.id}</td>${tds.map(t => `<td>${t}</td>`).join("")}` +
            (act ? `<td class="ac">${E.noEdit ? "" : '<button class="ic" data-a="e" title="Editar">✏️</button>'}${E.noDel ? "" : '<button class="ic" data-a="d" title="Eliminar">🗑️</button>'}</td>` : "") + "</tr>";
        }).join("") + "</table>"
      : '<div class="empty">Todavía no hay registros. Usá el botón de arriba para crear el primero.</div>';
  } catch (e) { $("gb").innerHTML = `<div class="empty">${esc(e.message)}</div>`; }
}

$("gq").oninput = e => {
  const q = e.target.value.toLowerCase();
  $("gb").querySelectorAll("tr[data-id]").forEach(tr => tr.hidden = !tr.dataset.q.includes(q));
};

$("gb").onclick = async e => {
  const b = e.target.closest("[data-a]");
  if (!b) return;
  const id = +b.closest("tr").dataset.id;
  if (b.dataset.a === "e") return formEnt(cur, rows.find(r => r.id === id));
  if (!confirm("¿Eliminar este registro?")) return;
  try { await api("/" + cur + "/" + id, {method: "DELETE"}); toast("Eliminado"); verGen(cur); }
  catch (x) { toast(x.message); }
};

/* ============ Ventana de formulario ============ */
function abrir(titulo, html, guardar) {
  $("mt").textContent = titulo; $("mb").innerHTML = html; $("me").textContent = "";
  $("modal").hidden = false;
  $("mf").onsubmit = async e => {
    e.preventDefault();
    try { await guardar(); $("modal").hidden = true; }
    catch (x) { $("me").textContent = x.message; }
  };
}
$("mc").onclick = () => $("modal").hidden = true;

async function formEnt(key, rec) {
  const E = ENT[key], refs = await loadRefs(E);
  const html = E.f.filter(f => !f.hide).map(f => {
    const v = rec ? rec[f.k] : (f.def ?? "");
    if (f.type === "checkbox") return `<label class="chk"><input type="checkbox" name="${f.k}" ${v ? "checked" : ""}> ${f.l}</label>`;
    let inp;
    if (f.ref || f.opts) {
      const o = f.ref ? Object.entries(refs[f.ref]) : f.opts.map(x => [x, x]);
      inp = `<select name="${f.k}" required>${f.ref ? '<option value="">Elegí una opción…</option>' : ""}` +
        o.map(([a, b]) => `<option value="${esc(a)}" ${String(a) === String(v) ? "selected" : ""}>${esc(b)}</option>`).join("") + "</select>";
    } else {
      inp = `<input name="${f.k}" type="${f.type || "text"}" ${f.step ? `step="${f.step}"` : ""} ${f.type === "number" ? 'min="0"' : ""} value="${esc(v)}" ${f.opt ? "" : "required"}>`;
    }
    return `<label>${f.l}${inp}</label>`;
  }).join("");

  abrir((rec ? "Editar " : "Nuevo ") + E.s, html, async () => {
    const body = {};
    E.f.forEach(f => {
      const el = $("mf").elements[f.k];
      if (f.hide) body[f.k] = rec ? rec[f.k] : f.def;
      else if (f.type === "checkbox") body[f.k] = el.checked;
      else if (f.type === "number" || f.ref) body[f.k] = Number(el.value);
      else body[f.k] = el.value;
    });
    await api("/" + key + "/" + (rec ? rec.id : ""), {method: rec ? "PUT" : "POST", body: JSON.stringify(body)});
    toast(rec ? "Cambios guardados" : "Creado correctamente");
    verGen(key);
  });
}

/* ============ Nueva venta ============ */
async function ventaForm() {
  const [cl, pr] = await Promise.all([api("/clientes/"), api("/productos/")]);
  if (!cl.length || !pr.length) return toast("Primero creá al menos un cliente y un producto");
  const linea = () => `<div class="ln"><select class="lp">${pr.map(p => `<option value="${p.id}" data-p="${p.precio}">${esc(p.nombre)} · ${money(p.precio)}</option>`).join("")}</select>` +
    '<input class="lc" type="number" min="1" value="1" required><button type="button" class="x" title="Quitar">✕</button></div>';
  const calc = () => {
    const t = [...document.querySelectorAll("#vl .ln")].reduce((s, l) => s + (+l.querySelector(".lc").value || 0) * +l.querySelector(".lp").selectedOptions[0].dataset.p, 0);
    $("vt").textContent = money(t);
  };
  abrir("Nueva venta",
    `<label>Cliente<select id="vc" required>${cl.map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("")}</select></label>` +
    `<div id="vl">${linea()}</div><button type="button" class="ghost" id="va">＋ Agregar otro producto</button>` +
    '<div class="tot">Total: <b id="vt"></b></div>',
    async () => {
      const det = [...document.querySelectorAll("#vl .ln")].map(l => {
        const s = l.querySelector(".lp");
        return {producto_id: +s.value, cantidad: +l.querySelector(".lc").value, precio_unitario: +s.selectedOptions[0].dataset.p};
      });
      const total = det.reduce((s, d) => s + d.cantidad * d.precio_unitario, 0);
      await api("/ventas/", {method: "POST", body: JSON.stringify({fecha: ahora(), total: +total.toFixed(2), cliente_id: +$("vc").value, usuario_id: me.id, detalles: det})});
      toast("Venta registrada");
      verGen("ventas");
    });
  $("va").onclick = () => { $("vl").insertAdjacentHTML("beforeend", linea()); calc(); };
  $("mb").oninput = calc;
  $("mb").onclick = e => { if (e.target.classList.contains("x") && $("vl").children.length > 1) { e.target.parentNode.remove(); calc(); } };
  calc();
}

/* ============ Dashboard de inicio ============ */
const tabla = (cols, filas) => filas.length
  ? `<table><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr>${filas.join("")}</table>`
  : '<div class="empty">Sin datos todavía</div>';

async function cargar() {
  try {
    const [prods, clientes, provs, ventas, detalles, lotes, porVencer] = await Promise.all([
      api("/productos/"), api("/clientes/"), api("/proveedores/"), api("/ventas/"),
      api("/detalleventas/"), api("/lotes/"), api("/lotes/por-vencer?dias=30")]);
    const prodPorId = Object.fromEntries(prods.map(p => [p.id, p]));
    const lotePorId = Object.fromEntries(lotes.map(l => [l.id, l]));
    const cliPorId = Object.fromEntries(clientes.map(c => [c.id, c]));
    const nombreProd = id => prodPorId[id]?.nombre ?? "Producto " + id;

    const hoy = new Date().toDateString();
    const deHoy = ventas.filter(v => new Date(v.fecha).toDateString() === hoy);
    $("k1").textContent = prods.length; $("k2").textContent = clientes.length; $("k3").textContent = provs.length;
    $("k4").textContent = deHoy.length; $("k5").textContent = money(deHoy.reduce((s, v) => s + Number(v.total), 0));
    $("k6").textContent = porVencer.length;

        // gráfica 7 días
    const dias = [...Array(7)].map((_, i) => { const d = new Date(); d.setDate(d.getDate() - 6 + i); return d; });
    const vals = dias.map(d => ventas.filter(v => new Date(v.fecha).toDateString() === d.toDateString()).reduce((s, v) => s + Number(v.total), 0));
    const hayVentas = vals.some(v => v > 0);
    const max = hayVentas ? Math.max(...vals) : 100, W = 520, H = 200, px = 40, py = 14;
    const fmt = n => n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(Math.round(n));
    const x = i => px + i * (W - px - 10) / 6, y = v => H - 28 - (v / max) * (H - 28 - py);
    const pts = vals.map((v, i) => `${x(i)},${y(v)}`).join(" ");
    $("chart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Ventas de los últimos 7 días">` +
      [0, .5, 1].map(f => `<line x1="${px}" x2="${W-10}" y1="${y(max*f)}" y2="${y(max*f)}" stroke="#dfe7f5"/><text x="${px-6}" y="${y(max*f)+4}" font-size="11" fill="#5d6b85" text-anchor="end">${fmt(max*f)}</text>`).join("") +
      `<polygon points="${px},${H-28} ${pts} ${x(6)},${H-28}" fill="#1e6fff" fill-opacity=".12"/><polyline points="${pts}" fill="none" stroke="#1e6fff" stroke-width="3"/>` +
      vals.map((v, i) => `<circle cx="${x(i)}" cy="${y(v)}" r="4.5" fill="#fff" stroke="#1e6fff" stroke-width="2.5"><title>${money(v)}</title></circle><text x="${x(i)}" y="${H-8}" font-size="12" fill="#5d6b85" text-anchor="middle">${dias[i].toLocaleDateString("es-HN", {weekday: "short"})}</text>`).join("") +
      (hayVentas ? "" : `<text x="${W/2}" y="${H/2 - 10}" font-size="14" fill="#5d6b85" text-anchor="middle">Sin ventas en los últimos 7 días</text>`) +
      "</svg>";
    
      // más vendidos
    const vend = {};
    detalles.forEach(d => { const pid = lotePorId[d.lote_id]?.producto_id; if (pid) vend[pid] = (vend[pid] || 0) + d.cantidad; });
    const top = Object.entries(vend).sort((a, b) => b[1] - a[1]).slice(0, 5);
    $("top").innerHTML = top.length
      ? top.map(([id, n], i) => `<li><span>${i + 1}. ${esc(nombreProd(id))}</span><em>${n} unidades</em></li>`).join("")
      : '<div class="empty">Aún no hay ventas registradas</div>';

    // lotes por vencer
    const faltan = f => Math.ceil((new Date(f + "T00:00:00") - new Date()) / 864e5);
    $("t-lotes").innerHTML = tabla(["Producto", "Lote", "Vence", "Stock"], porVencer.slice(0, 5).map(l => {
      const d = faltan(l.fecha_vencimiento), c = d <= 10 ? "d-red" : d <= 20 ? "d-ora" : "d-blu";
      return `<tr><td>${esc(nombreProd(l.producto_id))}</td><td>${esc(l.numero_lote)}</td><td>${fdate(l.fecha_vencimiento)}</td><td><span class="pill ${c}">${l.cantidad}</span></td></tr>`;
    }));

    // inventario (stock real = lotes vigentes), primero lo más crítico
    const hoyISO = ahora().slice(0, 10), stock = {};
    lotes.filter(l => l.fecha_vencimiento >= hoyISO).forEach(l => stock[l.producto_id] = (stock[l.producto_id] || 0) + l.cantidad);
    const criticos = [...prods].sort((a, b) => (stock[a.id] || 0) - (stock[b.id] || 0)).slice(0, 5);
    $("t-inv").innerHTML = tabla(["Producto", "Stock", "Estado"], criticos.map(p => {
      const s = stock[p.id] || 0;
      const [c, t] = s === 0 ? ["p-out", "Agotado"] : s <= 30 ? ["p-low", "Stock bajo"] : ["p-ok", "Disponible"];
      return `<tr><td>${esc(p.nombre)}</td><td>${s}</td><td><span class="pill ${c}">${t}</span></td></tr>`;
    }));

    // últimas ventas
    const ult = [...ventas].sort((a, b) => new Date(b.fecha) - new Date(a.fecha)).slice(0, 5);
    $("t-ventas").innerHTML = tabla(["Fecha", "Cliente", "Total"], ult.map(v =>
      `<tr><td>${new Date(v.fecha).toLocaleString("es-HN", {dateStyle: "short", timeStyle: "short"})}</td><td>${esc(cliPorId[v.cliente_id]?.nombre ?? "—")}</td><td>${money(v.total)}</td></tr>`));
  } catch (e) { toast("No se pudieron cargar los datos: " + e.message); }
}

/* ============ Exportar CSV y respaldo ============ */
async function exportarCSV(entidad) {
  try {
    const r = await fetch(API + "/reportes/csv/" + entidad, {headers: {Authorization: "Bearer " + token}});
    if (!r.ok) throw new Error("No se pudo exportar");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(await r.blob());
    a.download = entidad + "_" + new Date().toISOString().slice(0, 10) + ".csv";
    a.click();
    URL.revokeObjectURL(a.href);
    toast("CSV descargado");
  } catch (e) { toast(e.message); }
}

async function respaldarAhora() {
  try { await api("/respaldos/", {method: "POST"}); toast("Respaldo iniciado"); }
  catch (e) { toast(e.message); }
}