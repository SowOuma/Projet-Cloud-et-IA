from code_python import*
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# Initialisation des variables globales
camera1_url = None#"rtsp://169.254.197.98:554/media/video1"
camera2_url =None
camera = None
camera1 = None
points_camera1 = []
points_camera2 = []



# Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://detection_user:sowoumar@localhost:5432/detection_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
 #Initialiser SQLAlchemy avec Flask
 
db = SQLAlchemy()
db.init_app(app)  # Assurez-vous que l'app est associée à l'instance de SQLAlchemy






#definition du route principale 
@app.route("/")


#appelle de la appelle page html pour son affichage 

@app.route("/home1")
def home1():
    return render_template('home.html')

#recuperation des urls saisi dans sur les champs du formulaire

@app.route('/recuperer_source', methods=['POST'])
def recuperer_source():
    global camera1_url, camera2_url, camera, camera1
    data = request.json
    try:
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        """"
        if 'camera1_url' not in data or 'camera2_url' not in data:
            return jsonify({'error': 'Les URLs des deux caméras doivent être fournies'}), 400
        """
        camera1_url = data.get('camera1_url')
        
        
        print(f"URL de la caméra 1 : {camera1_url}")
      
        
        # Libération des caméras précédemment ouvertes

        if camera is not None:
            camera.release()
        


        def captureVideo(url):
            if url.startswith("rtsp://"):
                capture=cv2.VideoCapture(url)
                capture.set(cv2.CAP_PROP_BUFFERSIZE,2)
                
                return capture
            elif(url=='0'):
                return cv2.VideoCapture(0)
            else:

                return cv2.VideoCapture(url)
    
        camera = captureVideo(camera1_url)
        
        
        # Vérification si les caméras ont été ouvertes avec succès
        if not camera.isOpened():
            camera = None
            print(f"Échec de l'ouverture de la caméra avec l'URL {camera1_url}")
            return jsonify({'error': f'Échec de l\'ouverture de la caméra avec l\'URL {camera1_url}'}), 500
        
        return jsonify({'message': 'Flux démarrés avec succès'})
    except Exception as e:
        print(f"Erreur lors de la recuperation des urls: {str(e)}")   
     



@app.route("/video")
def video():
    if camera is None:
        return "Camera 1 non initialisée", 500
    return Response(generation_video(camera), mimetype="multipart/x-mixed-replace; boundary=frame")





@app.route("/cliquer_bouton", methods=["POST"])
def cliquer_bouton():
    button = request.form.get("button")
    if button == "camera1":
        url = url_for("video", _external=True)  # Retourne l'URL complète pour /video
    elif button == "camera2":
        url = url_for("video1", _external=True)  # Retourne l'URL complète pour /video1
    else:
        url = None

    if url:
        return jsonify({"url": url})
    else:
        return jsonify({"error": "Flux vidéo non disponible"}), 400
    


@app.route('/detections', methods=['GET'])
def get_detections():
    try:
        detections = Detection.query.all()
        resultat = [
            {
                'id': d.id,
                'nom': d.nom,
                'image_path': d.image_path,
                'date_detection': d.date_detection.strftime('%Y-%m-%d %H:%M:%S')
            }
            for d in detections
        ]
        return {"detections": resultat}, 200
    except Exception as e:
        return {"error": str(e)}, 500



if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=3000)
