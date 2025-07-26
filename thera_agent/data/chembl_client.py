"""
Async ChEMBL API client with data normalization
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from .http_client import get_http_client

class ChEMBLClient:
    """Async ChEMBL API client with enhanced data normalization"""
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/chembl/api/data"
    
    async def get_targets(self, gene_symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get ChEMBL targets for gene symbol"""
        client = await get_http_client()
        
        url = f"{self.base_url}/target.json"
        params = {
            "target_synonym__icontains": gene_symbol,
            "format": "json",
            "limit": limit
        }
        
        try:
            response = await client.get(url, params=params)
            return response.get("targets", [])
        except Exception as e:
            print(f"ChEMBL target search error: {e}")
            return []
    
    async def get_activities(self, target_chembl_id: str, 
                           standard_types: List[str] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get normalized activities for target"""
        client = await get_http_client()
        
        # Default to common binding assays
        if standard_types is None:
            standard_types = ["IC50", "Ki", "Kd", "EC50"]
        
        url = f"{self.base_url}/activity.json"
        params = {
            "target_chembl_id": target_chembl_id,
            "standard_type__in": ",".join(standard_types),
            "standard_units": "nM",  # Normalize to nM
            "format": "json",
            "limit": limit
        }
        
        try:
            response = await client.get(url, params=params)
            activities = response.get("activities", [])
            
            # Normalize and validate activities
            normalized_activities = []
            for activity in activities:
                normalized = self._normalize_activity(activity)
                if normalized:
                    normalized_activities.append(normalized)
            
            # Sort by potency (ascending)
            normalized_activities.sort(key=lambda x: x.get("standard_value_nm", float('inf')))
            
            return normalized_activities
            
        except Exception as e:
            print(f"ChEMBL activity search error: {e}")
            return []
    
    def _normalize_activity(self, activity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize and validate activity data"""
        try:
            # Extract key fields
            standard_value = activity.get("standard_value")
            standard_units = activity.get("standard_units", "").upper()
            standard_type = activity.get("standard_type", "")
            
            # Skip if missing critical data
            if not standard_value or not standard_type:
                return None
            
            # Convert to nM
            value_nm = self._convert_to_nm(float(standard_value), standard_units)
            if value_nm is None:
                return None
            
            # Extract assay metadata for quality assessment
            assay_data = activity.get("assay_description", "")
            assay_type = activity.get("assay_type", "")
            
            # Quality score based on assay type and data completeness
            quality_score = self._calculate_quality_score(activity)
            
            return {
                "activity_id": activity.get("activity_id"),
                "molecule_chembl_id": activity.get("molecule_chembl_id"),
                "standard_type": standard_type,
                "standard_value_nm": value_nm,
                "assay_description": assay_data,
                "assay_type": assay_type,
                "assay_organism": activity.get("assay_organism"),
                "quality_score": quality_score,
                "confidence_score": activity.get("confidence_score"),
                "pchembl_value": activity.get("pchembl_value"),  # -log10(IC50 in M)
                "data_validity_comment": activity.get("data_validity_comment")
            }
            
        except (ValueError, TypeError) as e:
            print(f"Error normalizing activity: {e}")
            return None
    
    def _convert_to_nm(self, value: float, units: str) -> Optional[float]:
        """Convert concentration to nM"""
        conversion_factors = {
            "NM": 1.0,
            "UM": 1000.0,
            "MM": 1_000_000.0,
            "M": 1_000_000_000.0,
            "PM": 0.001,
            "FM": 0.000001
        }
        
        units_clean = units.replace("μ", "U").upper()  # Handle μM
        
        if units_clean in conversion_factors:
            return value * conversion_factors[units_clean]
        
        return None
    
    def _calculate_quality_score(self, activity: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)"""
        score = 0.5  # Base score
        
        # Bonus for complete data
        if activity.get("pchembl_value"):
            score += 0.2
        
        if activity.get("confidence_score"):
            conf_score = activity.get("confidence_score", 0)
            score += (conf_score / 10) * 0.2  # Normalize confidence score
        
        # Bonus for functional assays
        assay_type = activity.get("assay_type", "").lower()
        if "functional" in assay_type or "cell" in assay_type:
            score += 0.1
        
        # Penalty for data validity issues
        validity_comment = activity.get("data_validity_comment", "")
        if validity_comment and "outside typical range" in validity_comment.lower():
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def get_molecules(self, chembl_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get molecule data for ChEMBL IDs"""
        client = await get_http_client()
        
        molecules = {}
        
        # Batch requests for efficiency
        for i in range(0, len(chembl_ids), 20):  # Process in batches of 20
            batch_ids = chembl_ids[i:i+20]
            
            url = f"{self.base_url}/molecule.json"
            params = {
                "molecule_chembl_id__in": ",".join(batch_ids),
                "format": "json"
            }
            
            try:
                response = await client.get(url, params=params)
                batch_molecules = response.get("molecules", [])
                
                for mol in batch_molecules:
                    chembl_id = mol.get("molecule_chembl_id")
                    if chembl_id:
                        molecules[chembl_id] = {
                            "preferred_name": mol.get("pref_name"),
                            "molecular_weight": mol.get("molecule_properties", {}).get("mw_freebase"),
                            "alogp": mol.get("molecule_properties", {}).get("alogp"),
                            "hbd": mol.get("molecule_properties", {}).get("hbd"),
                            "hba": mol.get("molecule_properties", {}).get("hba"),
                            "max_phase": mol.get("max_phase"),  # Clinical phase
                            "structure_type": mol.get("structure_type"),
                            "smiles": mol.get("molecule_structures", {}).get("canonical_smiles") if mol.get("molecule_structures") else None
                        }
                        
            except Exception as e:
                print(f"Error fetching molecule batch: {e}")
                continue
        
        return molecules
    
    async def get_inhibitors_for_target(self, gene_symbol: str, 
                                      max_ic50_nm: Optional[float] = None,
                                      min_ic50_nm: Optional[float] = None,
                                      limit: int = 50) -> List[Dict[str, Any]]:
        """Get normalized inhibitors for target with potency filtering"""
        
        # Get targets
        targets = await self.get_targets(gene_symbol)
        if not targets:
            return []
        
        all_inhibitors = []
        
        for target in targets[:3]:  # Top 3 targets to avoid overwhelming
            target_id = target.get("target_chembl_id")
            if not target_id:
                continue
                
            # Get activities
            activities = await self.get_activities(target_id, limit=limit)
            
            # Filter by potency
            filtered_activities = []
            for activity in activities:
                ic50_nm = activity.get("standard_value_nm")
                if ic50_nm is None:
                    continue
                    
                if max_ic50_nm and ic50_nm > max_ic50_nm:
                    continue
                    
                if min_ic50_nm and ic50_nm < min_ic50_nm:
                    continue
                    
                filtered_activities.append(activity)
            
            # Get molecule details
            chembl_ids = [act.get("molecule_chembl_id") for act in filtered_activities if act.get("molecule_chembl_id")]
            molecules = await self.get_molecules(chembl_ids)
            
            # Combine activity and molecule data
            for activity in filtered_activities:
                chembl_id = activity.get("molecule_chembl_id")
                molecule_data = molecules.get(chembl_id, {})
                
                inhibitor = {
                    **activity,
                    "target_chembl_id": target_id,
                    "target_name": target.get("pref_name"),
                    **molecule_data
                }
                
                all_inhibitors.append(inhibitor)
        
        # Sort by quality score and potency
        all_inhibitors.sort(key=lambda x: (-x.get("quality_score", 0), x.get("standard_value_nm", float('inf'))))
        
        return all_inhibitors[:limit]
