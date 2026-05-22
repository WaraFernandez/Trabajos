let currentField = null;
let currentElementId = null;
let currentPublicacionId = null;
let editPubId = null;
let editFotoId = null;
let selectedFile = null;

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========== DESCRIPCIÓN PERSONAL ==========
function abrirModalEditarDescripcion() {
    let descripcionActual = document.getElementById('descripcionText').innerText;
    if (descripcionActual.includes('No has agregado una descripción personal')) {
        descripcionActual = '';
    }
    document.getElementById('descripcionInput').value = descripcionActual;
    document.getElementById('modalDescripcion').style.display = 'flex';
}

function cerrarModalDescripcion() {
    document.getElementById('modalDescripcion').style.display = 'none';
}

function guardarDescripcion() {
    const nuevaDescripcion = document.getElementById('descripcionInput').value.trim();

    fetch('/perfil/editar-campo/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `campo=descripcion_personal&valor=${encodeURIComponent(nuevaDescripcion)}`
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                if (nuevaDescripcion) {
                    document.getElementById('descripcionText').innerHTML = nuevaDescripcion.replace(/\n/g, '<br>');
                } else {
                    document.getElementById('descripcionText').innerHTML = '<span style="color: #9CA3AF;">No has agregado una descripción personal.</span>';
                }
                cerrarModalDescripcion();
                showToast('✅ Descripción actualizada correctamente');
            } else {
                showToast('❌ Error al guardar la descripción', 'error');
            }
        })
        .catch(error => {
            showToast('❌ Error de conexión', 'error');
        });
}

// ========== PORTAFOLIO ==========
const fileInput = document.getElementById('portafolioImagen');
const btnSubir = document.getElementById('btnSubirPortafolio');
const tituloInput = document.getElementById('portafolioTitulo');
const descripcionInput = document.getElementById('portafolioDescripcion');
const previewDiv = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const previewFileName = document.getElementById('previewFileName');
const spinner = document.getElementById('portafolioSpinner');

fileInput.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (!file) {
        selectedFile = null;
        btnSubir.disabled = true;
        previewDiv.style.display = 'none';
        return;
    }

    if (!file.type.startsWith('image/')) {
        showToast('❌ Por favor selecciona una imagen válida', 'error');
        fileInput.value = '';
        selectedFile = null;
        btnSubir.disabled = true;
        previewDiv.style.display = 'none';
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('❌ La imagen no debe superar los 5MB', 'error');
        fileInput.value = '';
        selectedFile = null;
        btnSubir.disabled = true;
        previewDiv.style.display = 'none';
        return;
    }

    selectedFile = file;
    btnSubir.disabled = false;

    const reader = new FileReader();
    reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewFileName.textContent = file.name;
        previewDiv.style.display = 'flex';
    };
    reader.readAsDataURL(file);
});

btnSubir.addEventListener('click', function () {
    if (!selectedFile) {
        showToast('❌ Selecciona una imagen primero', 'error');
        return;
    }

    const titulo = tituloInput.value;
    const descripcion = descripcionInput.value;
    const formData = new FormData();
    formData.append('imagen', selectedFile);
    formData.append('titulo', titulo);
    formData.append('descripcion', descripcion);
    formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

    spinner.style.display = 'flex';
    btnSubir.disabled = true;
    btnSubir.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';

    fetch('/perfil/subir-portafolio/', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}', 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            if (data.success) {
                showToast('✅ Foto agregada al portafolio', 'success');
                selectedFile = null;
                fileInput.value = '';
                tituloInput.value = '';
                descripcionInput.value = '';
                previewDiv.style.display = 'none';
                btnSubir.disabled = true;
                btnSubir.innerHTML = '<i class="fas fa-upload"></i> Subir foto';
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('❌ Error: ' + (data.error || 'No se pudo subir'), 'error');
                btnSubir.disabled = false;
                btnSubir.innerHTML = '<i class="fas fa-upload"></i> Subir foto';
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            showToast('❌ Error de conexión', 'error');
            btnSubir.disabled = false;
            btnSubir.innerHTML = '<i class="fas fa-upload"></i> Subir foto';
        });
});

function cancelarPreview() {
    selectedFile = null;
    fileInput.value = '';
    previewDiv.style.display = 'none';
    btnSubir.disabled = true;
}

// ========== EDICIÓN DE ESTADO (modal) ==========
function abrirModalEditarPublicacion(pubId) {
    editPubId = pubId;
    const contenidoElement = document.getElementById(`contenido-pub-${pubId}`);
    let contenido = contenidoElement.innerText;
    document.getElementById('editPubContenido').value = contenido;
    const imagenDiv = document.getElementById(`imagen-pub-${pubId}`);
    const previewDiv = document.getElementById('editPubImagenActual');
    if (imagenDiv) {
        previewDiv.innerHTML = `<img src="${imagenDiv.querySelector('img').src}" style="max-width:100%; max-height:150px; border-radius:0.5rem;">`;
    } else {
        previewDiv.innerHTML = '<p style="color:#999;">No hay imagen actual</p>';
    }
    document.getElementById('editPubEliminarImagen').checked = false;
    document.getElementById('modalEditarPublicacion').style.display = 'flex';
}

function cerrarModalEditarPublicacion() {
    document.getElementById('modalEditarPublicacion').style.display = 'none';
    editPubId = null;
}

function guardarEdicionPublicacion() {
    const nuevoContenido = document.getElementById('editPubContenido').value.trim();
    if (!nuevoContenido) {
        alert('El contenido no puede estar vacío');
        return;
    }
    const formData = new FormData();
    formData.append('contenido', nuevoContenido);
    const imagenFile = document.getElementById('editPubImagen').files[0];
    if (imagenFile) formData.append('imagen', imagenFile);
    if (document.getElementById('editPubEliminarImagen').checked) formData.append('eliminar_imagen', 'true');

    fetch(`/publicacion/editar/${editPubId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' },
        body: formData
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showToast('✅ Publicación actualizada');
            setTimeout(() => location.reload(), 500);
        } else {
            alert('Error al guardar cambios');
        }
    });
}

function eliminarPublicacion(pubId) {
    if (confirm('¿Estás seguro de eliminar esta publicación?')) {
        fetch(`/publicacion/eliminar/${pubId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}' }
        }).then(r => r.json()).then(data => {
            if (data.success) {
                document.getElementById(`publicacion-${pubId}`).remove();
                showToast('✅ Publicación eliminada');
            }
        });
    }
}

// ========== EDICIÓN DE PORTAFOLIO ==========
function abrirModalEditarPortafolio(id, titulo, descripcion, imagenUrl) {
    editFotoId = id;
    document.getElementById('editFotoId').value = id;
    document.getElementById('editFotoTitulo').value = titulo;
    document.getElementById('editFotoDescripcion').value = descripcion;
    document.getElementById('editFotoPreview').src = imagenUrl;
    document.getElementById('editFotoImagen').value = '';
    document.getElementById('modalEditarPortafolio').style.display = 'flex';
}

function cerrarModalEditarPortafolio() {
    document.getElementById('modalEditarPortafolio').style.display = 'none';
    editFotoId = null;
}

function guardarEdicionPortafolio() {
    const id = editFotoId;
    const titulo = document.getElementById('editFotoTitulo').value;
    const descripcion = document.getElementById('editFotoDescripcion').value;
    const imagenFile = document.getElementById('editFotoImagen').files[0];
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('descripcion', descripcion);
    if (imagenFile) formData.append('imagen', imagenFile);

    fetch(`/perfil/editar-portafolio/${id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' },
        body: formData
    }).then(r => r.json()).then(data => {
        if (data.success) {
            showToast('✅ Foto actualizada');
            setTimeout(() => location.reload(), 500);
        } else {
            alert('Error al guardar cambios');
        }
    });
}

function eliminarFoto(fotoId) {
    if (confirm('¿Eliminar esta foto del portafolio?')) {
        fetch(`/perfil/eliminar-portafolio/${fotoId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}' }
        }).then(() => location.reload());
    }
}

// ========== EDITAR CAMPO SIMPLE ==========
function abrirModalEditar(field, elementId) {
    currentField = field;
    currentElementId = elementId;
    const currentValue = document.getElementById(elementId).innerText;
    document.getElementById('modalSimpleTitulo').innerHTML = `Editar ${field.replace('_', ' ')}`;
    document.getElementById('modalSimpleInput').value = currentValue;
    document.getElementById('modalSimple').style.display = 'flex';
}

function cerrarModalSimple() {
    document.getElementById('modalSimple').style.display = 'none';
}

function guardarCampoSimple() {
    const newValue = document.getElementById('modalSimpleInput').value;
    fetch('/perfil/editar-campo/', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `campo=${currentField}&valor=${encodeURIComponent(newValue)}`
    }).then(r => r.json()).then(data => {
        if (data.success) {
            document.getElementById(currentElementId).innerText = newValue;
            cerrarModalSimple();
            showToast('✅ Campo actualizado');
        }
    });
}

// ========== EDITAR EXPERIENCIA ==========
function abrirModalEditarExperiencia() {
    const experienciaSpan = document.getElementById('experienciaText');
    let textoExperiencia = experienciaSpan.innerText;
    let años = 0;
    const match = textoExperiencia.match(/(\d+)/);
    if (match) años = parseInt(match[0]);
    document.getElementById('experienciaInput').value = años;
    document.getElementById('modalExperiencia').style.display = 'flex';
}

function cerrarModalExperiencia() {
    document.getElementById('modalExperiencia').style.display = 'none';
}

function guardarExperiencia() {
    const nuevosAños = document.getElementById('experienciaInput').value;
    fetch('/perfil/editar-campo/', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `campo=anios_experiencia&valor=${encodeURIComponent(nuevosAños)}`
    }).then(r => r.json()).then(data => {
        if (data.success) {
            const texto = nuevosAños == 1 ? `${nuevosAños} año` : `${nuevosAños} años`;
            document.getElementById('experienciaText').innerHTML = texto;
            cerrarModalExperiencia();
            showToast('✅ Experiencia actualizada');
            setTimeout(() => location.reload(), 500);
        }
    });
}

// ========== MODAL GENERAL ==========
function abrirModalGeneral() { document.getElementById('modalGeneral').style.display = 'flex'; }
function cerrarModalGeneral() { document.getElementById('modalGeneral').style.display = 'none'; }

// ========== TOGGLE DISPONIBILIDAD ==========
function toggleDisponibilidad() {
    fetch('/perfil/toggle-disponibilidad/', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' }
    }).then(r => r.json()).then(data => {
        if (data.success) {
            const span = document.getElementById('disponibilidadSpan');
            span.innerHTML = data.disponible ? '<i class="fas fa-check-circle"></i> Disponible' : '<i class="fas fa-times-circle"></i> No disponible';
            span.className = data.disponible ? 'disponible' : 'no-disponible';
            showToast(data.disponible ? '✅ Ahora estás disponible' : '❌ Ahora no estás disponible');
        }
    });
}

// ========== LIKE ==========
function toggleLike(pubId) {
    fetch(`/like/${pubId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' }
    }).then(r => r.json()).then(data => {
        const icon = document.getElementById(`like-icon-${pubId}`);
        const count = document.getElementById(`like-count-${pubId}`);
        icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
        count.textContent = data.total_likes;
    });
}

// ========== COMENTARIOS ==========
function abrirModalComentarios(pubId) {
    currentPublicacionId = pubId;
    document.getElementById('modalComentarios').style.display = 'flex';
    cargarComentarios(pubId);
}

function cerrarModalComentarios() {
    document.getElementById('modalComentarios').style.display = 'none';
    currentPublicacionId = null;
}

function cargarComentarios(pubId) {
    fetch(`/comentarios/${pubId}/`).then(r => r.json()).then(data => {
        let html = '';
        data.comentarios.forEach(c => {
            const esPropio = (c.usuario_id == {{ user.id }
        });
        html += `
                        <div class="comentario-item">
                            <div class="comentario-header">
                                <strong>${c.usuario}</strong>
                                <small style="color:#999;">${c.fecha}</small>
                                ${esPropio ? `
                                <div>
                                    <button onclick="editarComentario(${c.id}, '${c.texto.replace(/'/g, "\\'")}')" style="background:none; border:none; cursor:pointer;"><i class="fas fa-edit"></i></button>
                                    <button onclick="eliminarComentario(${c.id})" style="background:none; border:none; cursor:pointer;"><i class="fas fa-trash-alt"></i></button>
                                </div>
                                ` : ''}
                            </div>
                            <p style="margin-top:0.3rem;">${c.texto}</p>
                        </div>
                    `;
    });
    if (!html) html = '<p style="text-align:center;">No hay comentarios aún</p>';
    document.getElementById('listaComentarios').innerHTML = html;
});
        }

function enviarComentario() {
    const texto = document.getElementById('inputComentario').value.trim();
    if (!texto || !currentPublicacionId) return;
    fetch(`/comentar/${currentPublicacionId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `texto=${encodeURIComponent(texto)}`
    }).then(r => r.json()).then(data => {
        if (data.success) {
            document.getElementById('inputComentario').value = '';
            cargarComentarios(currentPublicacionId);
            const count = document.getElementById(`com-count-${currentPublicacionId}`);
            count.textContent = parseInt(count.textContent) + 1;
            showToast('💬 Comentario publicado');
        }
    });
}

function editarComentario(comentarioId, textoActual) {
    const nuevoTexto = prompt('Editar comentario:', textoActual);
    if (nuevoTexto && nuevoTexto.trim()) {
        fetch(`/comentario/editar/${comentarioId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `texto=${encodeURIComponent(nuevoTexto)}`
        }).then(r => r.json()).then(data => {
            if (data.success) {
                cargarComentarios(currentPublicacionId);
                showToast('✅ Comentario editado');
            }
        });
    }
}

function eliminarComentario(comentarioId) {
    if (confirm('¿Eliminar comentario?')) {
        fetch(`/comentario/eliminar/${comentarioId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}' }
        }).then(r => r.json()).then(data => {
            if (data.success) {
                cargarComentarios(currentPublicacionId);
                const count = document.getElementById(`com-count-${currentPublicacionId}`);
                count.textContent = parseInt(count.textContent) - 1;
                showToast('✅ Comentario eliminado');
            }
        });
    }
}

// ========== FOTO DE PERFIL ==========
document.getElementById('fotoInput')?.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showToast('❌ Selecciona una imagen válida', 'error');
        this.value = '';
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('❌ La imagen no debe superar los 5MB', 'error');
        this.value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('perfilFoto').src = e.target.result;
    };
    reader.readAsDataURL(file);

    showToast('📸 Subiendo foto de perfil...', 'info');
    document.getElementById('fotoForm').submit();
});

// Cerrar modales al hacer clic fuera
document.getElementById('modalGeneral')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalGeneral(); });
document.getElementById('modalSimple')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalSimple(); });
document.getElementById('modalComentarios')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalComentarios(); });
document.getElementById('modalExperiencia')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalExperiencia(); });
document.getElementById('modalEditarPublicacion')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalEditarPublicacion(); });
document.getElementById('modalEditarPortafolio')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalEditarPortafolio(); });
document.getElementById('modalDescripcion')?.addEventListener('click', e => { if (e.target === e.currentTarget) cerrarModalDescripcion(); });

// Exponer funciones
window.abrirModalEditarPublicacion = abrirModalEditarPublicacion;
window.eliminarPublicacion = eliminarPublicacion;
window.abrirModalEditarPortafolio = abrirModalEditarPortafolio;
window.eliminarFoto = eliminarFoto;
window.abrirModalEditar = abrirModalEditar;
window.abrirModalEditarExperiencia = abrirModalEditarExperiencia;
window.toggleDisponibilidad = toggleDisponibilidad;
window.toggleLike = toggleLike;
window.abrirModalComentarios = abrirModalComentarios;
window.enviarComentario = enviarComentario;
window.editarComentario = editarComentario;
window.eliminarComentario = eliminarComentario;
window.abrirModalGeneral = abrirModalGeneral;
window.cerrarModalGeneral = cerrarModalGeneral;
window.cerrarModalSimple = cerrarModalSimple;
window.guardarCampoSimple = guardarCampoSimple;
window.cerrarModalExperiencia = cerrarModalExperiencia;
window.guardarExperiencia = guardarExperiencia;
window.cerrarModalEditarPublicacion = cerrarModalEditarPublicacion;
window.guardarEdicionPublicacion = guardarEdicionPublicacion;
window.cerrarModalEditarPortafolio = cerrarModalEditarPortafolio;
window.guardarEdicionPortafolio = guardarEdicionPortafolio;
window.cancelarPreview = cancelarPreview;
window.abrirModalEditarDescripcion = abrirModalEditarDescripcion;