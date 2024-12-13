
from flask import Flask, Response, render_template, request, jsonify, url_for 
import cv2
import numpy as np
from torch.hub import load as hub_load
import time
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from code_flask import db,app

        
temps_entrer_polygone = 0
points_camera1 = []
points_camera2 =[]



# Définir le modèle de la table

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=True)
    image_path = db.Column(db.String(255), nullable=False)
    date_detection = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()

# Charger le modèle YOLOv5 pré-entraîné
model = hub_load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.eval()

# Ouvrir la caméra
#camera = cv2.VideoCapture('/home/osow/Bureau/C&V/Prjet_Etudiant_UTT/Mon_Projet_Etudiant - Copie (2)/Video_Data_Days.mp4')

def generation_video(camera):
    compteur = 0
    # Assurez-vous que le répertoire "captures" existe
    os.makedirs("captures", exist_ok=True)
    capture=False
    

    while True:
        success, frame = camera.read()

        if not success:
            break

        # Taille de l'image
        print("taille :", frame.shape)

        # Application du modèle YOLOv5
        results = model(frame)  # Faire des prédictions
        detections = results.xyxy[0].cpu().numpy()  # Obtenir les résultats (bounding boxes, confidence, class)

        # Dessiner les détections sur l'image (uniquement pour la classe "person")
        for *box, confidence, cls in detections:
            if int(cls) == 0  and not capture:  # Vérifier si la classe correspond à "person"
                x1, y1, x2, y2 = map(int, box)  # Coordonnées de la boîte englobante
                label = f"Person {confidence:.2f}"  # Nom et score
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Dessiner la boîte
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Ajouter le label
                
                image_path = f"captures/capture.jpg"
                cv2.imwrite(image_path, frame)
                print(f"Image sauvegardée : {image_path}")


                #Interaction avec la base de données dans le bon contexte
                def save_to_db():
                    with app.app_context():  # Utiliser le bon contexte d'application ici
                        nouvelle_detection = Detection(nom="Personne détectée", image_path=image_path)
                        db.session.add(nouvelle_detection)
                        db.session.commit()
                        print("Détection enregistrée dans la base de données")

                # Appeler la fonction pour sauvegarder dans la base de données
                save_to_db()

                capture=True
                """"
                # Enregistrer les détails dans la base de données
                nouvelle_detection = Detection(nom="Personne détectée", image_path=image_path)
                db.session.add(nouvelle_detection)
                db.session.commit()
                print("Détection enregistrée dans la base de données")


                #capture=True

                """

                
        # Encoder l'image pour l'afficher
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        compteur += 1
        

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

