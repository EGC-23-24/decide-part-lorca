<h1 align="center">Ciclo de despliegue e integración continua</h1>
<h6 align="center">Documento que presenta la metodología DevOps implementada en el proyecto. Centrándose en la automatización, el control de la calidad y la eficiencia del despliegue.</h6>

### 1. Control de versiones y gestión del código fuente

Usamos Git y GitHub para el control de versiones, adoptando un flujo de trabajo centrado en pull requests (PR) para facilitar las revisiones de código colaborativas y eficientes. Cada PR es revisada exhaustivamente por pares, garantizando el funcionamiento y la coherencia del código. Con este proceso buscamos no solo mejorar la calidad del código, sino fomentar la colaboración y el intercambio de conocimientos entre los miembros del equipo de trabajo.

### 2. Gestión de dependencias

Para la gestión de dependencias utilizamos Pip, lo que nos permite mantener un control preciso sobre las versiones de bibliotecas y paquetes en diferentes entornos. Esta práctica es fundamental para garantizar la reproducibilidad y la estabilidad del sistema. 

### 3. Integración Continua (CI)

#### a. Automatización de pruebas

Como parte del proceso de integración continua, tenemos configurado el lanzamiento automatizado del conjunto de tests que prueban cada una de las funcionalidades que integran un incremento en el sistema. La ejecución de estos tests junto a las revisiones, garantizan el funcionamiento del código, identificando errores antes de la integración. En este sentido, optimizan el proceso de revisión, al automatizar la evaluación de aspectos básicos, permitiendo a los revisores centrarse en detalles más complejos.

#### b. Evaluación de la calidad del código y cumplimiento de PEP8

Paralelamente, ejecutamos rutinas para evaluar la calidad del código y su conformidad con PEP8. Utilizamos herramientas automatizadas que no solo analizan el código, sino que también pueden generar PR de refactorización para alinearse con las mejores prácticas de estilo. Con este enfoque buscamos garantizar la coherencia y legibilidad del código, facilitando el mantenimiento y la colaboración.

### 4. Despliegue automatizado y gestión de configuraciones

#### a. Despliegue en Render

Al fusionar las características que integran un paquete de incremento funcional del sistema en la rama 'develop', iniciamos una PR hacia la rama de producción 'main' que desencadena el despliegue automático en Render. Este proceso garantiza una entrega continua y eficiente, minimizando el tiempo de inactividad y maximizando la disponibilidad del sistema. Este enfoque de despliegue asegura que las nuevas funcionalidades y correcciones estén rápidamente al alcance del usuario final de la apliación.

#### b. Dockerización

Contamos además con una configuración de despliegue en Docker, encapsulando todas las dependencias y servicios necesarios para lanzar el sistema. Esto nos proporciona un entorno de despligue uniforme, que evita inconsistencias entre los entornos de desarrollo y producción. Esta configuración nos permite probar la funcionalidad de los diferentes incrementos específicos así como la del entorno de producción, para ello, se indica como argumento de construcción de las imágenes, la rama del repositorio de código fuente que se desea ejecutar, siendo la rama por defecto la que contiene el sistema listo para producción.

### 5. Generación automatizada de documentación

La documentación del sistema se genera de manera automática a partir de docstrings en el código fuente usando la herramienta Sphinx. Este proceso se automatiza mediante una rutina específica que asegura que la documentación está siempre actualizada con los últimos cambios. TLa documentación, además, se publica en GitHub Pages, con objeto de facilitar su accesibilidad y contribuir a facilitar el mantenimiento y la integración del sistema.

### 6. Preparación de releases

Para las releases, adoptamos Semantic Versioning, un metodología que da significado a cada incremento de versión. Cuando se completa un incremento funcional o correción del sistema, añadimos una tag al código, tal y como se recoge en el documento de preparación de releases, lo que desencadena automáticamente la creación de una nueva release. Esta práctica asegura una gestión de versiones coherente y transparente, facilitando el seguimiento de cambios y mejoras del sistema.
