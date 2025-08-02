from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
import psycopg2
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
from config import CONNECTION_STRING
from datetime import datetime
import calendar

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():
    conn = psycopg2.connect(CONNECTION_STRING)
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/categorias")
def listar_categorias():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre;")
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("categorias/listar.html", categorias=categorias)


@app.route("/categorias/nuevo", methods=["GET", "POST"])
def crear_categoria():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form.get("descripcion", "")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s);",
            (nombre, descripcion),
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Categoría creada exitosamente.", "success")
        return redirect(url_for("listar_categorias"))

    return render_template("categorias/nuevo.html")


@app.route("/categorias/editar/<int:id>", methods=["GET", "POST"])
def editar_categoria(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form.get("descripcion", "")

        cur.execute(
            "UPDATE categorias SET nombre=%s, descripcion=%s WHERE id=%s;",
            (nombre, descripcion, id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Categoría actualizada.", "success")
        return redirect(url_for("listar_categorias"))

    cur.execute("SELECT id, nombre, descripcion FROM categorias WHERE id=%s;", (id,))
    categoria = cur.fetchone()
    cur.close()
    conn.close()

    if categoria is None:
        flash("Categoría no encontrada.", "danger")
        return redirect(url_for("listar_categorias"))

    return render_template("categorias/editar.html", categoria=categoria)


@app.route("/categorias/eliminar/<int:id>", methods=["POST"])
def eliminar_categoria(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM categorias WHERE id=%s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Categoría eliminada.", "info")
    return redirect(url_for("listar_categorias"))


# ----------------------------------------
# Rutas CRUD para Etiquetas
# ----------------------------------------
@app.route("/etiquetas")
def listar_etiquetas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM etiquetas ORDER BY nombre;")
    etiquetas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("etiquetas/listar.html", etiquetas=etiquetas)


@app.route("/etiquetas/nuevo", methods=["GET", "POST"])
def crear_etiqueta():
    if request.method == "POST":
        nombre = request.form["nombre"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO etiquetas (nombre) VALUES (%s);", (nombre,))
        conn.commit()
        cur.close()
        conn.close()

        flash("Etiqueta creada exitosamente.", "success")
        return redirect(url_for("listar_etiquetas"))

    return render_template("etiquetas/nuevo.html")


@app.route("/etiquetas/editar/<int:id>", methods=["GET", "POST"])
def editar_etiqueta(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]

        cur.execute("UPDATE etiquetas SET nombre=%s WHERE id=%s;", (nombre, id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Etiqueta actualizada.", "success")
        return redirect(url_for("listar_etiquetas"))

    cur.execute("SELECT id, nombre FROM etiquetas WHERE id=%s;", (id,))
    etiqueta = cur.fetchone()
    cur.close()
    conn.close()

    if etiqueta is None:
        flash("Etiqueta no encontrada.", "danger")
        return redirect(url_for("listar_etiquetas"))

    return render_template("etiquetas/editar.html", etiqueta=etiqueta)


@app.route("/etiquetas/eliminar/<int:id>", methods=["POST"])
def eliminar_etiqueta(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM etiquetas WHERE id=%s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Etiqueta eliminada.", "info")
    return redirect(url_for("listar_etiquetas"))


# ----------------------------------------
# Rutas CRUD para Gastos
# ----------------------------------------
@app.route("/gastos")
def listar_gastos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.id, g.fecha, c.nombre AS categoria, g.descripcion, g.monto
        FROM gastos g
        LEFT JOIN categorias c ON g.id_categoria = c.id
        ORDER BY g.fecha DESC;
        """
    )
    gastos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("gastos/listar.html", gastos=gastos)


@app.route("/gastos/nuevo", methods=["GET", "POST"])
def crear_gasto():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre;")
    categorias = cur.fetchall()

    if request.method == "POST":
        id_categoria = request.form.get("categoria") or None
        descripcion = request.form.get("descripcion", "")
        monto = request.form["monto"]
        fecha = request.form.get("fecha") or None

        if fecha:
            cur.execute(
                "INSERT INTO gastos (id_categoria, descripcion, monto, fecha) VALUES (%s, %s, %s, %s);",
                (id_categoria, descripcion, monto, fecha),
            )
        else:
            cur.execute(
                "INSERT INTO gastos (id_categoria, descripcion, monto) VALUES (%s, %s, %s);",
                (id_categoria, descripcion, monto),
            )
        conn.commit()
        cur.close()
        conn.close()
        flash("Gasto agregado correctamente.", "success")
        return redirect(url_for("listar_gastos"))

    cur.close()
    conn.close()
    return render_template("gastos/nuevo.html", categorias=categorias)


@app.route("/gastos/editar/<int:id>", methods=["GET", "POST"])
def editar_gasto(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        id_categoria = request.form.get("categoria") or None
        descripcion = request.form.get("descripcion", "")
        monto = request.form["monto"]
        fecha = request.form["fecha"]

        cur.execute(
            "UPDATE gastos SET id_categoria=%s, descripcion=%s, monto=%s, fecha=%s WHERE id=%s;",
            (id_categoria, descripcion, monto, fecha, id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Gasto actualizado correctamente.", "success")
        return redirect(url_for("listar_gastos"))

    cur.execute("SELECT id, id_categoria, descripcion, monto, fecha FROM gastos WHERE id=%s;", (id,))
    gasto = cur.fetchone()

    cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre;")
    categorias = cur.fetchall()

    cur.close()
    conn.close()

    if gasto is None:
        flash("No se encontró el gasto.", "danger")
        return redirect(url_for("listar_gastos"))

    return render_template("gastos/editar.html", gasto=gasto, categorias=categorias)


@app.route("/gastos/eliminar/<int:id>", methods=["POST"])
def eliminar_gasto(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM gastos WHERE id=%s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Gasto eliminado.", "info")
    return redirect(url_for("listar_gastos"))


# ----------------------------------------
# Rutas CRUD para Ingresos
# ----------------------------------------
@app.route("/ingresos")
def listar_ingresos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, fecha, descripcion, monto FROM ingresos ORDER BY fecha DESC;")
    ingresos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("ingresos/listar.html", ingresos=ingresos)


@app.route("/ingresos/nuevo", methods=["GET", "POST"])
def crear_ingreso():
    if request.method == "POST":
        descripcion = request.form.get("descripcion", "")
        monto = request.form["monto"]
        fecha = request.form.get("fecha") or None

        conn = get_db_connection()
        cur = conn.cursor()
        if fecha:
            cur.execute(
                "INSERT INTO ingresos (descripcion, monto, fecha) VALUES (%s, %s, %s);",
                (descripcion, monto, fecha),
            )
        else:
            cur.execute(
                "INSERT INTO ingresos (descripcion, monto) VALUES (%s, %s);",
                (descripcion, monto),
            )
        conn.commit()
        cur.close()
        conn.close()
        flash("Ingreso agregado correctamente.", "success")
        return redirect(url_for("listar_ingresos"))

    return render_template("ingresos/nuevo.html")


@app.route("/ingresos/editar/<int:id>", methods=["GET", "POST"])
def editar_ingreso(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        descripcion = request.form.get("descripcion", "")
        monto = request.form["monto"]
        fecha = request.form["fecha"]

        cur.execute(
            "UPDATE ingresos SET descripcion=%s, monto=%s, fecha=%s WHERE id=%s;",
            (descripcion, monto, fecha, id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Ingreso actualizado correctamente.", "success")
        return redirect(url_for("listar_ingresos"))

    cur.execute("SELECT id, descripcion, monto, fecha FROM ingresos WHERE id=%s;", (id,))
    ingreso = cur.fetchone()
    cur.close()
    conn.close()

    if ingreso is None:
        flash("No se encontró el ingreso.", "danger")
        return redirect(url_for("listar_ingresos"))

    return render_template("ingresos/editar.html", ingreso=ingreso)


@app.route("/ingresos/eliminar/<int:id>", methods=["POST"])
def eliminar_ingreso(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ingresos WHERE id=%s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Ingreso eliminado.", "info")
    return redirect(url_for("listar_ingresos"))


# ----------------------------------------
# Rutas CRUD para Presupuestos
# ----------------------------------------
@app.route("/presupuestos")
def listar_presupuestos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.id, c.nombre AS categoria, p.monto_limite, p.mes, p.anio
        FROM presupuestos p
        JOIN categorias c ON p.id_categoria = c.id
        ORDER BY p.anio DESC, p.mes DESC, c.nombre;
        """
    )
    presupuestos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("presupuestos/listar.html", presupuestos=presupuestos)


@app.route("/presupuestos/nuevo", methods=["GET", "POST"])
def crear_presupuesto():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre;")
    categorias = cur.fetchall()

    if request.method == "POST":
        id_categoria = request.form["categoria"]
        monto_limite = request.form["monto_limite"]
        mes = request.form["mes"]
        anio = request.form["anio"]

        cur.execute(
            "INSERT INTO presupuestos (id_categoria, monto_limite, mes, anio) VALUES (%s, %s, %s, %s);",
            (id_categoria, monto_limite, mes, anio),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Presupuesto creado correctamente.", "success")
        return redirect(url_for("listar_presupuestos"))

    cur.close()
    conn.close()
    return render_template("presupuestos/nuevo.html", categorias=categorias)


@app.route("/presupuestos/editar/<int:id>", methods=["GET", "POST"])
def editar_presupuesto(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        id_categoria = request.form["categoria"]
        monto_limite = request.form["monto_limite"]
        mes = request.form["mes"]
        anio = request.form["anio"]

        cur.execute(
            "UPDATE presupuestos SET id_categoria=%s, monto_limite=%s, mes=%s, anio=%s WHERE id=%s;",
            (id_categoria, monto_limite, mes, anio, id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Presupuesto actualizado correctamente.", "success")
        return redirect(url_for("listar_presupuestos"))

    cur.execute("SELECT id, id_categoria, monto_limite, mes, anio FROM presupuestos WHERE id=%s;", (id,))
    presupuesto = cur.fetchone()

    cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre;")
    categorias = cur.fetchall()

    cur.close()
    conn.close()

    if presupuesto is None:
        flash("No se encontró el presupuesto.", "danger")
        return redirect(url_for("listar_presupuestos"))

    return render_template("presupuestos/editar.html", presupuesto=presupuesto, categorias=categorias)


@app.route("/presupuestos/eliminar/<int:id>", methods=["POST"])
def eliminar_presupuesto(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM presupuestos WHERE id=%s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Presupuesto eliminado.", "info")
    return redirect(url_for("listar_presupuestos"))


# ----------------------------------------
# Rutas CRUD para Archivos Adjuntos
# ----------------------------------------
@app.route("/archivos/")
@app.route("/archivos/<int:gasto_id>")
def listar_archivos(gasto_id):
    """
    Lista los archivos adjuntos de un gasto específico.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre_archivo, ruta_archivo FROM archivos WHERE id_gasto=%s ORDER BY id;",
        (gasto_id,),
    )
    archivos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("archivos/listar.html", archivos=archivos, gasto_id=gasto_id)

@app.route("/archivos/subir/<int:gasto_id>", methods=["GET", "POST"])
def subir_archivo(gasto_id):
    """
    Permite subir un archivo y registrar su ruta en la base de datos.
    """
    if request.method == "POST":
        if "archivo" not in request.files:
            flash("No se seleccionó ningún archivo.", "danger")
            return redirect(request.url)

        file = request.files["archivo"]
        if file.filename == "":
            flash("No se seleccionó ningún archivo.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Guardar en UPLOAD_FOLDER usando el id del gasto como subcarpeta
            gasto_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(gasto_id))
            os.makedirs(gasto_folder, exist_ok=True)
            filepath = os.path.join(gasto_folder, filename)
            file.save(filepath)

            # Registrar en la base de datos
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO archivos (id_gasto, nombre_archivo, ruta_archivo) VALUES (%s, %s, %s);",
                (gasto_id, filename, filepath),
            )
            conn.commit()
            cur.close()
            conn.close()

            flash("Archivo subido correctamente.", "success")
            return redirect(url_for("listar_archivos", gasto_id=gasto_id))
        else:
            flash("Extensión de archivo no permitida.", "danger")
            return redirect(request.url)

    return render_template("archivos/subir.html", gasto_id=gasto_id)


@app.route("/archivos/eliminar/<int:id>/<int:gasto_id>", methods=["POST"])
def eliminar_archivo(id, gasto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ruta_archivo FROM archivos WHERE id=%s;", (id,))
    resultado = cur.fetchone()

    if resultado:
        ruta_archivo = resultado[0]
        try:
            os.remove(ruta_archivo)
        except FileNotFoundError:
            flash("Archivo físico no encontrado, pero se eliminará el registro.", "warning")
        except Exception as e:
            flash(f"Error al eliminar el archivo: {e}", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("listar_archivos", gasto_id=gasto_id))

        cur.execute("DELETE FROM archivos WHERE id=%s;", (id,))
        conn.commit()
        flash("Archivo eliminado correctamente.", "info")
    else:
        flash("Archivo no encontrado.", "danger")

    cur.close()
    conn.close()
    return redirect(url_for("listar_archivos", gasto_id=gasto_id))


# ----------------------------------------
# Ruta para servir archivos subidos (descarga)
# ----------------------------------------
@app.route("/uploads/<int:gasto_id>/<filename>")
def descargar_archivo(gasto_id, filename):
    folder = os.path.join(app.config["UPLOAD_FOLDER"], str(gasto_id))
    return send_from_directory(folder, filename)

def login_required(f):
    """
    Decorador que redirige al login si el usuario no ha iniciado sesión.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión primero.", "warning")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


# ----------------------------------------
# Rutas de Autenticación
# ----------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    """
    Página de login en la raíz. Si ya está logueado, redirige al dashboard.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, contraseña FROM login WHERE username = %s;",
            (username,),
        )
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if usuario:
            user_id, hash_almacenado = usuario
            # Comparamos hash usando werkzeug.security
            if check_password_hash(hash_almacenado, password):
                session.clear()
                session["user_id"] = user_id
                flash("Autenticación exitosa.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Contraseña incorrecta.", "danger")
        else:
            flash("Usuario no existe.", "warning")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Ruta de registro de nuevos usuarios.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # 1) Verificar que username, password y confirmación no estén vacíos
        if not username or not password or not password_confirm:
            flash("Por favor completa todos los campos.", "warning")
            return redirect(url_for("register"))

        # 2) Verificar que las contraseñas coincidan
        if password != password_confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cur = conn.cursor()
        # 3) Verificar si el usuario ya existe
        cur.execute("SELECT id FROM login WHERE username = %s;", (username,))
        existente = cur.fetchone()
        if existente:
            cur.close()
            conn.close()
            flash("El nombre de usuario ya está en uso.", "warning")
            return redirect(url_for("register"))

        # 4) Insertar nuevo usuario con hash de contraseña
        hash_pw = generate_password_hash(password)
        cur.execute(
            "INSERT INTO login (username, contraseña) VALUES (%s, %s);",
            (username, hash_pw),
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/auth/logout")
@login_required
def logout():
    """
    Elimina la sesión del usuario y redirige al login.
    """
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("home"))

# ----------------------------------------
# Dashboard
# ----------------------------------------
@app.route("/dashboard/data")
def dashboard_data():
    inicio = request.args.get("inicio")
    fin = request.args.get("fin")

    filtro_fecha = ""
    valores = ()

    if inicio and fin:
        try:
            fecha_ini = datetime.strptime(inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fin, "%Y-%m-%d").date()
            filtro_fecha = "WHERE fecha BETWEEN %s AND %s"
            valores = (fecha_ini, fecha_fin)
        except ValueError:
            pass  # Ignora si las fechas no son válidas

    conn = get_db_connection()
    cur = conn.cursor()

    # Ingresos últimos 6 meses
    cur.execute(f"""
        SELECT TO_CHAR(fecha, 'YYYY-MM') as mes, SUM(monto)
        FROM ingresos {filtro_fecha}
        GROUP BY mes ORDER BY mes DESC LIMIT 6
    """, valores)
    ingresos = dict(cur.fetchall())

    # Gastos últimos 6 meses
    cur.execute(f"""
        SELECT TO_CHAR(fecha, 'YYYY-MM') as mes, SUM(monto)
        FROM gastos {filtro_fecha}
        GROUP BY mes ORDER BY mes DESC LIMIT 6
    """, valores)
    gastos = dict(cur.fetchall())

    # Fechas combinadas para labels
    meses = sorted(set(ingresos.keys()) | set(gastos.keys()))

    # Gastos por categoría
    cur.execute(f"""
        SELECT c.nombre, SUM(g.monto)
        FROM gastos g
        JOIN categorias c ON g.id_categoria = c.id
        {filtro_fecha.replace('fecha', 'g.fecha') if filtro_fecha else ''}
        GROUP BY c.nombre
    """, valores)
    categorias = [{"nombre": nombre, "total": float(total)} for nombre, total in cur.fetchall()]

    # Presupuesto vs Gasto por Categoría (solo mes actual)
    cur.execute("""
        SELECT 
            c.nombre AS categoria,
            COALESCE(SUM(p.monto_limite), 0) AS presupuesto,
            COALESCE(SUM(g.monto), 0) AS gasto
        FROM categorias c
        LEFT JOIN presupuestos p ON c.id = p.id_categoria
            AND p.mes = EXTRACT(MONTH FROM CURRENT_DATE)
            AND p.anio = EXTRACT(YEAR FROM CURRENT_DATE)
        LEFT JOIN gastos g ON g.id_categoria = c.id
            AND EXTRACT(MONTH FROM g.fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM g.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY c.nombre
    """)
    presupuesto_vs_gasto = [
        {"categoria": row[0], "presupuesto": float(row[1]), "gasto": float(row[2])}
        for row in cur.fetchall()
    ]

    # Último ingreso
    cur.execute("SELECT descripcion, monto, fecha FROM ingresos ORDER BY fecha DESC LIMIT 1")
    ingreso = cur.fetchone()
    ultimo_ingreso = f"{ingreso[0]} (S/{ingreso[1]}) - {ingreso[2]}" if ingreso else None

    # Último gasto
    cur.execute("SELECT descripcion, monto, fecha FROM gastos ORDER BY fecha DESC LIMIT 1")
    gasto = cur.fetchone()
    ultimo_gasto = f"{gasto[0]} (S/{gasto[1]}) - {gasto[2]}" if gasto else None

    # Último presupuesto
    cur.execute("""
        SELECT c.nombre, p.monto_limite, p.mes, p.anio
        FROM presupuestos p
        JOIN categorias c ON p.id_categoria = c.id
        ORDER BY p.anio DESC, p.mes DESC, p.id DESC
        LIMIT 1
    """)
    pres = cur.fetchone()
    ultimo_presupuesto = f"{pres[0]}: S/{pres[1]} ({pres[2]}/{pres[3]})" if pres else None

    # Presupuesto total asignado (sumatoria completa)
    cur.execute("SELECT COALESCE(SUM(monto_limite), 0) FROM presupuestos")
    presupuesto_total_asignado = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        "labels": meses,
        "ingresos": [float(ingresos.get(m, 0)) for m in meses],
        "gastos": [float(gastos.get(m, 0)) for m in meses],
        "categorias": categorias,
        "presupuesto_vs_gasto": presupuesto_vs_gasto,
        "ultimo_ingreso": ultimo_ingreso,
        "ultimo_gasto": ultimo_gasto,
        "ultimo_presupuesto": ultimo_presupuesto,
        "presupuesto_total_asignado": float(presupuesto_total_asignado)
    })

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
