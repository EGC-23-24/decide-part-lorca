# Proceso de Gestión de Incidencias

## ¿Qué es una incidencia?

Una incidencia es un problema que se ha detectado, relacionado con el software o la documentación del proyecto.

## ¿Qué es el Registro de Incidencias?

El Registro de Incidencias es un Project Board de GitHub, en el que se registran todas las incidencias detectadas. Cada incidencia se representa como una Issue. El idioma empleado en el Registro de Incidencias es el inglés.

## ¿Qué hacer cuando se detecta una incidencia?

Cuando se detecta una incidencia, se debe seguir el siguiente proceso:

1. Se crea una Issue en el Registro de Incidencias, dentro de la columna *OPEN*,  indicando el nombre de la incidencia y el módulo al que hace referencia, separado por un guión. Por ejemplo: *Import/Export Census - Census*. Si la incidencia está relacionada con la documentación, en lugar de un módulo, se indica *Doc*. Por ejemplo: *Change documentation - Doc*.
2. Si es necesario, se realiza una descripción detallada de la Issue.
3. Se asigna la Issue a la persona responsable de resolverla.
4. Se asigna una Label a la Issue indicando el grupo al que pertenece la persona responsable de resolverla (*lorca-1* o *lorca-2*).
5. Se asigna una Label a la Issue indicando el tipo de incidencia (*Error*, *Improvement* o *New feature*).
6. Se asigna una Label a la Issue indicando la prioridad de la incidencia (*High*, 
*Medium* o *Low*).

## ¿Qué hacer cuando se resuelve una incidencia?

Cuando se resuelve una incidencia, se debe seguir el siguiente proceso:

1. Crear una Pull Request hacia la rama `develop` del repositorio, en la que se incluya la modificación que resuelve la incidencia. Es importante que la Issue esté referenciada en la descripción de la Pull Request. Por ejemplo: *Fixes #1*.
2. Una vez que la Pull Request ha sido aprobada y fusionada, se mueve la Issue a la columna *CLOSED* del Registro de Incidencias.
3. Se cierra la Issue.
