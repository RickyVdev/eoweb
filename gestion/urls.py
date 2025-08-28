from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.login_view, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('clientes/',views.lista_clientes, name='lista_clientes'),
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('clientes/modificar/<int:cliente_id>/',views.modificar_cliente, name='modificar_cliente'),
    path('clientes/eliminar/<int:cliente_id>/',views.eliminar_cliente, name='eliminar_cliente'),
    path('empleados/',views.lista_empleados, name='lista_empleados'),
    path('empleados/agregar/',views.agregar_empleado, name='agregar_empleado'),
    path('empleados/modificar/<int:empleado_id>/',views.modificar_empleado, name='modificar_empleado'),
    path('empleados/eliminar/<int:empleado_id>/',views.eliminar_empleado, name='eliminar_empleado'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('empleado/enviar_invitacion/<int:empleado_id>/', views.enviar_invitacion_empleado, name='enviar_invitacion_empleado'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('empleados/editar-usuario/<int:empleado_id>/', views.editar_usuario_empleado, name='editar_usuario_empleado'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('empleados/<int:empleado_id>/', views.ver_empleado, name='ver_empleado'),
    path('clientes/<int:cliente_id>/ver/', views.ver_cliente, name='ver_cliente'),
    path('empleados/<int:empleado_id>/subir_documento/', views.subir_documento_empleado, name='subir_documento_empleado'),
    path('empleados/documento/<int:documento_id>/eliminar/', views.eliminar_documento_empleado, name='eliminar_documento_empleado'),
    path('clientes/<int:cliente_id>/eliminar_cfdi/', views.eliminar_cfdi_cliente, name='eliminar_cfdi_cliente'),
    path('ajax/obtener-id-empleado/', views.obtener_id_empleado_ajax, name='obtener_id_empleado_ajax'),
    path('clientes/<int:cliente_id>/obras/', views.ver_obras, name='ver_obras'),
    path('clientes/<int:cliente_id>/agregar/', views.agregar_obra, name='agregar_obra'),
    path('obras/<int:obra_id>/modificar/', views.modificar_obra, name='modificar_obra'),
    path('obras/eliminar/<int:obra_id>/', views.eliminar_obra, name='eliminar_obra'),
    path('obras/<int:obra_id>/servicios/', views.ver_servicios, name='ver_servicios'),
    path('obras/<int:obra_id>/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicios/detalle/<int:servicio_id>/', views.detalle_servicio, name='detalle_servicio'),
    path('servicios/modificar/<int:servicio_id>/', views.modificar_servicio, name='modificar_servicio'),
    path('servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('obras/', views.listado_obras, name='listado_obras'),
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


