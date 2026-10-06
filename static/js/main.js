// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {

    // ── Inicializar tooltips de Bootstrap ─────────────────────
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ── Auto-cerrar alertas flash después de 5 segundos ───────
    // (complementa la animación CSS del styles.css)
    setTimeout(function () {
        document.querySelectorAll('.messages .alert').forEach(function (alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        });
    }, 5000);

    // ── Abrir el detalle al hacer clic en una fila ────────────
    // Uso: <tr class="fila-link" data-href="{% url 'encomienda_detalle' enc.pk %}">
    document.querySelectorAll('.fila-link').forEach(function (fila) {
        fila.addEventListener('click', function (e) {
            if (e.target.closest('a, button')) return;   // no interferir con enlaces
            window.location = this.dataset.href;
        });
    });

    // ── Barras del dashboard: ancho según el porcentaje ───────
    // Uso: <div class="barra-relleno" data-porcentaje="40"></div>
    document.querySelectorAll('[data-porcentaje]').forEach(function (barra) {
        barra.style.width = barra.dataset.porcentaje + '%';
    });

    // ── Validación client-side de formularios Bootstrap ───────
    document.querySelectorAll('form.needs-validation').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// ── Confirmación antes de eliminar ────────────────────────────
// Uso: <button onclick="return confirmar('¿Eliminar este registro?')">Eliminar</button>
window.confirmar = function (mensaje) {
    return confirm(mensaje || '¿Estás seguro?');
};