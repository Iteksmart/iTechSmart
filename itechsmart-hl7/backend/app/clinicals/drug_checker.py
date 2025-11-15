"""
Drug Interaction Checker
Medication safety and drug interaction detection
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InteractionSeverity(str, Enum):
    """Drug interaction severity levels"""
    CONTRAINDICATED = "contraindicated"  # Never use together
    MAJOR = "major"  # May cause serious harm
    MODERATE = "moderate"  # May cause moderate harm
    MINOR = "minor"  # Limited clinical significance


class InteractionType(str, Enum):
    """Types of drug interactions"""
    DRUG_DRUG = "drug_drug"
    DRUG_ALLERGY = "drug_allergy"
    DRUG_CONDITION = "drug_condition"
    DRUG_FOOD = "drug_food"
    DRUG_LAB = "drug_lab"
    DUPLICATE_THERAPY = "duplicate_therapy"
    PREGNANCY = "pregnancy"
    RENAL_ADJUSTMENT = "renal_adjustment"
    HEPATIC_ADJUSTMENT = "hepatic_adjustment"


class DrugInteraction:
    """Drug interaction details"""
    
    def __init__(
        self,
        interaction_id: str,
        interaction_type: InteractionType,
        severity: InteractionSeverity,
        drug1: str,
        drug2: Optional[str],
        description: str,
        clinical_effects: str,
        management: str,
        references: List[str] = None
    ):
        self.interaction_id = interaction_id
        self.interaction_type = interaction_type
        self.severity = severity
        self.drug1 = drug1
        self.drug2 = drug2
        self.description = description
        self.clinical_effects = clinical_effects
        self.management = management
        self.references = references or []
        self.detected_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'interaction_id': self.interaction_id,
            'interaction_type': self.interaction_type.value,
            'severity': self.severity.value,
            'drug1': self.drug1,
            'drug2': self.drug2,
            'description': self.description,
            'clinical_effects': self.clinical_effects,
            'management': self.management,
            'references': self.references,
            'detected_at': self.detected_at.isoformat()
        }


class DrugInteractionChecker:
    """
    Drug Interaction Checker
    Detects medication safety issues and drug interactions
    """
    
    def __init__(self):
        self.interaction_database: Dict[str, List[DrugInteraction]] = {}
        self.allergy_database: Dict[str, List[str]] = {}
        self.pregnancy_categories: Dict[str, str] = {}
        self._load_interaction_database()
    
    def _load_interaction_database(self):
        """Load drug interaction database"""
        
        # Major Drug-Drug Interactions
        interactions = [
            # Warfarin interactions
            DrugInteraction(
                "DDI_001",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "warfarin",
                "aspirin",
                "Warfarin + Aspirin increases bleeding risk",
                "Increased risk of major bleeding, GI bleeding, intracranial hemorrhage",
                "Monitor INR closely. Consider alternative antiplatelet if possible. Use lowest effective aspirin dose.",
                ["Micromedex", "Lexicomp"]
            ),
            DrugInteraction(
                "DDI_002",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.CONTRAINDICATED,
                "warfarin",
                "ketoconazole",
                "Warfarin + Ketoconazole - Contraindicated",
                "Severe increase in INR, life-threatening bleeding risk",
                "Avoid combination. Use alternative antifungal (e.g., fluconazole with dose adjustment).",
                ["FDA", "Micromedex"]
            ),
            
            # ACE Inhibitor interactions
            DrugInteraction(
                "DDI_003",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "lisinopril",
                "spironolactone",
                "ACE Inhibitor + Potassium-sparing diuretic",
                "Hyperkalemia risk, cardiac arrhythmias, muscle weakness",
                "Monitor potassium levels closely. Consider alternative diuretic. Avoid potassium supplements.",
                ["UpToDate", "Lexicomp"]
            ),
            
            # SSRI interactions
            DrugInteraction(
                "DDI_004",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.CONTRAINDICATED,
                "fluoxetine",
                "phenelzine",
                "SSRI + MAOI - Serotonin Syndrome",
                "Life-threatening serotonin syndrome: hyperthermia, rigidity, autonomic instability",
                "Contraindicated. Allow 5-week washout after fluoxetine before starting MAOI.",
                ["FDA Black Box", "Micromedex"]
            ),
            
            # Statin interactions
            DrugInteraction(
                "DDI_005",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "simvastatin",
                "clarithromycin",
                "Simvastatin + Clarithromycin - Rhabdomyolysis risk",
                "Increased statin levels, rhabdomyolysis, acute kidney injury",
                "Avoid combination. Suspend statin during clarithromycin course or use alternative antibiotic.",
                ["FDA", "Lexicomp"]
            ),
            
            # Anticoagulant interactions
            DrugInteraction(
                "DDI_006",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "apixaban",
                "ibuprofen",
                "Anticoagulant + NSAID increases bleeding risk",
                "Increased risk of GI bleeding, intracranial hemorrhage",
                "Avoid NSAIDs if possible. Use acetaminophen for pain. If NSAID necessary, use lowest dose with PPI.",
                ["CHEST Guidelines", "Micromedex"]
            ),
            
            # QT prolongation
            DrugInteraction(
                "DDI_007",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "azithromycin",
                "ondansetron",
                "QT prolongation risk",
                "Additive QT prolongation, torsades de pointes, sudden cardiac death",
                "Monitor ECG. Avoid in patients with QT >500ms. Consider alternative antiemetic.",
                ["CredibleMeds", "FDA"]
            ),
            
            # Methotrexate interactions
            DrugInteraction(
                "DDI_008",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "methotrexate",
                "trimethoprim",
                "Methotrexate + Trimethoprim - Bone marrow suppression",
                "Severe pancytopenia, megaloblastic anemia, mucositis",
                "Avoid combination. Use alternative antibiotic. Monitor CBC closely if unavoidable.",
                ["Micromedex", "Lexicomp"]
            ),
            
            # Digoxin interactions
            DrugInteraction(
                "DDI_009",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "digoxin",
                "amiodarone",
                "Digoxin + Amiodarone increases digoxin levels",
                "Digoxin toxicity: nausea, arrhythmias, visual disturbances",
                "Reduce digoxin dose by 50%. Monitor digoxin levels. Check for toxicity symptoms.",
                ["UpToDate", "Micromedex"]
            ),
            
            # Lithium interactions
            DrugInteraction(
                "DDI_010",
                InteractionType.DRUG_DRUG,
                InteractionSeverity.MAJOR,
                "lithium",
                "hydrochlorothiazide",
                "Lithium + Thiazide diuretic increases lithium levels",
                "Lithium toxicity: tremor, confusion, seizures, renal failure",
                "Monitor lithium levels closely. Consider alternative diuretic. Ensure adequate hydration.",
                ["Lexicomp", "Micromedex"]
            )
        ]
        
        # Build interaction lookup
        for interaction in interactions:
            # Add for drug1
            if interaction.drug1 not in self.interaction_database:
                self.interaction_database[interaction.drug1] = []
            self.interaction_database[interaction.drug1].append(interaction)
            
            # Add for drug2 if present
            if interaction.drug2:
                if interaction.drug2 not in self.interaction_database:
                    self.interaction_database[interaction.drug2] = []
                self.interaction_database[interaction.drug2].append(interaction)
        
        # Allergy cross-sensitivities
        self.allergy_database = {
            'penicillin': ['amoxicillin', 'ampicillin', 'piperacillin', 'nafcillin'],
            'sulfa': ['sulfamethoxazole', 'sulfasalazine', 'sulfadiazine'],
            'aspirin': ['ibuprofen', 'naproxen', 'ketorolac', 'diclofenac']
        }
        
        # Pregnancy categories
        self.pregnancy_categories = {
            'warfarin': 'X',  # Contraindicated
            'lisinopril': 'D',  # Positive evidence of risk
            'methotrexate': 'X',  # Contraindicated
            'lithium': 'D',  # Positive evidence of risk
            'acetaminophen': 'B',  # No evidence of risk
            'amoxicillin': 'B',  # No evidence of risk
        }
        
        logger.info(f"Loaded {len(interactions)} drug interactions")
    
    def check_drug_drug_interactions(
        self,
        medications: List[str]
    ) -> List[DrugInteraction]:
        """Check for drug-drug interactions"""
        interactions = []
        
        # Normalize drug names
        meds = [med.lower().strip() for med in medications]
        
        # Check each pair
        for i, med1 in enumerate(meds):
            for med2 in meds[i+1:]:
                # Check if interaction exists
                if med1 in self.interaction_database:
                    for interaction in self.interaction_database[med1]:
                        if interaction.drug2 and interaction.drug2.lower() == med2:
                            interactions.append(interaction)
        
        return interactions
    
    def check_drug_allergy_interactions(
        self,
        medication: str,
        allergies: List[str]
    ) -> List[DrugInteraction]:
        """Check for drug-allergy interactions"""
        interactions = []
        med = medication.lower().strip()
        
        for allergy in allergies:
            allergy = allergy.lower().strip()
            
            # Direct match
            if med == allergy:
                interactions.append(DrugInteraction(
                    f"ALLERGY_{med}",
                    InteractionType.DRUG_ALLERGY,
                    InteractionSeverity.CONTRAINDICATED,
                    med,
                    None,
                    f"Patient has documented allergy to {med}",
                    "Allergic reaction: rash, anaphylaxis, angioedema",
                    "Do not administer. Use alternative medication.",
                    ["Patient Chart"]
                ))
            
            # Cross-sensitivity
            elif allergy in self.allergy_database:
                if med in self.allergy_database[allergy]:
                    interactions.append(DrugInteraction(
                        f"CROSS_ALLERGY_{allergy}_{med}",
                        InteractionType.DRUG_ALLERGY,
                        InteractionSeverity.MAJOR,
                        med,
                        None,
                        f"Cross-sensitivity: Patient allergic to {allergy}, {med} may cause reaction",
                        "Possible allergic reaction due to cross-sensitivity",
                        "Use with extreme caution or avoid. Consider alternative medication.",
                        ["Allergy Database"]
                    ))
        
        return interactions
    
    def check_duplicate_therapy(
        self,
        medications: List[str]
    ) -> List[DrugInteraction]:
        """Check for duplicate therapy"""
        interactions = []
        
        # Drug classes
        drug_classes = {
            'ace_inhibitors': ['lisinopril', 'enalapril', 'ramipril'],
            'statins': ['atorvastatin', 'simvastatin', 'rosuvastatin'],
            'ssris': ['fluoxetine', 'sertraline', 'escitalopram'],
            'ppis': ['omeprazole', 'pantoprazole', 'esomeprazole'],
            'nsaids': ['ibuprofen', 'naproxen', 'diclofenac']
        }
        
        meds = [med.lower().strip() for med in medications]
        
        for class_name, class_drugs in drug_classes.items():
            duplicates = [med for med in meds if med in class_drugs]
            if len(duplicates) > 1:
                interactions.append(DrugInteraction(
                    f"DUP_{class_name}",
                    InteractionType.DUPLICATE_THERAPY,
                    InteractionSeverity.MODERATE,
                    duplicates[0],
                    duplicates[1] if len(duplicates) > 1 else None,
                    f"Duplicate therapy: Multiple {class_name.replace('_', ' ')}",
                    "Increased risk of adverse effects, unnecessary cost",
                    f"Review indication for multiple {class_name.replace('_', ' ')}. Discontinue one if appropriate.",
                    ["Clinical Guidelines"]
                ))
        
        return interactions
    
    def check_pregnancy_safety(
        self,
        medication: str,
        is_pregnant: bool
    ) -> Optional[DrugInteraction]:
        """Check pregnancy safety"""
        if not is_pregnant:
            return None
        
        med = medication.lower().strip()
        category = self.pregnancy_categories.get(med)
        
        if category in ['D', 'X']:
            severity = (InteractionSeverity.CONTRAINDICATED if category == 'X' 
                       else InteractionSeverity.MAJOR)
            
            return DrugInteraction(
                f"PREG_{med}",
                InteractionType.PREGNANCY,
                severity,
                med,
                None,
                f"Pregnancy Category {category}: Risk to fetus",
                "Potential fetal harm, teratogenic effects" if category == 'X' else "Evidence of fetal risk",
                "Avoid in pregnancy" if category == 'X' else "Use only if benefit outweighs risk",
                ["FDA Pregnancy Categories"]
            )
        
        return None
    
    def check_renal_adjustment(
        self,
        medication: str,
        creatinine_clearance: float
    ) -> Optional[DrugInteraction]:
        """Check if renal dose adjustment needed"""
        # Drugs requiring renal adjustment
        renal_drugs = {
            'metformin': {'threshold': 30, 'action': 'Contraindicated if CrCl < 30 mL/min'},
            'gabapentin': {'threshold': 60, 'action': 'Reduce dose if CrCl < 60 mL/min'},
            'enoxaparin': {'threshold': 30, 'action': 'Reduce dose if CrCl < 30 mL/min'},
            'digoxin': {'threshold': 50, 'action': 'Reduce dose if CrCl < 50 mL/min'}
        }
        
        med = medication.lower().strip()
        
        if med in renal_drugs:
            drug_info = renal_drugs[med]
            if creatinine_clearance < drug_info['threshold']:
                return DrugInteraction(
                    f"RENAL_{med}",
                    InteractionType.RENAL_ADJUSTMENT,
                    InteractionSeverity.MAJOR,
                    med,
                    None,
                    f"Renal dose adjustment required (CrCl: {creatinine_clearance} mL/min)",
                    "Risk of drug accumulation and toxicity",
                    drug_info['action'],
                    ["Renal Dosing Guidelines"]
                )
        
        return None
    
    def comprehensive_check(
        self,
        new_medication: str,
        current_medications: List[str],
        allergies: List[str],
        is_pregnant: bool = False,
        creatinine_clearance: Optional[float] = None
    ) -> Dict[str, Any]:
        """Comprehensive medication safety check"""
        all_interactions = []
        
        # Drug-drug interactions
        all_meds = current_medications + [new_medication]
        drug_drug = self.check_drug_drug_interactions(all_meds)
        all_interactions.extend(drug_drug)
        
        # Drug-allergy interactions
        drug_allergy = self.check_drug_allergy_interactions(new_medication, allergies)
        all_interactions.extend(drug_allergy)
        
        # Duplicate therapy
        duplicate = self.check_duplicate_therapy(all_meds)
        all_interactions.extend(duplicate)
        
        # Pregnancy safety
        if is_pregnant:
            pregnancy = self.check_pregnancy_safety(new_medication, is_pregnant)
            if pregnancy:
                all_interactions.append(pregnancy)
        
        # Renal adjustment
        if creatinine_clearance is not None:
            renal = self.check_renal_adjustment(new_medication, creatinine_clearance)
            if renal:
                all_interactions.append(renal)
        
        # Categorize by severity
        contraindicated = [i for i in all_interactions if i.severity == InteractionSeverity.CONTRAINDICATED]
        major = [i for i in all_interactions if i.severity == InteractionSeverity.MAJOR]
        moderate = [i for i in all_interactions if i.severity == InteractionSeverity.MODERATE]
        minor = [i for i in all_interactions if i.severity == InteractionSeverity.MINOR]
        
        # Determine overall safety
        if contraindicated:
            safety_status = "CONTRAINDICATED"
            recommendation = "DO NOT PRESCRIBE - Contraindicated interactions detected"
        elif major:
            safety_status = "MAJOR_CONCERNS"
            recommendation = "CAUTION - Major interactions detected. Review carefully before prescribing."
        elif moderate:
            safety_status = "MODERATE_CONCERNS"
            recommendation = "MONITOR - Moderate interactions detected. Monitor patient closely."
        elif minor:
            safety_status = "MINOR_CONCERNS"
            recommendation = "SAFE - Only minor interactions. Proceed with standard monitoring."
        else:
            safety_status = "SAFE"
            recommendation = "SAFE - No significant interactions detected."
        
        return {
            'medication': new_medication,
            'safety_status': safety_status,
            'recommendation': recommendation,
            'total_interactions': len(all_interactions),
            'interactions_by_severity': {
                'contraindicated': len(contraindicated),
                'major': len(major),
                'moderate': len(moderate),
                'minor': len(minor)
            },
            'interactions': [i.to_dict() for i in all_interactions],
            'checked_at': datetime.utcnow().isoformat()
        }


# Global drug checker instance
drug_checker = DrugInteractionChecker()