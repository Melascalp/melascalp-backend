"""
MelaScalp Backend API - Flask Implementation
RESTful API wrapper for the triage engine
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from datetime import datetime

from triage_engine import classify_symptoms, MelaScalpTriageEngine

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== INPUT VALIDATION ==========

VALID_SYMPTOMS = {
    "itching", "itchy", "flaking", "flakes", "dandruff", "bumps", "pustules",
    "pimples", "small_bumps", "pain", "painful", "tenderness", "tender",
    "sore", "soreness", "dryness", "dry", "oily", "greasy", "scales",
    "scaling", "thick_scales", "silvery_scales", "scale_patches", "plaques",
    "redness", "red", "inflamed", "swelling", "hot", "warm", "burning",
    "hair_loss", "thinning", "bald_spots", "edges_thinning", "breakage",
    "bleeding", "crusting", "oozing", "pus", "infected_bumps", "severe",
    "worsening", "spreading", "rash", "hives"
}

VALID_STYLE_TYPES = {
    "natural", "braids", "cornrows", "weave", "extensions", "locs",
    "twists", "faux_locs", "crochet", "tight_ponytail", "relaxed",
    "permed", "none"
}

VALID_WASH_FREQUENCIES = {
    "daily", "every_other_day", "twice_weekly", "weekly",
    "biweekly", "monthly", "less_than_monthly"
}

VALID_PRODUCTS = {
    "shampoo", "conditioner", "oil", "gel", "edge_control",
    "pomade", "grease", "wax", "leave_in", "mousse",
    "hairspray", "serum"
}


def validate_triage_input(f):
    """Decorator to validate incoming triage requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON payload provided",
                "status": "error"
            }), 400
        
        # Check required fields
        required = ["symptoms", "style_type", "wash_frequency"]
        missing = [field for field in required if field not in data]
        
        if missing:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing)}",
                "status": "error"
            }), 400
        
        # Validate symptoms is non-empty list
        if not isinstance(data.get("symptoms"), list) or len(data["symptoms"]) == 0:
            return jsonify({
                "error": "Symptoms must be a non-empty array",
                "status": "error"
            }), 400
        
        # Validate style_type
        if data["style_type"].lower() not in VALID_STYLE_TYPES:
            return jsonify({
                "error": f"Invalid style_type. Must be one of: {', '.join(VALID_STYLE_TYPES)}",
                "status": "error"
            }), 400
        
        # Validate wash_frequency
        if data["wash_frequency"].lower() not in VALID_WASH_FREQUENCIES:
            return jsonify({
                "error": f"Invalid wash_frequency. Must be one of: {', '.join(VALID_WASH_FREQUENCIES)}",
                "status": "error"
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


# ========== API ENDPOINTS ==========

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MelaScalp Triage API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route('/api/v1/triage', methods=['POST'])
@validate_triage_input
def triage():
    """
    Main triage endpoint.
    
    Request Body:
    {
        "symptoms": ["itching", "flaking"],
        "style_type": "braids",
        "wash_frequency": "weekly",
        "product_use": ["oil", "gel"],
        "known_issues": ["eczema"],
        "image_uploaded": false
    }
    
    Response:
    {
        "condition_label": "seborrheic_dermatitis",
        "care_plan_id": "CP-001",
        "referral_required": false,
        "confidence_level": "high",
        "reasoning": "...",
        "severity_score": 4,
        "status": "success",
        "timestamp": "2026-01-30T22:00:00.000Z"
    }
    """
    try:
        input_data = request.get_json()
        
        # Log request (without PII)
        logger.info(f"Triage request: {len(input_data.get('symptoms', []))} symptoms, "
                   f"style: {input_data.get('style_type')}")
        
        # Run classification
        result = classify_symptoms(input_data)
        
        # Add metadata
        result.update({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "api_version": "1.0.0"
        })
        
        # Log result
        logger.info(f"Triage result: {result['condition_label']}, "
                   f"referral: {result['referral_required']}, "
                   f"confidence: {result['confidence_level']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in triage endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error during classification",
            "status": "error"
        }), 500


@app.route('/api/v1/conditions', methods=['GET'])
def list_conditions():
    """
    List all supported condition labels and care plans.
    
    Response:
    {
        "conditions": {
            "seborrheic_dermatitis": {
                "care_plan_id": "CP-001",
                "name": "Seborrheic Dermatitis",
                "typically_requires_referral": false,
                "description": "..."
            },
            ...
        },
        "total_count": 8
    }
    """
    conditions = {
        "seborrheic_dermatitis": {
            "care_plan_id": "CP-001",
            "name": "Seborrheic Dermatitis",
            "typically_requires_referral": False,
            "description": "Chronic inflammatory condition causing itching and flaking"
        },
        "folliculitis": {
            "care_plan_id": "CP-002",
            "name": "Folliculitis",
            "typically_requires_referral": True,
            "description": "Inflammation of hair follicles, common with protective styles"
        },
        "psoriasis": {
            "care_plan_id": "CP-003",
            "name": "Psoriasis",
            "typically_requires_referral": True,
            "description": "Chronic autoimmune condition causing thick, scaly patches"
        },
        "scalp_acne": {
            "care_plan_id": "CP-004",
            "name": "Scalp Acne",
            "typically_requires_referral": False,
            "description": "Pimples and bumps from product buildup or excess oil"
        },
        "tension_damage": {
            "care_plan_id": "CP-005",
            "name": "Tension Damage / Traction Alopecia",
            "typically_requires_referral": True,
            "description": "Damage from tight hairstyles causing tenderness and hair loss"
        },
        "product_buildup": {
            "care_plan_id": "CP-006",
            "name": "Product Buildup",
            "typically_requires_referral": False,
            "description": "Accumulation of styling products on scalp"
        },
        "dry_scalp": {
            "care_plan_id": "CP-006",
            "name": "Dry Scalp",
            "typically_requires_referral": False,
            "description": "Lack of moisture causing dryness and sometimes flaking"
        },
        "contact_dermatitis": {
            "care_plan_id": "CP-007",
            "name": "Contact Dermatitis",
            "typically_requires_referral": False,
            "description": "Allergic reaction to hair products or chemicals"
        }
    }
    
    return jsonify({
        "conditions": conditions,
        "total_count": len(conditions),
        "status": "success"
    }), 200


@app.route('/api/v1/validate', methods=['POST'])
def validate_input():
    """
    Validate quiz input before submission.
    
    Request Body:
    {
        "symptoms": ["itching", "unknown_symptom"],
        "style_type": "braids",
        "wash_frequency": "weekly",
        "product_use": ["oil"]
    }
    
    Response:
    {
        "valid": false,
        "errors": {
            "symptoms": ["unknown_symptom is not recognized"]
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "error": "No JSON payload provided"
        }), 400
    
    errors = {}
    
    # Validate symptoms
    if "symptoms" in data:
        unknown = [s for s in data["symptoms"] if s.lower() not in VALID_SYMPTOMS]
        if unknown:
            errors["symptoms"] = [f"'{s}' is not a recognized symptom" for s in unknown]
    
    # Validate style_type
    if "style_type" in data and data["style_type"].lower() not in VALID_STYLE_TYPES:
        errors["style_type"] = f"Must be one of: {', '.join(VALID_STYLE_TYPES)}"
    
    # Validate wash_frequency
    if "wash_frequency" in data and data["wash_frequency"].lower() not in VALID_WASH_FREQUENCIES:
        errors["wash_frequency"] = f"Must be one of: {', '.join(VALID_WASH_FREQUENCIES)}"
    
    # Validate products
    if "product_use" in data:
        unknown_products = [p for p in data["product_use"] if p.lower() not in VALID_PRODUCTS]
        if unknown_products:
            errors["product_use"] = [f"'{p}' is not recognized" for p in unknown_products]
    
    is_valid = len(errors) == 0
    
    return jsonify({
        "valid": is_valid,
        "errors": errors if not is_valid else None,
        "status": "success"
    }), 200


@app.route('/api/v1/vocabulary', methods=['GET'])
def get_vocabulary():
    """
    Get valid vocabulary for all quiz fields.
    Useful for frontend autocomplete/validation.
    """
    return jsonify({
        "symptoms": sorted(list(VALID_SYMPTOMS)),
        "style_types": sorted(list(VALID_STYLE_TYPES)),
        "wash_frequencies": sorted(list(VALID_WASH_FREQUENCIES)),
        "products": sorted(list(VALID_PRODUCTS)),
        "status": "success"
    }), 200


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500


# ========== MAIN ==========

if __name__ == '__main__':
    # Development server
    # In production, use gunicorn or similar WSGI server
    logger.info("Starting MelaScalp Triage API...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
