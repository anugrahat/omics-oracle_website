"""
LLM-Powered Result Summarizer for Therapeutic Target Discovery
Beautifully analyzes and presents JSON results using GPT-4 intelligence
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from tabulate import tabulate
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TherapeuticResultSummarizer:
    """LLM-powered intelligent summarization of therapeutic target results"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def summarize_results(self, json_file: str, query: str) -> str:
        """
        Generate beautiful LLM-powered summary of therapeutic target results
        
        Args:
            json_file: Path to JSON results file
            query: Original user query
            
        Returns:
            Formatted summary string with tables, insights, and analysis
        """
        try:
            # Load results
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if self.openai_api_key:
                summary = await self._llm_summarize(data, query)
            else:
                summary = self._fallback_summarize(data, query)
                
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing results: {e}")
            return self._fallback_summarize(data, query)
    
    async def _llm_summarize(self, data: Dict[str, Any], query: str) -> str:
        """Use GPT-4 to intelligently analyze and summarize results"""
        
        # Prepare structured data for LLM
        summary_data = self._prepare_data_for_llm(data)
        
        prompt = f"""
You are a world-class pharmaceutical researcher and drug discovery expert writing for a professional audience.
Analyze the therapeutic target discovery results and provide an intelligent clinical analysis.

ORIGINAL QUERY: "{query}"

ANALYSIS DATA:
{json.dumps(summary_data, indent=2)}

Provide a comprehensive clinical analysis in markdown format with these sections:

## 🎯 Executive Summary
Provide 2-3 sentences highlighting the most significant findings and therapeutic opportunities.

## 🧬 Target Analysis & Druggability Assessment
For each target, analyze:
- **Biological relevance** to the disease/indication
- **Druggability factors** (structure availability, binding sites, etc.)
- **Therapeutic potential** and development opportunities
- **Existing clinical precedent** or competitive landscape

## 💊 Lead Compound Assessment
Analyze the most promising inhibitors focusing on:
- **Potency analysis** (IC50 values and significance)
- **Selectivity considerations** 
- **Drug-like properties** and development potential
- **Structure-activity relationships** where relevant

## 🏥 Clinical Development Perspective
Provide strategic insights on:
- **Priority targets** for further investigation
- **Development timelines** and regulatory considerations  
- **Market opportunities** and competitive landscape
- **Key risks** and mitigation strategies

## 🔬 Research Recommendations
Suggest specific next steps:
- **Optimization strategies** for lead compounds
- **Additional studies** needed (PK/PD, toxicity, etc.)
- **Partnership opportunities** or licensing considerations

Write in professional pharmaceutical industry language, focus on actionable insights, and provide specific recommendations.
DO NOT create ASCII tables - use clear prose and bullet points instead.
"""

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a therapeutic target discovery expert and scientific writer. Create beautiful, comprehensive summaries with proper formatting for terminal display."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"LLM summarization failed: {e}")
            return self._fallback_summarize(data, query)
    
    def _prepare_data_for_llm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data for LLM analysis"""
        
        summary_data = {
            "query_type": data.get("query_type", "unknown"),
            "total_targets": len(data.get("targets", [])),
            "targets": []
        }
        
        for target in data.get("targets", []):
            target_summary = {
                "gene_symbol": target.get("gene_symbol", "Unknown"),
                "target_score": target.get("target_score", 0),
                "inhibitor_count": len(target.get("inhibitors", [])),
                "structure_count": len(target.get("structures", [])),
                "literature_count": len(target.get("literature", [])),
                "best_inhibitor": None,
                "best_structure": None
            }
            
            # Find best inhibitor
            inhibitors = target.get("inhibitors", [])
            if inhibitors:
                best = min(inhibitors, key=lambda x: x.get("standard_value_nm", float('inf')))
                target_summary["best_inhibitor"] = {
                    "chembl_id": best.get("molecule_chembl_id", "Unknown"),
                    "ic50_nm": best.get("standard_value_nm", "N/A"),
                    "assay_type": best.get("assay_type", "Unknown")
                }
            
            # Find best structure
            structures = target.get("structures", [])
            if structures:
                best_struct = structures[0]  # Already sorted by quality in agent
                target_summary["best_structure"] = {
                    "pdb_id": best_struct.get("pdb_id", "Unknown"),
                    "resolution": best_struct.get("resolution", "N/A"),
                    "method": best_struct.get("experimental_method", "Unknown")
                }
            
            summary_data["targets"].append(target_summary)
        
        return summary_data
    
    def _fallback_summarize(self, data: Dict[str, Any], query: str) -> str:
        """Fallback summary without LLM (still formatted nicely)"""
        
        targets = data.get("targets", [])
        if not targets:
            return "❌ No targets found for this query."
        
        summary = []
        summary.append("🧬 THERAPEUTIC TARGET DISCOVERY RESULTS")
        summary.append("=" * 60)
        summary.append(f"📝 Query: {query}")
        summary.append(f"🎯 Targets analyzed: {len(targets)}")
        summary.append("")
        
        # Create target table
        table_data = []
        for target in targets:
            symbol = target.get("gene_symbol", "Unknown")
            score = target.get("target_score", 0)
            inhibitors = len(target.get("inhibitors", []))
            structures = len(target.get("structures", []))
            
            # Determine status
            if score >= 8.0:
                status = "Excellent ⭐⭐⭐"
            elif score >= 6.5:
                status = "Good ⭐⭐"
            elif score >= 5.0:
                status = "Moderate ⭐"
            else:
                status = "Challenging"
            
            table_data.append([symbol, f"{score:.1f}", inhibitors, structures, status])
        
        summary.append("📊 TARGET RANKING:")
        summary.append("")
        summary.append(tabulate(
            table_data,
            headers=["Target", "Score", "Inhibitors", "Structures", "Assessment"],
            tablefmt="grid",
            stralign="center"
        ))
        summary.append("")
        
        # Top inhibitors
        all_inhibitors = []
        for target in targets:
            for inh in target.get("inhibitors", []):
                if inh.get("standard_value_nm"):
                    all_inhibitors.append({
                        "target": target.get("gene_symbol", "Unknown"),
                        "chembl_id": inh.get("molecule_chembl_id", "Unknown"),
                        "ic50": inh.get("standard_value_nm", float('inf'))
                    })
        
        if all_inhibitors:
            all_inhibitors.sort(key=lambda x: x["ic50"])
            summary.append("💊 TOP INHIBITORS:")
            for i, inh in enumerate(all_inhibitors[:5], 1):
                summary.append(f"   {i}. {inh['chembl_id']} ({inh['target']}): {inh['ic50']} nM")
            
        summary.append("")
        summary.append("✅ Analysis complete!")
        
        return "\n".join(summary)

# Create global instance
result_summarizer = TherapeuticResultSummarizer()
