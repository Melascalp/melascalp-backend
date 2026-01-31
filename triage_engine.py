"""
MelaScalp Triage Engine - MVP Backend Logic
Rule-based scalp condition classification for melanated skin
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConditionLabel(str, Enum):
    """Approved scalp condition labels (non-diagnostic)"""
    SEBORRHEIC_DERMATITIS = "seborrheic_dermatitis"
    FOLLICULITIS = "folliculitis"
    PSORIASIS = "psoriasis"
    SCALP_ACNE = "scalp_acne"
    TENSION_DAMAGE = "tension_damage"
    PRODUCT_BUILDUP = "product_buildup"
    DRY_SCALP = "dry_scalp"
    CONTACT_DERMATITIS = "contact_dermatitis"
    UNCLEAR = "unclear"


class ConfidenceLevel(str, Enum):
    """Confidence levels for classification"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class TriageInput:
    """Structured input from user quiz"""
    symptoms: List[str]
    style_type: str
    wash_frequency: str
    product_use: List[str]
    known_issues: List[str]
    image_uploaded: bool = False


@dataclass
class TriageResult:
    """Triage classification result"""
    condition_label: str
    care_plan_id: str
    referral_required: bool
    confidence_level: str
    reasoning: str
    severity_score: int  # 1-10 scale


class MelaScalpTriageEngine:
    """
    Core triage engine using conditional logic.
    Culturally competent for melanated hair and skin.
    """
    
    # Approved care plan mappings
    CARE_PLANS = {
        ConditionLabel.SEBORRHEIC_DERMATITIS: "CP-001",
        ConditionLabel.FOLLICULITIS: "CP-002",
        ConditionLabel.PSORIASIS: "CP-003",
        ConditionLabel.SCALP_ACNE: "CP-004",
        ConditionLabel.TENSION_DAMAGE: "CP-005",
        ConditionLabel.PRODUCT_BUILDUP: "CP-006",
        ConditionLabel.DRY_SCALP: "CP-006",
        ConditionLabel.CONTACT_DERMATITIS: "CP-007",
        ConditionLabel.UNCLEAR: "CP-999"
    }
    
    # Protective/tight hairstyles
    PROTECTIVE_STYLES = {
        "braids", "cornrows", "weave", "extensions", "locs", 
        "twists", "faux_locs", "crochet", "tight_ponytail"
    }
    
    # Low wash frequencies (appropriate for textured hair)
    LOW_WASH_FREQUENCIES = {"biweekly", "monthly", "less_than_monthly"}
    
    # Heavy styling products
    HEAVY_PRODUCTS = {"edge_control", "pomade", "grease", "gel", "wax"}
    
    def __init__(self):
        """Initialize the triage engine"""
        self.rule_chain = [
            self._check_folliculitis,
            self._check_psoriasis,
            self._check_tension_damage,
            self._check_seborrheic_dermatitis,
            self._check_contact_dermatitis,
            self._check_scalp_acne,
            self._check_product_buildup,
            self._check_dry_scalp,
        ]
    
    def classify(self, input_data: Dict) -> Dict:
        """
        Main classification method.
        
        Args:
            input_data: Dictionary with user quiz responses
            
        Returns:
            Dictionary with triage results
        """
        # Parse and validate input
        triage_input = self._parse_input(input_data)
        
        # Run through decision tree
        result = self._run_decision_tree(triage_input)
        
        # Apply referral overrides
        result = self._apply_referral_rules(result, triage_input)
        
        # Convert to output format
        return self._format_output(result)
    
    def _parse_input(self, data: Dict) -> TriageInput:
        """Parse and normalize input data"""
        return TriageInput(
            symptoms=[s.lower().strip() for s in data.get("symptoms", [])],
            style_type=data.get("style_type", "").lower().strip(),
            wash_frequency=data.get("wash_frequency", "").lower().strip(),
            product_use=[p.lower().strip() for p in data.get("product_use", [])],
            known_issues=[k.lower().strip() for k in data.get("known_issues", [])],
            image_uploaded=data.get("image_uploaded", False)
        )
    
    def _run_decision_tree(self, input_data: TriageInput) -> Optional[TriageResult]:
        """
        Run input through decision tree.
        Rules are checked in priority order (most severe first).
        """
        for rule_func in self.rule_chain:
            result = rule_func(input_data)
            if result:
                return result
        
        # Default fallback
        return self._create_unclear_result(input_data)
    
    # ========== CONDITION-SPECIFIC RULES ==========
    
    def _check_folliculitis(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 1: Folliculitis (bacterial infection of hair follicles)
        High risk with protective styling - can lead to scarring alopecia
        """
        has_bumps = any(s in data.symptoms for s in [
            "bumps", "pustules", "pimples", "small_bumps", "infected_bumps"
        ])
        
        has_pain = any(s in data.symptoms for s in [
            "pain", "painful", "tenderness", "tender", "sore", "soreness"
        ])
        
        has_protective_style = data.style_type in self.PROTECTIVE_STYLES
        
        has_inflammation = any(s in data.symptoms for s in [
            "redness", "swelling", "hot", "warm", "inflamed"
        ])
        
        # Folliculitis scoring
        score = 0
        confidence_factors = []
        
        if has_bumps:
            score += 3
            confidence_factors.append("bumps present")
        
        if has_pain:
            score += 3
            confidence_factors.append("painful symptoms")
        
        if has_protective_style:
            score += 2
            confidence_factors.append("protective styling")
        
        if has_inflammation:
            score += 2
            confidence_factors.append("inflammation signs")
        
        # Folliculitis threshold
        if score >= 5:
            confidence = self._calculate_confidence(score, max_score=10)
            
            reasoning = (
                f"Bumps and pain with {data.style_type} styling suggest folliculitis. "
                "This requires professional evaluation to prevent scarring."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.FOLLICULITIS.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.FOLLICULITIS],
                referral_required=True,  # Always refer folliculitis
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=8
            )
        
        return None
    
    def _check_psoriasis(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 2: Psoriasis (chronic autoimmune condition)
        Requires medical management
        """
        has_scales = any(s in data.symptoms for s in [
            "scales", "scaling", "thick_scales", "silvery_scales", 
            "scale_patches", "plaques"
        ])
        
        has_dryness = any(s in data.symptoms for s in [
            "dryness", "dry", "very_dry", "cracking"
        ])
        
        known_psoriasis = "psoriasis" in data.known_issues
        
        has_itching = any(s in data.symptoms for s in [
            "itching", "itchy", "irritation"
        ])
        
        score = 0
        
        # Known history is strong indicator
        if known_psoriasis:
            score += 5
        
        if has_scales:
            score += 4
        
        if has_dryness:
            score += 2
        
        if has_itching:
            score += 1
        
        # Psoriasis threshold
        if score >= 5:
            confidence = self._calculate_confidence(score, max_score=12)
            
            if known_psoriasis:
                reasoning = "Known psoriasis history with matching symptoms requires dermatologist management."
            else:
                reasoning = "Thick scaling and dryness patterns suggest psoriasis. Professional diagnosis recommended."
            
            return TriageResult(
                condition_label=ConditionLabel.PSORIASIS.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.PSORIASIS],
                referral_required=True,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=7
            )
        
        return None
    
    def _check_tension_damage(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 3: Tension damage / Traction alopecia
        Common with tight protective styles
        """
        has_tenderness = any(s in data.symptoms for s in [
            "tenderness", "tender", "sore", "soreness", "pain", "painful"
        ])
        
        has_protective_style = data.style_type in self.PROTECTIVE_STYLES
        
        has_hair_loss = any(s in data.symptoms for s in [
            "hair_loss", "thinning", "bald_spots", "edges_thinning", "breakage"
        ])
        
        has_bumps = any(s in data.symptoms for s in [
            "bumps", "pustules", "pimples"
        ])
        
        score = 0
        
        if has_tenderness and has_protective_style:
            score += 5  # Classic presentation
        
        if has_hair_loss:
            score += 4  # Serious concern
        
        if has_tenderness and not has_bumps:
            score += 2  # Tenderness without infection
        
        # Tension damage threshold (but not if bumps present - likely folliculitis)
        if score >= 5 and not has_bumps:
            confidence = self._calculate_confidence(score, max_score=11)
            
            reasoning = (
                f"Scalp tenderness with {data.style_type} suggests tension damage. "
                "Consult a professional to prevent traction alopecia."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.TENSION_DAMAGE.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.TENSION_DAMAGE],
                referral_required=True,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=7
            )
        
        return None
    
    def _check_seborrheic_dermatitis(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 4: Seborrheic Dermatitis (chronic inflammatory condition)
        Very common, manageable with OTC treatments
        """
        has_itching = any(s in data.symptoms for s in [
            "itching", "itchy", "irritation", "scratchy"
        ])
        
        has_flaking = any(s in data.symptoms for s in [
            "flaking", "flakes", "dandruff", "white_flakes", "yellow_flakes"
        ])
        
        has_oily = any(s in data.symptoms for s in [
            "oily", "greasy", "oily_flakes"
        ])
        
        has_redness = "redness" in data.symptoms or "red" in data.symptoms
        
        score = 0
        
        if has_itching and has_flaking:
            score += 5  # Classic presentation
        elif has_itching or has_flaking:
            score += 2
        
        if has_oily:
            score += 2  # Characteristic of seb derm
        
        if has_redness:
            score += 1
        
        # Seborrheic dermatitis threshold
        if score >= 4:
            confidence = self._calculate_confidence(score, max_score=10)
            
            reasoning = (
                "Itching and flaking are classic signs of seborrheic dermatitis. "
                "Often manageable with medicated shampoos."
            )
            
            # Refer if severe or chronic
            needs_referral = any(s in data.symptoms for s in [
                "severe", "worsening", "bleeding", "crusting"
            ]) or "eczema" in data.known_issues
            
            return TriageResult(
                condition_label=ConditionLabel.SEBORRHEIC_DERMATITIS.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.SEBORRHEIC_DERMATITIS],
                referral_required=needs_referral,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=4 if not needs_referral else 6
            )
        
        return None
    
    def _check_contact_dermatitis(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 5: Contact Dermatitis (allergic reaction to products)
        Common with new products or chemicals
        """
        has_itching = any(s in data.symptoms for s in ["itching", "itchy", "burning"])
        has_redness = any(s in data.symptoms for s in ["redness", "red", "inflamed"])
        has_bumps = any(s in data.symptoms for s in ["bumps", "rash", "hives"])
        
        uses_heavy_products = bool(set(data.product_use) & self.HEAVY_PRODUCTS)
        
        # Look for timing indicators
        recent_change = any(s in data.symptoms for s in [
            "new_product", "recent_reaction", "sudden_onset"
        ])
        
        score = 0
        
        if has_itching and has_redness:
            score += 3
        
        if has_bumps and not any(s in data.symptoms for s in ["pustules", "pus"]):
            score += 2  # Bumps but not infected
        
        if uses_heavy_products or recent_change:
            score += 2
        
        if score >= 4:
            confidence = self._calculate_confidence(score, max_score=7)
            
            reasoning = (
                "Symptoms suggest possible contact dermatitis from hair products. "
                "Consider eliminating products one at a time."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.CONTACT_DERMATITIS.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.CONTACT_DERMATITIS],
                referral_required=False,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=4
            )
        
        return None
    
    def _check_scalp_acne(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 6: Scalp Acne (pimples from product buildup)
        Common with heavy styling products
        """
        has_bumps = any(s in data.symptoms for s in [
            "bumps", "pimples", "small_bumps"
        ])
        
        has_oily = any(s in data.symptoms for s in [
            "oily", "greasy"
        ])
        
        uses_heavy_products = bool(set(data.product_use) & self.HEAVY_PRODUCTS)
        
        no_pain = not any(s in data.symptoms for s in [
            "pain", "painful", "tender", "sore"
        ])
        
        not_protective_style = data.style_type not in self.PROTECTIVE_STYLES
        
        score = 0
        
        if has_bumps and no_pain:
            score += 3
        
        if has_oily:
            score += 2
        
        if uses_heavy_products:
            score += 2
        
        if not_protective_style:
            score += 1
        
        # Scalp acne threshold
        if score >= 4:
            confidence = self._calculate_confidence(score, max_score=8)
            
            reasoning = (
                "Bumps and product buildup suggest scalp acne. "
                "Try clarifying shampoo and reducing heavy products."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.SCALP_ACNE.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.SCALP_ACNE],
                referral_required=False,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=3
            )
        
        return None
    
    def _check_product_buildup(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 7: Product Buildup
        Common with low wash frequency and heavy products
        """
        has_flaking = any(s in data.symptoms for s in [
            "flaking", "flakes", "buildup"
        ])
        
        uses_heavy_products = bool(set(data.product_use) & self.HEAVY_PRODUCTS)
        low_wash = data.wash_frequency in self.LOW_WASH_FREQUENCIES
        
        has_itching = "itching" in data.symptoms or "itchy" in data.symptoms
        
        score = 0
        
        if has_flaking and not has_itching:
            score += 3  # Flaking without inflammation
        
        if uses_heavy_products and low_wash:
            score += 3
        
        if len(data.product_use) >= 3:
            score += 1  # Multiple products
        
        if score >= 4:
            confidence = self._calculate_confidence(score, max_score=7)
            
            reasoning = (
                "Product buildup from styling products. "
                "Consider clarifying treatments and adjusting wash routine."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.PRODUCT_BUILDUP.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.PRODUCT_BUILDUP],
                referral_required=False,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=2
            )
        
        return None
    
    def _check_dry_scalp(self, data: TriageInput) -> Optional[TriageResult]:
        """
        PRIORITY 8: Dry Scalp
        Very common, especially with low moisture routines
        """
        has_dryness = any(s in data.symptoms for s in [
            "dryness", "dry", "tight", "flaking"
        ])
        
        low_wash = data.wash_frequency in self.LOW_WASH_FREQUENCIES
        
        minimal_symptoms = len(data.symptoms) <= 2
        
        score = 0
        
        if has_dryness:
            score += 3
        
        if low_wash and not any("oil" in p for p in data.product_use):
            score += 2  # Low wash without moisturizing
        
        if minimal_symptoms:
            score += 1
        
        if score >= 3:
            confidence = ConfidenceLevel.MODERATE.value
            
            reasoning = (
                "Dry scalp symptoms. Increase moisture with oils and gentle cleansing."
            )
            
            return TriageResult(
                condition_label=ConditionLabel.DRY_SCALP.value,
                care_plan_id=self.CARE_PLANS[ConditionLabel.DRY_SCALP],
                referral_required=False,
                confidence_level=confidence,
                reasoning=reasoning,
                severity_score=2
            )
        
        return None
    
    def _create_unclear_result(self, data: TriageInput) -> TriageResult:
        """Fallback for unclear cases"""
        return TriageResult(
            condition_label=ConditionLabel.UNCLEAR.value,
            care_plan_id=self.CARE_PLANS[ConditionLabel.UNCLEAR],
            referral_required=True,  # Refer unclear cases
            confidence_level=ConfidenceLevel.LOW.value,
            reasoning=(
                "Symptoms don't clearly match a single condition. "
                "Professional evaluation recommended for accurate diagnosis."
            ),
            severity_score=5
        )
    
    # ========== HELPER METHODS ==========
    
    def _apply_referral_rules(
        self, 
        result: TriageResult, 
        data: TriageInput
    ) -> TriageResult:
        """
        Override referral flag based on severity indicators.
        Safety-first approach.
        """
        # Automatic referral triggers
        severe_symptoms = any(s in data.symptoms for s in [
            "bleeding", "pus", "oozing", "crusting", "severe", 
            "worsening", "spreading", "fever"
        ])
        
        hair_loss_with_pain = (
            any(s in data.symptoms for s in ["hair_loss", "bald_spots"]) and
            any(s in data.symptoms for s in ["pain", "tenderness"])
        )
        
        known_chronic_condition = any(
            condition in data.known_issues 
            for condition in ["psoriasis", "eczema", "lupus", "autoimmune"]
        )
        
        # Override if any severe trigger
        if severe_symptoms or hair_loss_with_pain:
            result.referral_required = True
            result.severity_score = max(result.severity_score, 8)
            result.reasoning += " URGENT: Severe symptoms require immediate professional evaluation."
        
        if known_chronic_condition and not result.referral_required:
            result.referral_required = True
            result.reasoning += " Note: Known condition warrants professional monitoring."
        
        return result
    
    def _calculate_confidence(self, score: int, max_score: int) -> str:
        """Calculate confidence level from scoring"""
        percentage = (score / max_score) * 100
        
        if percentage >= 70:
            return ConfidenceLevel.HIGH.value
        elif percentage >= 40:
            return ConfidenceLevel.MODERATE.value
        else:
            return ConfidenceLevel.LOW.value
    
    def _format_output(self, result: TriageResult) -> Dict:
        """Format result as JSON-serializable dict"""
        return {
            "condition_label": result.condition_label,
            "care_plan_id": result.care_plan_id,
            "referral_required": result.referral_required,
            "confidence_level": result.confidence_level,
            "reasoning": result.reasoning,
            "severity_score": result.severity_score
        }


# ========== CONVENIENCE FUNCTION ==========

def classify_symptoms(input_data: Dict) -> Dict:
    """
    Main entry point for triage classification.
    
    Args:
        input_data: Dictionary with user quiz responses
        
    Returns:
        Dictionary with classification results
        
    Example:
        >>> result = classify_symptoms({
        ...     "symptoms": ["itching", "flaking"],
        ...     "style_type": "natural",
        ...     "wash_frequency": "weekly",
        ...     "product_use": ["oil"],
        ...     "known_issues": [],
        ...     "image_uploaded": False
        ... })
        >>> print(result["condition_label"])
        'seborrheic_dermatitis'
    """
    engine = MelaScalpTriageEngine()
    return engine.classify(input_data)
