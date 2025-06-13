# 📈 Portal de Rentabilidades SURA Investments

Aplicación web interactiva para visualizar y analizar las rentabilidades de fondos de inversión de SURA Investments en tiempo real.

## 🌟 Características Principales

### 📊 **Tres Módulos de Análisis:**
- **Rentabilidad Acumulada**: Visualiza el crecimiento acumulado de los fondos con gráficos interactivos
- **Rentabilidad Anualizada**: Consulta el rendimiento anual promedio equivalente
- **Rentabilidad por Año**: Compara el desempeño año calendario completo

### 🔧 **Funcionalidades:**
- ✅ **Filtros por Moneda**: CLP (Pesos Chilenos) y USD (Dólares)
- ✅ **Selección Sincronizada**: Los fondos seleccionados se sincronizan entre todas las pestañas
- ✅ **Períodos Personalizables**: 1M, 3M, 6M, YTD, 1Y, 3Y, 5Y, Max
- ✅ **Gráficos Interactivos**: Con opción de pantalla completa y descarga
- ✅ **Tablas Dinámicas**: Con códigos de colores para rendimientos positivos/negativos
- ✅ **Responsive Design**: Optimizado para desktop y móvil

## 🎯 **Datos y Fuentes**

- **Fuente**: Bloomberg Terminal
- **Actualización**: Diaria
- **Período**: Datos históricos desde inicio de cada fondo
- **Precisión**: Calculados con metodología estándar de la industria

## 🛠️ **Tecnologías Utilizadas**

### **Backend & Procesamiento:**
- **Python 3.8+**
- **Pandas** - Manipulación y análisis de datos
- **NumPy** - Cálculos numéricos
- **OpenPyXL** - Lectura de archivos Excel

### **Frontend & Visualización:**
- **Dash** - Framework web interactivo
- **Plotly** - Gráficos interactivos
- **Dash Bootstrap Components** - UI moderna y responsive

### **Deployment:**
- **Gunicorn** - Servidor WSGI para producción
- **Render.com** - Plataforma de hosting

## 🚀 **Instalación y Uso Local**

### **Prerrequisitos:**
```bash
Python 3.8+
pip
```

### **Pasos de Instalación:**

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Sura-Investments/Panel_Rentabilidad.git
cd Panel_Rentabilidad
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Verificar estructura de datos:**
Asegúrate de que `data/rentabilidades.xlsx` contenga:
- Hoja "nombres": Nombres de fondos y series
- Hoja "Pesos": Precios en CLP  
- Hoja "Dolares": Precios en USD

4. **Ejecutar aplicación:**
```bash
python app.py
```

5. **Acceder:**
```
http://localhost:8050
```

## 📂 **Estructura del Proyecto**

```
Panel_Rentabilidad/
├── app.py                    # Aplicación principal
├── server.py                 # Configuración para deployment
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación
├── data/
│   └── rentabilidades.xlsx   # Datos de rentabilidades
└── assets/
    ├── sura_logo.png         # Logo SURA
    ├── investments_logo.png  # Logo Investments
    ├── SuraSans-Bold.otf     # Fuente corporativa
    ├── SuraSans-Regular.otf  # Fuente corporativa
    ├── SuraSans-SemiBold.otf # Fuente corporativa
    └── custom_styles.css     # Estilos personalizados
```

## 🔧 **Configuración para Desarrollo**

### **Variables de Entorno:**
```bash
PORT=8050          # Puerto de la aplicación
DEBUG=True         # Modo debug (solo desarrollo)
```

### **Formato de Datos:**
El archivo Excel debe tener esta estructura:

**Hoja "nombres":**
- Fila 1: Nombres de fondos
- Fila 3: Códigos de series

**Hojas "Pesos" y "Dolares":**
- Columna A: Fechas (desde fila 8)
- Columnas B+: Precios de cada fondo

## 📊 **Cálculos Implementados**

### **Rentabilidad Simple:**
```
Rentabilidad = (Precio_Final / Precio_Inicial - 1) × 100
```

### **Rentabilidad Anualizada:**
```
Rentabilidad_Anual = ((Precio_Final / Precio_Inicial)^(1/años) - 1) × 100
```

### **Retornos Acumulados:**
```
Retorno_t = (Precio_t / Precio_base - 1) × 100
```

## 🎨 **Diseño y UX**

- **Colores Corporativos**: Paleta SURA (#0B2DCE, #24272A, #FFE946)
- **Tipografía**: SuraSans (Bold, Regular, SemiBold)
- **Responsive**: Bootstrap 5 + componentes personalizados
- **Accesibilidad**: Contraste optimizado y navegación por teclado

## 🔄 **Actualizaciones de Datos**

Para actualizar los datos:

1. **Reemplazar** `data/rentabilidades.xlsx` con datos actualizados
2. **Mantener** la misma estructura de hojas y columnas
3. **Restart** la aplicación para cargar nuevos datos

## 🚀 **Deployment en Producción**

### **Render.com (Recomendado):**

1. **Conectar repositorio GitHub**
2. **Configurar Build:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:server`
3. **Variables de entorno:**
   - `DEBUG=False`
   - `PORT=10000` (automático en Render)

### **Otras Plataformas:**
- Railway.app
- Heroku
- PythonAnywhere
- Vercel (con adaptaciones)

## 🤝 **Contribución**

### **Estándares de Código:**
- PEP 8 para Python
- Comentarios en español
- Docstrings para funciones principales
- Variables descriptivas

### **Proceso de Contribución:**
1. Fork del repositorio
2. Crear branch feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Add: nueva funcionalidad'`
4. Push a branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📞 **Soporte y Contacto**

**Equipo SURA Investments - Technology**
- **Email**: investments.tech@sura.cl
- **Interno**: Portal Colaboradores SURA

## 📜 **Licencia**

© 2025 SURA Investments. Todos los derechos reservados.

Este software es propiedad de SURA Investments y está destinado únicamente para uso interno de la organización.

