# one-alura-project
Proyecto One Alura Latam para el Tech AI Builder

Para poder correr el codigo del repositorio se recomienda fuertemente primero crear un entorno virtual que englobe el proyecto
para evitar conflictos entre las dependencias del proyecto y las que se encuentren en su computador.

Para poder crear el entorno virtual debe escribir el siguiente codigo(Se asume que ya se encuentre Python instalado):

    python -m venv .venv

Luego debera activar el entorno virtual con el siguiente comando:
    (IOS, Linux, WSL) .venv/Scripts/activate
    (CMD) .venv\Scripts\activate.bat

Para correr el codigo sin ninguna modificacion o eligiendo el modelo de llm o embedding que quiera utilizar debera correr el siguiente codigo:
python app.py

Para utilizar Gemini como modelo de llm debera correr el siguiente comando:
python app.py --llm gemini

Para utilizar el modelo de embeddings de Gemini debera correr el siguiente comando:
python app.py --emb gemini

Si prefiere que todo el rag se genere con Gemini debera correr el siguiente comando:
python app --allgem True