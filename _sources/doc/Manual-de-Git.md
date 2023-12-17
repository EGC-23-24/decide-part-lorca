<h1 align="center">Manual de Git</h1>

<h5 align="center">Por Álvaro Bernal Caunedo y Joaquín Martín Acuña</h5>

### Copiar commits de otras ramas
#### 1.1. Prerequisitos

**Si tienes cambios sin confirmar en local:**
1. Estando en tu rama:
	Para guardar tus cambios de forma temporal sin moverlos de rama:
		`git stash -u`
2. Tener actualizada la rama de la que quieres copiar los commits:
```
	git switch <rama_que_quieres_copiar>
	git fetch origin
	git pull origin  <rama_que_quieres_copiar>
```

#### 1.2. Copiar commits
1. Mirar el historial de commits de la rama
	- Desde el historial de github de esa rama
	- Haciendo:
			`git log --oneline`
2.  Volver a la rama en la que quieres copiar esos commits
	1. `git switch <tu_rama>`
3. Copiar los commits:
	- Si son muchos:
			`git cherry-pick <hash_commit_mas_antiguo>^..<hash_commit_mas_nuevo>`
	- Si son pocos:
			`git cherry-pick <hash1> <hash2>`

#### 1.3. Copiar commits
1. Recuperar tus anteriores
	`git stash apply`

> [!warning]
> Cuando vayas a hacer push a tu rama, seguramente tengas problemas con la actualización de las ramas. Para solucionarlo haz `git push -f origin <tu_rama>`

### Actualizar la integración continua en vuestra rama de trabajo

#### 1.1. Pre-requisitos

Si tienes cambios sin confirmar en local:
1. Estando en tu rama:
   `git stash -u`

#### 1.2. Actualizar:

1. Hacer un fetch para asegurarse de tener las últimas actualizaciones:
   `git fetch origin`

2. Cambiar a la rama 'develop':
   `git switch develop`

3. Actualizar 'develop' desde el repositorio remoto:
   `git pull origin develop`

4. Cambiar a la rama 'main':
   `git switch main`

5. Actualizar 'main' desde el repositorio remoto:
   `git pull origin main`

6. Volver a tu rama:
   `git switch <tu_rama>`

7. Hacer un rebase con los cambios de 'origin/main' en tu rama:
   `git rebase origin/main`

**POST-REQUISITOS** si hiciste stash:

Si hiciste stash al principio, vuelve a aplicar esos cambios:
1. Estando en tu rama:
   `git stash apply`

> [!warning]
> Cuando vayas a hacer push a tu rama, seguramente tengas problemas con la actualización de las ramas. Para solucionarlo haz `git push -f origin <tu_rama>`

