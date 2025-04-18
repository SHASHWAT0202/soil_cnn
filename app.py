import os
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Flask app setup for Smart Soil AI
app = Flask(__name__, static_folder='static')

# For local development
if os.environ.get('VERCEL_ENV') != 'production':
    app.config['UPLOAD_FOLDER'] = 'uploads'
else:
    # For Vercel deployment - use /tmp for file uploads in serverless environment
    app.config['UPLOAD_FOLDER'] = '/tmp'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Model parameters
IMG_HEIGHT = 150
IMG_WIDTH = 150
MODEL_PATH = "soil_classifier_model.h5"

# Soil types and crop recommendations
SOIL_RECOMMENDATIONS = {
    "Black Soil": "Cotton, Soybean, Sorghum, Maize, Sunflower, Millets, Pulses",
    "Cinder Soil": "Millets, Oilseeds, Pulses",
    "Laterite Soil": "Tea, Coffee, Cashew, Coconut, Tapioca, Pineapple",
    "Peat Soil": "Rice, Potatoes, Sugar Beet, Vegetables",
    "Yellow Soil": "Groundnut, Maize, Cotton, Pulses, Oilseeds"
}

# Soil descriptions
SOIL_DESCRIPTIONS = {
    "Black Soil": "Rich in clay, calcium, potassium and magnesium. It has excellent water retention capacity and is ideal for deep-rooted crops. This soil is known for its fertility and self-plowing nature due to its high clay content.",
    "Cinder Soil": "Formed from volcanic ash and cinders, this soil has good drainage but may lack nutrients. It's lightweight with a gravelly texture, requiring organic matter supplements for optimal crop growth. Found primarily in volcanic regions.",
    "Laterite Soil": "Reddish in color due to high iron oxide content, these soils form in tropical regions with high rainfall. They tend to be acidic and leached of nutrients, but are suitable for specific crops with proper management.",
    "Peat Soil": "Highly organic soil formed from partially decomposed plant material in waterlogged conditions. It's dark, retains moisture extremely well, and is naturally acidic. When properly drained, it can be highly productive.",
    "Yellow Soil": "Contains iron oxides but in a less oxidized form than red soils. Typically found in regions with moderate rainfall, these soils are less fertile than black soils but can support a variety of crops with proper fertilization."
}

# Load model once at startup - only load during initialization to save memory in serverless
model = None
class_names = ["Black Soil", "Cinder Soil", "Laterite Soil", "Peat Soil", "Yellow Soil"]

def load_model_if_needed():
    """Load the model on demand to reduce cold start times"""
    global model
    if model is None:
        try:
            model = load_model(MODEL_PATH)
            print("✅ Smart Soil: Model loaded successfully")
        except Exception as e:
            print(f"❌ Smart Soil: Error loading model: {e}")
            return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_soil_type(image_path):
    try:
        if not load_model_if_needed():
            return {"error": "Failed to load model"}
            
        img = load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        confidence = float(prediction[0][predicted_class_index] * 100)
        
        soil_type = class_names[predicted_class_index]
        recommendations = SOIL_RECOMMENDATIONS.get(soil_type, "No specific recommendations available")
        description = SOIL_DESCRIPTIONS.get(soil_type, "No description available")
        
        return {
            "soil_type": soil_type,
            "confidence": confidence,
            "recommendations": recommendations,
            "description": description
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction
        result = predict_soil_type(filepath)
        
        # Clean up uploaded file in serverless environment
        if os.environ.get('VERCEL_ENV') == 'production':
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify(result)
    
    return jsonify({"error": "File type not allowed"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve static files for Vercel
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Remove test files before deployment
def cleanup_unnecessary_files():
    if os.path.exists('test_Y.jpg'):
        os.remove('test_Y.jpg')
        print("Removed unnecessary test image file")

# For local development
if __name__ == '__main__':
    # Run cleanup
    cleanup_unnecessary_files()
    
    # Start the app
    app.run(debug=True) 