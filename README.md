# Registro-Horario
Programa para generar el registro de jornada laboral.

Además mi primer proyecto en GitHub

Configurarión de NGINX
----------------------

Añado al fichero de configuración /etc/nginx/sites-available/default las siguientes líneas:

```
location /registro-horario/ {

        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;
        proxy_buffering off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        }


location /static {

        alias /var/www/Registro-Horario/static;  # Ruta absoluta a la carpeta static del proyecto Flask
        }


location ~ /(process|descargar_tabla_odt|subir_datos|descargar_formulario) {

        proxy_pass http://127.0.0.1:5000/$1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        }
```

Configuración de SYSTEMD
------------------------

Añado el fichero /etc/systemd/system/registro-horario.service con el siguiente contenido:

```
        [Unit]
        Description=Servidor Flask de Registro-Horario
        After=network.target

        [Service]
        User=perexat
        WorkingDirectory=/var/www/Registro-Horario/
        ExecStart=python3 /var/www/Registro-Horario/app.py
        Restart=always

        [Install]
        WantedBy=multi-user.target
```



Luego ejecutar
sudo systemctl enable registro-horario

Comprobar con
sudo systemctl is-enabled registro-horario
