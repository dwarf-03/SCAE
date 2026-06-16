# SCAE - Sistema de Control y Administración de Equipos

## Descripción General

SCAE (Sistema de Control y Administración de Equipos) es una aplicación web desarrollada en **Python con Django**, diseñada para gestionar de forma integral el proceso de alquiler de herramientas y equipos. El sistema implementa una arquitectura modular que facilita la administración de clientes, inventario, reservas, alquileres, devoluciones, multas y reportes, garantizando trazabilidad, seguridad y eficiencia operativa.

La plataforma centraliza toda la información del negocio en una base de datos relacional, automatizando procesos que tradicionalmente se realizan de manera manual y reduciendo errores administrativos.

## Objetivos del Proyecto

* Digitalizar el proceso de alquiler y devolución de herramientas.
* Mantener un control actualizado del inventario y su disponibilidad.
* Gestionar clientes y usuarios con diferentes niveles de acceso.
* Registrar auditorías para mejorar la trazabilidad de las operaciones.
* Automatizar notificaciones y el cálculo de multas cuando corresponda.
* Generar reportes que apoyen la toma de decisiones.
* Incorporar un chatbot para mejorar la interacción y atención al usuario.

## Funcionalidades Principales

### Gestión de Clientes

* Registro y actualización de información de clientes.
* Administración de documentos y datos asociados.

### Gestión de Inventario

* Administración de herramientas y equipos disponibles.
* Control de disponibilidad y estado de cada elemento.

### Módulo de Alquileres

* Creación y administración de reservas.
* Registro de alquileres activos.
* Seguimiento de cada operación realizada.

### Gestión de Devoluciones

* Registro del retorno de equipos.
* Actualización automática del inventario.
* Historial de devoluciones.

### Gestión de Multas

* Control de penalizaciones derivadas de retrasos o incumplimientos.
* Asociación de multas con los procesos correspondientes.

### Sistema de Auditoría

* Registro de eventos importantes dentro de la aplicación.
* Seguimiento de cambios para mejorar la trazabilidad y el control.

### Notificaciones

* Gestión de avisos relacionados con procesos relevantes del sistema.
* Soporte para recordatorios y alertas administrativas.

### Reportes

* Generación de información consolidada sobre alquileres, devoluciones, inventario y actividad del sistema.

### Chatbot Integrado

* Atención automatizada para consultas frecuentes.
* Gestión de sesiones, mensajes e intenciones predefinidas para brindar respuestas rápidas.

### Gestión de Usuarios

* Administración de usuarios y permisos.
* Control de acceso según roles definidos en la plataforma.

## Arquitectura del Sistema

El proyecto está organizado mediante una estructura modular basada en aplicaciones independientes de Django, permitiendo una alta cohesión y bajo acoplamiento entre componentes. Cada módulo encapsula su propia lógica de negocio, modelos de datos y funcionalidades específicas, facilitando el mantenimiento y la escalabilidad del sistema.

## Flujo General de Funcionamiento

1. El administrador registra clientes, herramientas y equipos en el sistema.
2. Se crean reservas o alquileres según las solicitudes recibidas.
3. El inventario actualiza automáticamente la disponibilidad de los elementos alquilados.
4. Al finalizar el período de alquiler, se registra la devolución y se restablece el estado del equipo.
5. Si existen incumplimientos, el sistema puede gestionar multas y generar los registros correspondientes.
6. Todas las operaciones relevantes quedan registradas mediante mecanismos de auditoría y pueden consultarse posteriormente en los reportes.

## Tecnologías Utilizadas

* Python
* Django
* Base de datos relacional (configurable según el entorno del proyecto)
* HTML
* CSS
* JavaScript
* Archivos estáticos y plantillas administradas por Django

## Beneficios del Sistema

* Automatización de procesos administrativos.
* Reducción de errores en la gestión de alquileres.
* Centralización y organización de la información.
* Mayor control sobre inventario, clientes y devoluciones.
* Registro de auditoría para garantizar trazabilidad.
* Escalabilidad para incorporar nuevas funcionalidades y módulos.
* Arquitectura modular que facilita el mantenimiento y la evolución del proyecto.
