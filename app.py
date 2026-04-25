from flask import Flask, request, redirect, session
import random
import json
import os
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "drakito_block_2026_secret")

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://nzoguuqiqeztgsrdcjwe.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "TeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56b2d1dXFpcWV6dGdzcmRjandlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzA3MDEyMywiZXhwIjoyMDkyNjQ2MTIzfQ.XdTIhx_ShbfGGsiCCXLK8EYiipVi55t7GF2bTPhevm4")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LOGO_URL = "https://i.postimg.cc/x8KdvtPQ/IMG-20260411-020447-078.jpg"

def init_db():
    # En Supabase las tablas se crean vía Dashboard. 
    # Aquí solo aseguramos que los admins existan.
    users_to_check = [
        ("jhorny", "123456", "admin"),
        ("DRAKITO_VIP7020", "860055", "admin"),
        ("operador1", "123456", "operador")
    ]
    
    for u, p, r in users_to_check:
        res = supabase.table("usuarios").select("user").eq("user", u).execute()
        if not res.data:
            supabase.table("usuarios").insert({
                "user": u, 
                "pass": p, 
                "rol": r, 
                "creditos": 999999 if r == "admin" else 0,
                "creado_por": "system" if r == "admin" else "jhorny"
            }).execute()

def require_login():
    return "user" in session

def is_super_admin():
    return session.get("user") in ["jhorny", "DRAKITO_VIP7020"]

def can_use_client_features():
    return session.get("rol") in ["user", "admin"] or is_super_admin()

def logo_html(size_class: str, extra_class: str = ""):
    return f"""
    <div class="{size_class} rounded-full overflow-hidden border-[2px] border-cyan-400 bg-black flex items-center justify-center shadow-[0_0_20px_rgba(34,211,238,0.5)] animate-pulse-slow {extra_class}">
        <img src="{LOGO_URL}" class="w-full h-full object-cover rounded-full scale-125" alt="logo">
    </div>
    """

def layout(content, show_nav=False, login_bg=False):
    u = session.get("user")
    r = session.get("rol")

    is_boss = is_super_admin()
    is_admin = (r == "admin")
    is_operador = (r == "operador")
    is_client_side = can_use_client_features()

    nav = ""
    if show_nav:
        nav = f"""
        <div class="w-full rounded-[24px] overflow-hidden mb-8 relative z-40 bg-[#08101a] border border-[#162336] shadow-[0_0_25px_rgba(0,0,0,0.5)]">
            <div class="flex items-center justify-between px-5 py-4">
                <div class="flex items-center gap-3">
                    {logo_html("w-12 h-12")}
                    <div class="flex flex-col">
                        <span class="text-[17px] font-black tracking-widest bg-gradient-to-r from-cyan-300 to-purple-400 bg-clip-text text-transparent uppercase">
                            Drakito Block
                        </span>
                    </div>
                </div>

                <button onclick="toggleMenu()" class="w-12 h-12 rounded-full bg-[#111a26] flex items-center justify-center text-cyan-400 shadow-md">
                    <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-8 6h8"></path>
                    </svg>
                </button>
            </div>
        </div>

        <div id="sidebar" class="fixed top-0 right-0 h-full w-72 bg-[#060b14] border-l border-[#162336] transform translate-x-full transition-transform duration-300 ease-in-out z-50 p-6 shadow-2xl overflow-y-auto">
            <div class="flex justify-between items-center mb-10">
                <span class="text-[11px] font-bold text-cyan-400 uppercase tracking-[0.2em]">MENÚ DE CONTROL</span>
                <button onclick="toggleMenu()" class="text-white text-3xl">&times;</button>
            </div>

            <div class="flex flex-col gap-6">
                <a href="/" class="text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2">🏠 INICIO</a>
                
                {"<a href='/panel_admin' class='text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2'>💎 PANEL ADMIN</a>" if is_boss or is_admin else ""}
                
                {"<a href='/gestion' class='text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2'>⚙️ GESTIÓN</a>" if is_operador else ""}
                
                <a href="/planes" class="text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2">🛒 COMPRAR CRÉDITOS</a>
                
                {"<a href='/bloqueo' class='text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2'>🚫 BLOQUEO</a>" if is_client_side else ""}
                
                {"<a href='/bancas' class='text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2'>🏦 BANCAS</a>" if is_client_side else ""}
                
                <a href="/soporte" class="text-sm font-bold uppercase text-white hover:text-cyan-400 flex items-center gap-2">🎧 SOPORTE</a>
                
                <hr class="border-[#162336] my-2">
                
                <a href="/logout" class="text-sm font-bold uppercase text-red-500 flex items-center gap-2">🚪 SALIR</a>
            </div>
        </div>

        <div id="overlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/80 hidden z-40"></div>
        """

    modal_script = """
    <script>
        function toggleMenu() {
            document.getElementById('sidebar')?.classList.toggle('translate-x-full');
            document.getElementById('overlay')?.classList.toggle('hidden');
        }

        function showReport(tipo, referencia, respuesta, detalle, codigo, operador) {
            document.getElementById('rep_tipo').innerText = tipo || '';
            document.getElementById('rep_ref').innerText = referencia || '';
            
            if(respuesta) {
                document.getElementById('rep_respuesta').innerHTML = "✅ " + respuesta + " ✅";
            } else {
                document.getElementById('rep_respuesta').innerHTML = "";
            }
            
            document.getElementById('rep_detalle').innerText = detalle || '';
            document.getElementById('rep_codigo').innerText = codigo || '';
            document.getElementById('rep_operador').innerText = operador || '';
            document.getElementById('modalReport').classList.remove('hidden');
        }

        function closeReport() {
            document.getElementById('modalReport').classList.add('hidden');
        }

        function copyText(texto) {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(texto).then(() => {
                    alert('Copiado correctamente');
                }).catch(() => {
                    fallbackCopy(texto);
                });
            } else {
                fallbackCopy(texto);
            }
        }

        function fallbackCopy(texto) {
            const area = document.createElement('textarea');
            area.value = texto;
            area.style.position = 'fixed';
            area.style.left = '-9999px';
            area.style.top = '0';
            document.body.appendChild(area);
            area.focus();
            area.select();
            try {
                document.execCommand('copy');
                alert('Copiado correctamente');
            } catch (err) {
                alert('No se pudo copiar automáticamente');
            }
            document.body.removeChild(area);
        }

        function copyReport() {
            const texto =
`TIPO: ${document.getElementById('rep_tipo').innerText}

REFERENCIA: ${document.getElementById('rep_ref').innerText}

RESPUESTA:
${document.getElementById('rep_respuesta').innerText}

DETALLE:
${document.getElementById('rep_detalle').innerText}

CÓDIGO: ${document.getElementById('rep_codigo').innerText}
OPERADOR: ${document.getElementById('rep_operador').innerText}`;

            copyText(texto);
        }
    </script>
    """

    modal_html = f"""
    <div id="modalReport" class="hidden fixed inset-0 bg-black/90 z-[60] flex items-center justify-center p-4">
        <div class="bg-[#08101a] border border-[#162336] w-full max-w-sm rounded-[30px] p-6 shadow-[0_0_30px_rgba(0,0,0,0.8)] relative">
            <button onclick="closeReport()" class="absolute top-4 right-5 text-gray-400 font-bold text-xl hover:text-white transition">&times;</button>

            <div class="text-center mb-6">
                {logo_html("w-16 h-16", "mx-auto mb-3 shadow-[0_0_15px_rgba(34,211,238,0.5)]")}
                <h3 class="text-cyan-400 font-bold uppercase tracking-widest text-sm">REPORTE OFICIAL</h3>
                <p class="text-[9px] text-gray-500 uppercase tracking-widest mt-1">Drakito Block System</p>
            </div>

            <div class="space-y-4 text-xs font-mono text-gray-300">
                <div class="flex justify-between gap-3 border-b border-[#162336] pb-2">
                    <span class="text-gray-500">TIPO:</span>
                    <span id="rep_tipo" class="text-cyan-400 font-bold uppercase"></span>
                </div>

                <div class="flex justify-between gap-3 border-b border-[#162336] pb-2">
                    <span class="text-gray-500">REFERENCIA:</span>
                    <span id="rep_ref" class="text-white font-bold uppercase"></span>
                </div>

                <div class="border-b border-[#162336] pb-3">
                    <p class="text-gray-500 mb-1">RESPUESTA:</p>
                    <p id="rep_respuesta" class="text-emerald-400 font-bold whitespace-pre-line"></p>
                </div>

                <div class="border-b border-[#162336] pb-3">
                    <p class="text-gray-500 mb-1">DETALLE:</p>
                    <p id="rep_detalle" class="text-white font-bold whitespace-pre-line leading-relaxed"></p>
                </div>

                <div class="flex justify-between gap-3 border-b border-[#162336] pb-2">
                    <span class="text-gray-500">CÓDIGO:</span>
                    <span id="rep_codigo" class="text-yellow-400 font-bold"></span>
                </div>

                <div class="flex justify-between gap-3 border-b border-[#162336] pb-2">
                    <span class="text-gray-500">OPERADOR:</span>
                    <span id="rep_operador" class="text-cyan-500 font-bold"></span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mt-8">
                <button onclick="copyReport()" class="bg-[#111b29] text-emerald-400 border border-[#1e293b] rounded-full py-3 text-[11px] uppercase font-bold tracking-widest shadow-lg hover:bg-[#1e293b] transition">
                    COPIAR
                </button>
                <button onclick="closeReport()" class="bg-[#111b29] text-cyan-400 border border-[#1e293b] rounded-full py-3 text-[11px] uppercase font-bold tracking-widest shadow-lg hover:bg-[#1e293b] transition">
                    CERRAR
                </button>
            </div>
        </div>
    </div>
    """

    login_background_html = ""
    if login_bg:
        login_background_html = f"""
        <div class="login-bg"></div>
        <div class="login-overlay"></div>
        """

    styles = """
    <style>
        body {
            background-color: #040914;
            color: white;
            font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            touch-action: manipulation;
            overflow-x: hidden;
            min-height: 100vh;
        }

        .animate-pulse-slow {
            animation: pulseGlow 3s ease-in-out infinite alternate;
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 10px rgba(34,211,238,0.3); }
            100% { box-shadow: 0 0 25px rgba(34,211,238,0.6); }
        }

        .neon-card {
            background-color: #08101a;
            border: 1px solid #162336;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .input-dark {
            background-color: #111a26;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
            width: 100%;
            outline: none;
            color: white;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        .input-dark:focus {
            border-color: rgba(56, 189, 248, 0.5);
        }

        .input-dark::placeholder {
            color: #64748b;
        }

        .login-bg {
            position: fixed;
            inset: 0;
            background-image: url('https://i.postimg.cc/x8KdvtPQ/IMG-20260411-020447-078.jpg');
            background-size: cover;
            background-position: center;
            transform: scale(1.05);
            animation: bgmove 20s ease-in-out infinite alternate;
            z-index: 0;
            filter: brightness(0.15) saturate(1.2) blur(2px);
        }

        .login-overlay {
            position: fixed;
            inset: 0;
            background: radial-gradient(circle at center, rgba(34,211,238,0.05), #040914 80%);
            z-index: 1;
        }

        @keyframes bgmove {
            0% { transform: scale(1.05) translate(0px, 0px); }
            100% { transform: scale(1.15) translate(-15px, -10px); }
        }

        .content-wrap {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 26rem;
            margin: 0 auto;
        }
    </style>
    """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    {styles}
    {modal_script}
</head>
<body class="p-4 flex flex-col items-center">
    {login_background_html}
    <div class="content-wrap">
        {nav}
        {content}
    </div>
    {modal_html if not login_bg else ""}
</body>
</html>"""


@app.route("/")
def index():
    if not require_login():
        return redirect("/login")

    # Obtener créditos
    res_user = supabase.table("usuarios").select("creditos").eq("user", session["user"]).execute()
    restantes = res_user.data[0]["creditos"] if res_user.data else 0

    # Contar exitosos
    res_count = supabase.table("pedidos").select("id_pedido", count="exact").eq("cliente", session["user"]).eq("estado", "EXITOSO").execute()
    usados = res_count.count if res_count.count is not None else 0

    # Historial (limit 8)
    res_peds = supabase.table("pedidos").select("*").eq("cliente", session["user"]).order("id_pedido", desc=True).limit(8).execute()
    peds = res_peds.data

    historial = ""
    for p in peds:
        if p["estado"] == "EXITOSO":
            args = ",".join([
                json.dumps((p["tipo"] or "").upper()),
                json.dumps(p["referencia"] or ""),
                json.dumps(p["respuesta"] or ""),
                json.dumps(p["detalle"] or ""),
                json.dumps(p["codigo"] or ""),
                json.dumps(p["operador"] or "")
            ])
            btn = f"""
            <button onclick='showReport({args})'
                class="bg-transparent text-cyan-400 border border-cyan-500/30 rounded-lg px-4 py-1.5 text-[9px] font-bold uppercase tracking-widest hover:bg-cyan-500/10 transition">
                VER REPORTE
            </button>
            """
        elif p["estado"] == "RECHAZADO":
            btn = '<span class="text-[9px] text-[#ff3333] font-bold tracking-widest uppercase">RECHAZADO</span>'
        else:
            btn = '<span class="text-[9px] text-gray-500 italic font-bold tracking-widest uppercase">PROCESANDO</span>'

        historial += f"""
        <div class="flex justify-between items-center border-b border-[#162336] py-4 gap-4">
            <div class="flex flex-col">
                <span class="text-sm font-mono text-white tracking-wide">{p["referencia"] or "SOLICITUD"}</span>
                <span class="text-[10px] text-cyan-500 uppercase mt-1 font-bold">{(p["tipo"] or "").upper()}</span>
            </div>
            {btn}
        </div>
        """

    content = f"""
    <div class="flex flex-col items-center mb-8 mt-2">
        {logo_html("w-20 h-20", "mb-4 border-[3px]")}
        <h1 class="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-400">
            Drakito Block
        </h1>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="bg-[#08101a] rounded-[20px] p-5 text-center border border-blue-600 shadow-[0_0_15px_rgba(37,99,235,0.15)]">
            <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-2">USADOS</p>
            <h2 class="text-4xl font-bold text-white">{usados}</h2>
        </div>
        <div class="bg-[#08101a] rounded-[20px] p-5 text-center border border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-2">RESTANTES</p>
            <h2 class="text-4xl font-bold text-white">{restantes}</h2>
        </div>
    </div>

    <div class="neon-card p-6 mb-8">
        <h3 class="text-[11px] font-bold text-cyan-400 uppercase tracking-widest mb-5 text-center">HISTORIAL</h3>
        <div class="space-y-1">
            {historial or "<p class='text-center text-gray-600 text-sm py-5'>Sin historial</p>"}
        </div>
    </div>
    
    <div class="neon-card p-6 relative overflow-hidden mb-6">
        <h3 class="text-[13px] font-bold text-cyan-400 uppercase text-center mb-8 tracking-[0.2em]">GUÍA DE USO</h3>

        <div class="mb-6">
            <h4 class="text-white font-bold text-sm mb-2 flex items-center gap-2">
                <span>💰</span> Recargas
            </h4>
            <p class="text-gray-400 text-xs mb-1">
                Planes desde <span class="text-[#10b981] font-bold">S/15</span> hasta <span class="text-[#10b981] font-bold">S/200</span>
            </p>
            <p class="text-gray-400 text-xs">Recarga segura desde el sistema.</p>
        </div>

        <div class="mb-6">
            <h4 class="text-white font-bold text-sm mb-2 flex items-center gap-2">
                <span>🎧</span> Soporte
            </h4>
            <p class="text-gray-400 text-xs mb-1">Soporte inmediato 24/7 ante cualquier inconveniente.</p>
            <p class="text-[#10b981] font-bold text-xs tracking-widest uppercase">GRATIS</p>
        </div>

        <div class="mb-6">
            <h4 class="text-white font-bold text-sm mb-3 flex items-center gap-2">
                <span class="text-red-500">🚫</span> Bloqueo
            </h4>
            <ul class="list-disc pl-5 text-gray-400 text-xs space-y-2 mb-3">
                <li>Crea una solicitud de bloqueo de línea o IMEI.</li>
                <li>Un operador especializado manejará su caso en privado.</li>
                <li>Te pedirá información completa del dispositivo y en línea.</li>
            </ul>
            <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                <span class="text-yellow-400">💳</span> Costo: 1 crédito
            </p>
        </div>

        <div class="mb-2">
            <h4 class="text-white font-bold text-sm mb-5 flex items-center gap-2">
                <span>🏦</span> Bancos
            </h4>

            <div class="mb-5">
                <h5 class="text-cyan-400 font-bold text-sm mb-1">Ágora</h5>
                <p class="text-gray-400 text-xs mb-2">Realiza tu consulta usando el número o DNI.</p>
                <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                    <span class="text-yellow-400">💳</span> Costo: 2 créditos
                </p>
            </div>

            <div class="mb-5">
                <h5 class="text-cyan-400 font-bold text-sm mb-1">BCP</h5>
                <p class="text-gray-400 text-xs mb-2">Realiza tu consulta usando el número o DNI.</p>
                <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                    <span class="text-yellow-400">💳</span> Costo: 2 créditos
                </p>
            </div>

            <div class="mb-5">
                <h5 class="text-cyan-400 font-bold text-sm mb-1">IBK</h5>
                <p class="text-gray-400 text-xs mb-2">Realiza tu consulta usando el número o DNI.</p>
                <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                    <span class="text-yellow-400">💳</span> Costo: 2 créditos
                </p>
            </div>

            <div class="mb-5">
                <h5 class="text-cyan-400 font-bold text-sm mb-1">Yape</h5>
                <p class="text-gray-400 text-xs mb-2">Realiza tu consulta usando el número o DNI.</p>
                <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                    <span class="text-yellow-400">💳</span> Costo: 2 créditos
                </p>
            </div>

            <div class="mb-2">
                <h5 class="text-cyan-400 font-bold text-sm mb-1">Caja Arequipa</h5>
                <p class="text-gray-400 text-xs mb-2">Realiza tu consulta usando el número o DNI.</p>
                <p class="text-[#ff3333] font-bold text-xs flex items-center gap-1">
                    <span class="text-yellow-400">💳</span> Costo: 2 créditos
                </p>
            </div>
        </div>
    </div>
    """
    return layout(content, True)


@app.route("/planes")
def planes():
    if not require_login():
        return redirect("/login")

    precios = [
        ("01 CRÉDITO", "S/15.00"),
        ("04 CRÉDITOS", "S/60.00"),
        ("06 CRÉDITOS", "S/90.00"),
        ("10 CRÉDITOS", "S/150.00"),
        ("12 CRÉDITOS", "S/120.00"),
        ("20 CRÉDITOS", "S/200.00"),
    ]

    cards = ""
    for nombre, precio in precios:
        cards += f"""
        <div class="p-5 mb-4 rounded-[20px] border border-[#a855f7]/50 bg-[#08101a] flex justify-between items-center shadow-[0_0_15px_rgba(168,85,247,0.15)]">
            <div>
                <h3 class="text-white font-bold text-xl tracking-tight">{nombre}</h3>
                <p class="text-gray-500 text-sm font-mono mt-1.5">{precio}</p>
            </div>
            <a href="https://t.me/DRAKO1X" target="_blank"
               class="bg-gradient-to-r from-[#d946ef] to-[#9333ea] px-6 py-3 rounded-full text-[10px] font-bold uppercase tracking-widest text-white shadow-[0_0_15px_rgba(217,70,239,0.4)] hover:opacity-90 transition">
               COMPRAR
            </a>
        </div>
        """

    content = f"""
    <div class="mt-6 mb-8 text-center">
        <h2 class="text-[12px] text-cyan-400 font-black italic uppercase tracking-[0.2em] mb-6">
            PAQUETES OFICIALES
        </h2>
    </div>
    <div class="space-y-3">
        {cards}
    </div>
    """
    return layout(content, True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("cap") == str(session.get("captcha_val")):
            u = request.form.get("u", "").strip()
            p = request.form.get("p", "").strip()

            res = supabase.table("usuarios").select("rol").eq("user", u).eq("pass", p).execute()

            if res.data:
                session["user"] = u
                session["rol"] = res.data[0]["rol"]
                return redirect("/")

    session["captcha_val"] = random.randint(100000, 999999)

    content = f"""
    <div class="flex flex-col items-center mt-16">
        {logo_html("w-28 h-28", "mb-6 border-[3px] shadow-[0_0_30px_rgba(34,211,238,0.6)]")}
        
        <h1 class="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-400">
            Drakito Block
        </h1>
        <p class="text-[10px] uppercase tracking-[0.4em] text-cyan-500 mb-8 mt-2 font-bold">
            Access Panel
        </p>

        <form method="post" class="w-full space-y-4 bg-[#08101a]/90 border border-[#162336] rounded-[24px] p-6 shadow-2xl backdrop-blur-sm">
            <input name="u" placeholder="Usuario" class="w-full bg-[#111a26] border border-[#1e293b] rounded-xl p-4 text-white outline-none focus:border-cyan-500 transition" autocomplete="off" required>
            <input name="p" type="password" placeholder="Contraseña" class="w-full bg-[#111a26] border border-[#1e293b] rounded-xl p-4 text-white outline-none focus:border-cyan-500 transition" required>

            <div class="flex gap-3 pt-2">
                <div class="bg-white text-black rounded-xl flex items-center justify-center font-bold w-1/2 text-2xl tracking-widest shadow-inner">
                    {session['captcha_val']}
                </div>
                <input name="cap" placeholder="Captcha" class="w-1/2 bg-[#111a26] border border-[#1e293b] rounded-xl p-4 text-white text-center outline-none focus:border-cyan-500 transition" autocomplete="off" required>
            </div>

            <button class="w-full bg-[#0ea5e9] p-4 rounded-xl font-bold text-sm uppercase tracking-widest text-white shadow-[0_0_15px_rgba(14,165,233,0.4)] mt-4 hover:bg-[#0284c7] transition">
                Acceder
            </button>
        </form>

        <a href="https://t.me/DRAKO1X" target="_blank"
           class="mt-10 text-cyan-400 text-[11px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 italic w-full hover:text-cyan-300 transition">
           <span>👤</span> CONTACTAR AL VENDEDOR
        </a>
    </div>
    """
    return layout(content, False, True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/panel_admin", methods=["GET", "POST"])
def panel_admin():
    if not require_login():
        return redirect("/login")

    u_log = session.get("user")
    r_log = session.get("rol")

    if not is_super_admin() and r_log != "admin":
        return redirect("/")

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "crear":
            rol_a_crear = request.form.get("r", "user")
            if r_log == "admin" and not is_super_admin() and rol_a_crear != "user":
                return "Error: admin solo crea clientes", 403

            nuevo_user = request.form["u"].strip()
            nuevo_pass = request.form["p"].strip()
            
            # Verificar si existe
            check = supabase.table("usuarios").select("user").eq("user", nuevo_user).execute()
            if not check.data:
                supabase.table("usuarios").insert({
                    "user": nuevo_user,
                    "pass": nuevo_pass,
                    "rol": rol_a_crear,
                    "creditos": 0,
                    "creado_por": u_log
                }).execute()
                
                session["last_user_created"] = {
                    "user": nuevo_user,
                    "pass": nuevo_pass,
                    "rol": rol_a_crear,
                    "url": request.host_url + "login"
                }

        elif action in ["creditos", "quitar_creditos", "sumar_rapido"]:
            target = request.form["target"]
            # Obtener datos de admin y target
            admin_data = supabase.table("usuarios").select("creditos").eq("user", u_log).execute()
            target_data = supabase.table("usuarios").select("creditos").eq("user", target).execute()
            
            if target_data.data:
                saldo_admin = admin_data.data[0]["creditos"] if admin_data.data else 0
                saldo_target = target_data.data[0]["creditos"]
                
                cant = int(request.form.get("cant", 0))
                
                if action == "creditos":
                    if is_super_admin() or saldo_admin >= cant:
                        supabase.table("usuarios").update({"creditos": saldo_target + cant}).eq("user", target).execute()
                        if not is_super_admin():
                            supabase.table("usuarios").update({"creditos": saldo_admin - cant}).eq("user", u_log).execute()
                            
                elif action == "quitar_creditos":
                    quitar_real = min(cant, saldo_target)
                    if quitar_real > 0:
                        supabase.table("usuarios").update({"creditos": saldo_target - quitar_real}).eq("user", target).execute()
                        if not is_super_admin():
                            supabase.table("usuarios").update({"creditos": saldo_admin + quitar_real}).eq("user", u_log).execute()

                elif action == "sumar_rapido":
                    if cant > 0: # Sumar
                        if is_super_admin() or saldo_admin >= cant:
                            supabase.table("usuarios").update({"creditos": saldo_target + cant}).eq("user", target).execute()
                            if not is_super_admin():
                                supabase.table("usuarios").update({"creditos": saldo_admin - cant}).eq("user", u_log).execute()
                    else: # Restar
                        quitar = abs(cant)
                        quitar_real = min(quitar, saldo_target)
                        if quitar_real > 0:
                            supabase.table("usuarios").update({"creditos": saldo_target - quitar_real}).eq("user", target).execute()
                            if not is_super_admin():
                                supabase.table("usuarios").update({"creditos": saldo_admin + quitar_real}).eq("user", u_log).execute()

        elif action == "eliminar_usuario":
            target = request.form.get("target")
            if target not in ["jhorny", "DRAKITO_VIP7020", "operador1"]:
                if is_super_admin():
                    supabase.table("usuarios").delete().eq("user", target).execute()
                else:
                    supabase.table("usuarios").delete().eq("user", target).eq("creado_por", u_log).execute()

    # Listar usuarios
    if is_super_admin():
        res_users = supabase.table("usuarios").select("*").order("id", desc=True).execute()
    else:
        res_users = supabase.table("usuarios").select("*").eq("creado_por", u_log).order("id", desc=True).execute()

    users = res_users.data
    nuevo_creado = session.get("last_user_created")
    bloque_nuevo = ""

    if nuevo_creado:
        texto_copiar = f"URL: {nuevo_creado['url']}\\nUSUARIO: {nuevo_creado['user']}\\nCLAVE: {nuevo_creado['pass']}\\nROL: {nuevo_creado['rol']}"
        bloque_nuevo = f'''
        <div class="bg-[#064e3b]/30 border border-[#10b981]/50 rounded-2xl p-5 mb-6 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <p class="text-[10px] uppercase text-emerald-400 font-bold mb-4 tracking-widest flex items-center gap-2">
                <span>✅</span> Nuevo acceso generado
            </p>
            <div class="space-y-3 text-xs text-gray-300 font-mono bg-black/40 p-4 rounded-xl">
                <p><span class="text-cyan-500 font-bold">URL:</span> {nuevo_creado["url"]}</p>
                <p><span class="text-cyan-500 font-bold">USUARIO:</span> {nuevo_creado["user"]}</p>
                <p><span class="text-cyan-500 font-bold">CLAVE:</span> {nuevo_creado["pass"]}</p>
                <p><span class="text-cyan-500 font-bold">ROL:</span> {nuevo_creado["rol"]}</p>
            </div>
            <button onclick="copyText(`{texto_copiar}`)" class="w-full mt-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl py-3 text-[10px] uppercase font-bold tracking-widest transition shadow-lg">
                Copiar acceso
            </button>
        </div>
        '''
        session.pop("last_user_created", None)

    lista = ""
    for u in users:
        if u["rol"] == "operador": continue
        btn_eliminar = ""
        if u["user"] not in ["jhorny", "DRAKITO_VIP7020"]:
            btn_eliminar = f"""
            <form method="POST" onsubmit="return confirm('¿Seguro que deseas eliminar a {u['user']}?');" class="mt-4">
                <input type="hidden" name="action" value="eliminar_usuario">
                <input type="hidden" name="target" value="{u['user']}">
                <button class="w-full bg-[#7f1d1d]/40 text-red-400 border border-red-500/30 rounded-xl py-2.5 text-[10px] font-bold uppercase tracking-widest hover:bg-[#7f1d1d]/60 transition">
                    Eliminar Usuario
                </button>
            </form>
            """
        lista += f"""
        <div class="p-5 bg-[#0b111a] rounded-[20px] border border-[#1e293b] mb-4 shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <div>
                    <span class="text-white font-bold text-base">{u["user"]}</span>
                    <span class="text-gray-500 text-[10px] ml-2 uppercase tracking-widest">({u["rol"]})</span>
                </div>
                <span class="text-cyan-400 font-black text-lg">{u["creditos"]} Cr.</span>
            </div>
            <div class="grid grid-cols-3 gap-2 mb-2">
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="1"><button class="w-full bg-[#111a26] text-cyan-400 border border-[#1e293b] rounded-xl py-2.5 text-xs font-bold">+1</button></form>
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="5"><button class="w-full bg-[#111a26] text-cyan-400 border border-[#1e293b] rounded-xl py-2.5 text-xs font-bold">+5</button></form>
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="10"><button class="w-full bg-[#111a26] text-cyan-400 border border-[#1e293b] rounded-xl py-2.5 text-xs font-bold">+10</button></form>
            </div>
            <div class="grid grid-cols-3 gap-2">
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="-1"><button class="w-full bg-[#3f0f15] text-red-400 border border-[#451515] rounded-xl py-2.5 text-xs font-bold">-1</button></form>
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="-5"><button class="w-full bg-[#3f0f15] text-red-400 border border-[#451515] rounded-xl py-2.5 text-xs font-bold">-5</button></form>
                <form method="POST"><input type="hidden" name="action" value="sumar_rapido"><input type="hidden" name="target" value="{u["user"]}"><input type="hidden" name="cant" value="-10"><button class="w-full bg-[#3f0f15] text-red-400 border border-[#451515] rounded-xl py-2.5 text-xs font-bold">-10</button></form>
            </div>
            {btn_eliminar}
        </div>
        """

    content = f"""
    {bloque_nuevo}
    <div class="neon-card p-6 mt-4 mb-6">
        <h2 class="text-[13px] text-cyan-400 font-bold uppercase text-center mb-8 tracking-[0.2em]">Panel de Control</h2>
        <form method="POST" class="space-y-4 mb-10 border-b border-[#1e293b] pb-8">
            <input type="hidden" name="action" value="crear">
            <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1">Crear Usuario</p>
            <input name="u" placeholder="Usuario Nuevo" class="input-dark" required>
            <input name="p" placeholder="Contraseña" class="input-dark" required>
            <select name="r" class="input-dark appearance-none">
                <option value="user">Cliente</option>
                {"<option value='admin'>Admin Secundario</option>" if is_super_admin() else ""}
            </select>
            <button class="w-full bg-gradient-to-r from-cyan-500 to-blue-600 p-4 rounded-xl font-bold text-xs uppercase tracking-widest text-white shadow-lg mt-2">Registrar</button>
        </form>
        <form method="POST" class="space-y-4 mb-10 border-b border-[#1e293b] pb-8">
            <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1">Modificar Saldo</p>
            <input name="target" placeholder="Usuario Destino" class="input-dark" required>
            <input name="cant" type="number" min="1" placeholder="Cantidad" class="input-dark" required>
            <div class="grid grid-cols-2 gap-3 mt-2">
                <button type="submit" name="action" value="creditos" class="w-full bg-gradient-to-r from-emerald-500 to-teal-400 p-4 rounded-xl font-bold text-xs uppercase tracking-widest text-white shadow-lg">Sumar</button>
                <button type="submit" name="action" value="quitar_creditos" class="w-full bg-gradient-to-r from-rose-500 to-red-600 p-4 rounded-xl font-bold text-xs uppercase tracking-widest text-white shadow-lg">Quitar</button>
            </div>
        </form>
        <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1 mb-4">Lista de Usuarios</p>
        <div class="max-h-[500px] overflow-y-auto pr-1">{lista or "<p class='text-center text-gray-600 text-sm py-8'>Sin usuarios</p>"}</div>
    </div>
    """
    return layout(content, True)


@app.route("/bloqueo", methods=["GET", "POST"])
def bloqueo():
    if not require_login() or not can_use_client_features():
        return redirect("/")
    msg = ""
    if request.method == "POST":
        cliente = session.get("user")
        referencia = request.form.get("num", "").strip()
        res_u = supabase.table("usuarios").select("creditos").eq("user", cliente).execute()
        if res_u.data and res_u.data[0]["creditos"] >= 1:
            supabase.table("usuarios").update({"creditos": res_u.data[0]["creditos"] - 1}).eq("user", cliente).execute()
            supabase.table("pedidos").insert({
                "cliente": cliente, "referencia": referencia, "estado": "PENDIENTE", "tipo": "bloqueo", "respuesta": "", "detalle": "", "codigo": "", "operador": ""
            }).execute()
            msg = "<p class='text-emerald-400 text-xs text-center font-bold mb-4 bg-emerald-900/30 p-3 rounded-xl uppercase tracking-widest'>¡Solicitud enviada!</p>"
        else:
            msg = "<p class='text-red-400 text-xs text-center font-bold mb-4 bg-red-900/30 p-3 rounded-xl uppercase tracking-widest'>Saldo insuficiente</p>"
    content = f"""
    <div class="neon-card p-6 mt-10 text-center">
        <h2 class="text-[13px] text-cyan-400 font-bold mb-8 uppercase tracking-[0.2em]">Solicitar Bloqueo</h2>
        {msg}
        <form action="/bloqueo" method="POST" class="space-y-5">
            <div class="bg-[#111a26] p-5 rounded-2xl border border-[#1e293b]">
                <input type="text" name="num" placeholder="Número, línea o referencia" maxlength="40" class="bg-transparent w-full text-center text-xl font-mono text-white outline-none placeholder-gray-600" required>
            </div>
            <button class="w-full bg-[#ef4444] p-4 rounded-xl font-bold text-xs uppercase tracking-widest text-white shadow-[0_0_15px_rgba(239,68,68,0.4)] mt-2 hover:bg-[#dc2626] transition">Enviar Solicitud</button>
        </form>
    </div>
    """
    return layout(content, True)


@app.route("/bancas", methods=["GET", "POST"])
def bancas():
    if not require_login() or not can_use_client_features():
        return redirect("/")
    msg = ""
    if request.method == "POST":
        cliente = session.get("user")
        banco = request.form.get("banco", "").strip()
        metodo = request.form.get("metodo", "").strip()
        dato = request.form.get("dato", "").strip()
        costo = 2 
        res_u = supabase.table("usuarios").select("creditos").eq("user", cliente).execute()
        if res_u.data and res_u.data[0]["creditos"] >= costo:
            supabase.table("usuarios").update({"creditos": res_u.data[0]["creditos"] - costo}).eq("user", cliente).execute()
            supabase.table("pedidos").insert({
                "cliente": cliente, "referencia": f"{banco} | {metodo} | {dato}", "estado": "PENDIENTE", "tipo": "banca", "respuesta": "", "detalle": "", "codigo": "", "operador": ""
            }).execute()
            msg = f"<p class='text-emerald-400 text-xs text-center font-bold mb-4 bg-emerald-900/30 p-3 rounded-xl uppercase tracking-widest'>¡{banco} Solicitado!</p>"
        else:
            msg = "<p class='text-red-400 text-xs text-center font-bold mb-4 bg-red-900/30 p-3 rounded-xl uppercase tracking-widest'>Saldo insuficiente</p>"
    content = f"""
    <div class="neon-card p-6 mt-10">
        <h2 class="text-[13px] text-cyan-400 font-bold mb-8 uppercase text-center tracking-[0.2em]">Solicitar Banca</h2>
        {msg}
        <form action="/bancas" method="POST" class="space-y-5">
            <div><p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1 mb-2">Entidad Bancaria</p>
                <select name="banco" class="input-dark appearance-none cursor-pointer" required>
                    <option value="" disabled selected>Selecciona banca...</option>
                    <option value="AGORA">Agora (Costo: 2 Cr.)</option>
                    <option value="BCP">BCP (Costo: 2 Cr.)</option>
                    <option value="IBK">IBK (Costo: 2 Cr.)</option>
                    <option value="YAPE">Yape (Costo: 2 Cr.)</option>
                    <option value="CAJA AREQUIPA">Caja Arequipa (Costo: 2 Cr.)</option>
                </select>
            </div>
            <div><p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1 mb-2">Método de Búsqueda</p>
                <select name="metodo" class="input-dark appearance-none cursor-pointer" required>
                    <option value="" disabled selected>Selecciona método...</option>
                    <option value="DNI">Por DNI</option>
                    <option value="NUMERO">Por Número</option>
                </select>
            </div>
            <div><p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest ml-1 mb-2">Dato a Consultar</p>
                <input type="text" name="dato" placeholder="Ingresa DNI o número" class="input-dark" required>
            </div>
            <button class="w-full bg-[#06b6d4] p-4 rounded-xl font-bold text-xs uppercase tracking-widest text-white shadow-[0_0_15px_rgba(6,182,212,0.4)] mt-4 hover:bg-[#0891b2] transition">Enviar Solicitud</button>
        </form>
    </div>
    """
    return layout(content, True)


@app.route("/gestion")
def gestion():
    if not require_login() or session.get("rol") != "operador":
        return redirect("/")
    res_ps = supabase.table("pedidos").select("*").eq("estado", "PENDIENTE").order("id_pedido", desc=True).execute()
    ps = res_ps.data
    cards = "".join([f"""
        <div class="bg-[#111a26] p-5 rounded-[20px] border border-[#1e293b] mb-4 shadow-sm">
            <div class="flex justify-between items-start mb-4">
                <div class="space-y-1">
                    <p class="text-[9px] text-gray-500 font-bold uppercase tracking-widest">CLIENTE: <span class="text-white">{p["cliente"]}</span></p>
                    <p class="text-[9px] text-cyan-500 font-bold uppercase tracking-widest">TIPO: {(p["tipo"] or "").upper()}</p>
                </div>
                <span class="bg-[#1e293b] text-gray-300 text-[10px] px-3 py-1 rounded-full font-mono">ID: {p["id_pedido"]}</span>
            </div>
            <div class="bg-black/30 p-3 rounded-xl border border-[#1e293b] mb-4"><p class="text-sm font-mono text-white text-center">{p["referencia"] or "SIN DATO"}</p></div>
            <a href="/trabajar/{p["id_pedido"]}" class="block text-center w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-3 rounded-xl text-xs font-bold uppercase tracking-widest shadow-lg hover:opacity-90 transition">AGARRAR PEDIDO</a>
        </div>
        """ for p in ps ])
    return layout(f'<div class="mt-6 mb-8 text-center"><h2 class="text-[13px] text-yellow-500 font-black uppercase tracking-[0.2em]">Bandeja Operador</h2></div><div class="space-y-2">{cards or "<p class=\'text-center text-gray-600 text-sm py-10\'>No hay pedidos pendientes.</p>"}</div>', True)


@app.route("/trabajar/<int:id_p>")
def trabajar(id_p):
    if not require_login() or session.get("rol") != "operador":
        return redirect("/")
    res_p = supabase.table("pedidos").select("*").eq("id_pedido", id_p).execute()
    if not res_p.data: return redirect("/gestion")
    p = res_p.data[0]
    tipo = (p["tipo"] or "").lower()
    if tipo == "bloqueo":
        form_html = f"""<form action="/completar" method="POST" class="space-y-4">
            <input type="hidden" name="id_p" value="{p["id_pedido"]}"><input type="hidden" name="tipo_form" value="bloqueo">
            <input name="nombres" placeholder="👤 NOMBRES" class="input-dark" required><input name="dni" placeholder="💳 DNI" class="input-dark" required><input name="telefono" placeholder="📞 TELEFONO" class="input-dark" required>
            <input name="operador_txt" placeholder="📞 OPERADOR" class="input-dark" required><input name="plan" placeholder="📞 PLAN" class="input-dark" required><input name="equipo" placeholder="📱 EQUIPO" class="input-dark" required>
            <input name="imei" placeholder="📱 IMEI" class="input-dark" required><input name="c_bloq" placeholder="📱 C.BLOQ" class="input-dark" required>
            <div class="grid grid-cols-2 gap-4 mt-6">
                <button type="submit" name="accion" value="exito" class="w-full bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl py-4 text-xs font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(16,185,129,0.3)] transition">ÉXITO</button>
                <button type="submit" name="accion" value="rechazar" class="w-full bg-rose-500 hover:bg-rose-600 text-white rounded-xl py-4 text-xs font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(244,63,94,0.3)] transition">RECHAZAR</button>
            </div></form>"""
    else:
        form_html = f"""<form action="/completar" method="POST" class="space-y-4">
            <input type="hidden" name="id_p" value="{p["id_pedido"]}"><input type="hidden" name="tipo_form" value="banca">
            <textarea name="mensaje_banca" placeholder="Escribe el detalle de la consulta aquí..." class="input-dark h-48 resize-none text-sm leading-relaxed" required></textarea>
            <div class="grid grid-cols-2 gap-4 mt-6">
                <button type="submit" name="accion" value="exito" class="w-full bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl py-4 text-xs font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(16,185,129,0.3)] transition">ÉXITO</button>
                <button type="submit" name="accion" value="rechazar" class="w-full bg-rose-500 hover:bg-rose-600 text-white rounded-xl py-4 text-xs font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(244,63,94,0.3)] transition">RECHAZAR</button>
            </div></form>"""
    content = f"""<div class="neon-card p-6 mt-6 shadow-2xl border-cyan-900/30"><h2 class="text-center text-[12px] text-cyan-400 font-bold mb-6 uppercase tracking-[0.2em]">Responder Solicitud</h2>
        <div class="bg-[#111a26] p-4 rounded-xl mb-8 border border-[#1e293b]">
            <div class="flex justify-between items-center mb-2"><p class="text-[9px] text-gray-500 uppercase font-bold tracking-widest">CLIENTE:</p><p class="text-[10px] text-white font-bold">{p["cliente"]}</p></div>
            <div class="flex justify-between items-center mb-4"><p class="text-[9px] text-gray-500 uppercase font-bold tracking-widest">TIPO:</p><p class="text-[10px] text-cyan-400 font-bold">{(p["tipo"] or "").upper()}</p></div>
            <div class="bg-black/40 p-3 rounded-lg border border-[#1e293b]"><p class="text-xs font-mono text-center text-white">{p["referencia"] or "Sin dato"}</p></div>
        </div> {form_html} </div>"""
    return layout(content, True)


@app.route("/completar", methods=["POST"])
def completar():
    if not require_login() or session.get("rol") != "operador": return redirect("/")
    id_p = request.form.get("id_p")
    tipo_form = request.form.get("tipo_form", "").strip().lower()
    accion = request.form.get("accion")
    if accion == "rechazar":
        supabase.table("pedidos").update({"estado": "RECHAZADO", "operador": session.get("user", "")}).eq("id_pedido", id_p).execute()
        res_p = supabase.table("pedidos").select("cliente", "tipo").eq("id_pedido", id_p).execute()
        if res_p.data:
            c = res_p.data[0]["cliente"]
            tipo_p = (res_p.data[0]["tipo"] or "").upper()
            reembolso = 2 if tipo_p in ["AGORA", "YAPE", "BCP", "IBK", "CAJA AREQUIPA", "BANCA"] else 1
            res_u = supabase.table("usuarios").select("creditos").eq("user", c).execute()
            if res_u.data: supabase.table("usuarios").update({"creditos": res_u.data[0]["creditos"] + reembolso}).eq("user", c).execute()
    elif accion == "exito":
        if tipo_form == "bloqueo":
            n, d, t, o, p, e, im, cb = request.form.get("nombres"), request.form.get("dni"), request.form.get("telefono"), request.form.get("operador_txt"), request.form.get("plan"), request.form.get("equipo"), request.form.get("imei"), request.form.get("c_bloq")
            detalle_final = f"👤 𝗡𝗢𝗠𝗕𝗥𝗘𝗦 ➟ {n}\n💳 𝗗𝗡𝗜 ➟ {d}\n📞 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗢 ➟ {t}\n📞 𝗢𝗣𝗘𝗥𝗔𝗗𝗢𝗥 ➟ {o}\n📞 𝗣𝗟𝗔𝗡 ➟ {p}\n📱 𝗘𝗤𝗨𝗜𝗣𝗢 ➟ {e}\n📱 𝗜𝗠𝗘𝗜 ➟ {im}\n📱 𝗖.𝗕𝗟𝗢𝗤 ➟ {cb}"
            supabase.table("pedidos").update({"respuesta": "BLOQUEADO EXITOSAMENTE", "detalle": detalle_final, "codigo": cb, "operador": session.get("user", ""), "estado": "EXITOSO"}).eq("id_pedido", id_p).execute()
        else:
            msg_b = request.form.get("mensaje_banca", "").strip()
            supabase.table("pedidos").update({"respuesta": "OPERACIÓN EXITOSA", "detalle": msg_b, "codigo": "", "operador": session.get("user", ""), "estado": "EXITOSO"}).eq("id_pedido", id_p).execute()
    return redirect("/gestion")


@app.route("/soporte")
def soporte():
    if not require_login(): return redirect("/login")
    content = """<div class="neon-card p-8 mt-6 text-center"><h2 class="text-3xl font-black text-white mb-4 tracking-tight">¿Necesitas ayuda?</h2><p class="text-gray-400 text-sm mb-8 leading-relaxed">Estamos aquí para apoyarte en todo momento.</p>
        <div class="bg-[#111a26] rounded-[20px] p-6 border-l-4 border-cyan-500 text-left mb-10 shadow-sm">
            <p class="text-white text-sm leading-relaxed mb-6"><span class="text-cyan-400 font-bold">💬 ¿Deseas ayuda con alguna consulta?</span><br><span class="text-gray-400">Contáctanos para brindarte soporte de manera inmediata.</span></p>
            <p class="text-white text-sm leading-relaxed"><span class="text-rose-400 font-bold">⚠️ ¿Error con alguna de tus búsquedas?</span><br><span class="text-gray-400">Nuestro soporte está disponible las 24 horas para ayudarte.</span></p>
        </div>
        <div class="text-center"><a href="https://t.me/DRAKO1X" target="_blank" class="inline-block bg-[#0f172a] text-cyan-400 border border-[#1e293b] rounded-full py-4 px-12 text-sm uppercase font-bold tracking-widest shadow-lg hover:bg-[#1e293b] transition">Contactar</a><p class="text-gray-500 text-xs mt-6 uppercase tracking-widest font-bold">Soporte disponible 24/7</p></div></div>"""
    return layout(content, True)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
