Dashboard de Avance de Topografía - Proyecto GUAYEPO I & II
Esta es una aplicación web interactiva creada con Streamlit para monitorear el progreso de un proyecto de topografía.

🚀 Cómo ejecutar la aplicación localmente
Sigue estos pasos para poner en marcha el dashboard en tu computadora.

1. Prerrequisitos
Tener Python 3.8 o superior instalado.

Tener los archivos CSV del proyecto en la misma carpeta que los archivos de este repositorio. Los archivos CSV deben llamarse:

TABLAS JAVIER.xlsx - CUADRANTE 1.csv

TABLAS JAVIER.xlsx - CUADRANTE 2.csv

TABLAS JAVIER.xlsx - CUADRANTE 3.csv

TABLAS JAVIER.xlsx - CUADRANTE 4.csv

2. Instalación
Crea un entorno virtual (recomendado):

python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`

Instala las librerías necesarias:

pip install -r requirements.txt

3. Ejecución
Una vez instaladas las dependencias, ejecuta el siguiente comando en tu terminal:

streamlit run dashboard.py

Se abrirá una nueva pestaña en tu navegador web con la aplicación funcionando.

☁️ Cómo desplegar en Streamlit Community Cloud
Puedes desplegar esta aplicación de forma gratuita siguiendo estos pasos:

Sube tu proyecto a GitHub:

Crea un nuevo repositorio en tu cuenta de GitHub.

Sube los siguientes archivos a tu repositorio:

dashboard.py

requirements.txt

README.md (opcional)

Los 4 archivos .csv con los datos.

Conecta tu cuenta de Streamlit:

Ve a Streamlit Community Cloud.

Inicia sesión con tu cuenta de GitHub.

Haz clic en "New app" y selecciona el repositorio que acabas de crear.

Asegúrate de que el archivo principal sea dashboard.py.

Haz clic en "Deploy!".

¡Y listo! Tu aplicación estará en línea y accesible para cualquier persona con el enlace.
