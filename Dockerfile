FROM python:3.9-slim




# Installation des bibiothéques
RUN pip install --no-cache-dir -r requirements.txt

#  répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app



# Exposer le port Flask

EXPOSE 5000

# lancer l'application
CMD ["python", "code_flask.py"]
