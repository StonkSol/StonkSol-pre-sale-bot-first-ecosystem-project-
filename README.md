# Bot de Telegram para la comunidad de StonkSol

Este repositorio contiene el código del bot PresaleStonkSolbot, diseñado para facilitar preventas de tokens sin costos ni comisiones para la comunidad de StonkSol.

## Librerías utilizadas

El bot utiliza las siguientes librerías:

### python-telegram-bot

La librería `python-telegram-bot` permite interactuar con la API de Telegram desde Python. Facilita la creación de bots de Telegram y el manejo de mensajes, comandos, entre otros.

Puedes encontrar más información sobre `python-telegram-bot` [aquí](https://github.com/python-telegram-bot/python-telegram-bot).

### urllib

La librería `urllib` se utiliza para generar y codificar URLs. En el contexto de este proyecto, se utiliza para construir la URL de autenticación de Phantom.

## Uso

Para utilizar el bot, sigue estos pasos:

1. Clona este repositorio a tu máquina local.
2. Instala las dependencias necesarias utilizando pip:

    "pip install python-telegram-bot"
   "pip install solana"
`pip install -r requirements.txt`

3. Ejecuta el bot con el siguiente comando:

`python main.py`

4. Una vez que el bot esté en funcionamiento, los usuarios pueden interactuar con él a través de comandos de Telegram, como `/start` y `/comprar`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork de este repositorio.
2. Crea una rama con una nueva funcionalidad o corrección de errores: `git checkout -b nueva-funcionalidad`.
3. Realiza tus cambios y realiza un commit: `git commit -am 'Añadir nueva funcionalidad'`.
4. Haz push a la rama: `git push origin nueva-funcionalidad`.
5. Envía un pull request.

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](https://opensource.org/licenses/MIT).

