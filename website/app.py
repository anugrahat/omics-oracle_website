"""
🧬 Omics Oracle: Streamlit Web Interface
AI-powered therapeutic target discovery for hiring managers and recruiters
"""

import streamlit as st
import asyncio
import json
import os
import sys
from datetime import datetime
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your agent components
from thera_agent.agent import TherapeuticTargetAgent
from thera_agent.query_parser import QueryParser
from thera_agent.disease_mapper import DiseaseTargetMapper
from thera_agent.result_summarizer import result_summarizer

# Try to import analytics, but don't fail if it's not available
try:
    from analytics import UsageTracker
except ImportError:
    # Fallback analytics class for deployment
    class UsageTracker:
        def __init__(self):
            pass
        def track_query(self, *args, **kwargs):
            pass
        def get_stats(self):
            return {"total_queries": 0, "unique_users": 0}
import time
import uuid

# Page configuration
st.set_page_config(
    page_title="🧬 Omics Oracle - AI Drug Discovery Demo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert > div {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧬 Omics Oracle: AI-Powered Therapeutic Target Discovery</h1>
    <p>Professional drug discovery platform for pharmaceutical companies and biotech startups</p>
</div>
""", unsafe_allow_html=True)

# Initialize analytics tracker and session
if 'tracker' not in st.session_state:
    st.session_state.tracker = UsageTracker()
    st.session_state.session_id = str(uuid.uuid4())[:8]
    st.session_state.query_count = 0  # Track free queries used
    st.session_state.user_api_key = None  # User's own API key

# Get OpenAI key from environment (hidden from users)
provided_openai_key = os.getenv('OPENAI_API_KEY')

# Determine which API key to use
user_provided_key = st.session_state.get('user_api_key')
openai_key = user_provided_key if user_provided_key else provided_openai_key

# Sidebar for API options and usage
with st.sidebar:
    st.title("🎆 Usage Options")
    
    # Show current usage mode
    if user_provided_key:
        st.success("🔑 **Using your API key** - Unlimited queries!")
    else:
        remaining = max(0, 3 - st.session_state.query_count)
        if remaining > 0:
            st.info(f"🆓 **Free Demo**: {remaining}/3 queries remaining")
        else:
            st.warning("🚫 **Free queries used up!** Get your own API key below.")
    
    st.markdown("---")
    
    # API Key input option
    st.subheader("🔓 Unlimited Access")
    
    with st.expander("🔑 Use Your Own OpenAI API Key", expanded=not bool(user_provided_key)):
        user_key_input = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            value=user_provided_key or "",
            help="Get unlimited queries with your own key!"
        )
        
        if st.button("🚀 Activate Key"):
            if user_key_input.startswith("sk-"):
                st.session_state.user_api_key = user_key_input
                st.success("✅ API key activated! Unlimited queries now available.")
                st.rerun()
            else:
                st.error("❌ Invalid API key format. Should start with 'sk-'")
        
        if user_provided_key and st.button("🔄 Switch to Free Mode"):
            st.session_state.user_api_key = None
            st.info("Switched back to free mode (3 queries max)")
            st.rerun()
    
    # Instructions for getting API key
    st.subheader("📝 How to Get OpenAI API Key")
    st.markdown("""
    **Step-by-step:**
    1. 🌐 Visit [platform.openai.com](https://platform.openai.com)
    2. 📝 Create account or sign in
    3. 🔑 Go to API Keys section
    4. ➕ Create new secret key
    5. 📋 Copy and paste above
    """)
    
    st.markdown("---")
    
    st.title("📋 Quick Start Examples")
    
    example_queries = [
        "Find druggable candidates for Alzheimer's disease",
        "Find potent inhibitors for COPD targets",
        "Type 2 diabetes therapeutic targets", 
        "EGFR inhibitors under 50 nM IC50",
        "Parkinson's disease drug targets",
        "JAK2 and BRAF cancer targets",
        "Find inhibitors for inflammatory bowel disease",
        "Oncology targets with structural data"
    ]
    
    st.markdown("**Click to try these examples:**")
    for i, example in enumerate(example_queries):
        if st.button(f"📋 {example}", key=f"example_{i}"):
            st.session_state.selected_query = example
            st.rerun()

    st.markdown("---")
    
    st.title("ℹ️ About")
    st.markdown("""
    **Omics Oracle** is an advanced RAG system that:
    
    - 🤖 **Uses GPT-4** for intelligent parsing
    - 📊 **Integrates 3 databases**: PubMed + ChEMBL + PDB
    - 🎯 **Discovers targets** from disease names
    - 💊 **Finds inhibitors** with IC50 filtering
    - 📋 **Generates clinical insights**
    
    **Perfect for:**
    - Pharmaceutical companies
    - Biotech startups  
    - Academic research
    - Drug discovery teams
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎯 Drug Target Discovery Query")
    
    # Query input - preserve user's query during analysis
    # Initialize query_input in session state if not present
    if 'query_input' not in st.session_state:
        if 'selected_query' in st.session_state:
            # User clicked an example query from sidebar
            st.session_state.query_input = st.session_state.selected_query
            del st.session_state.selected_query
        else:
            # Show example for new users
            st.session_state.query_input = "Find druggable candidates for Alzheimer's disease"
    elif 'selected_query' in st.session_state:
        # Update with new example query
        st.session_state.query_input = st.session_state.selected_query
        del st.session_state.selected_query
    
    query = st.text_area(
        "Enter your therapeutic target query:",
        height=100,
        help="💡 Click examples in sidebar or try: 'COPD inhibitors', 'Parkinson targets', 'EGFR under 50 nM'",
        key="query_input"
    )
    
    # Run button
    run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    # Clear previous results when starting new analysis
    if run_analysis:
        # Clear previous results to avoid confusion
        if 'current_query' in st.session_state:
            del st.session_state['current_query']
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']
        # Set new query
        st.session_state.current_query = query.strip()

with col2:
    st.title("🏆 Features Demo")
    
    st.info("""
    **🧠 AI Features:**
    - Natural language parsing
    - Disease-to-target mapping  
    - IC50 range detection
    - Clinical recommendations
    """)
    
    st.success("""
    **📊 Data Sources:**
    - PubMed (35M+ papers)
    - ChEMBL (2M+ compounds)
    - RCSB PDB (200K+ structures)
    """)

# Results section
if run_analysis:
    # Check if API key is available
    if not openai_key:
        st.error("⚠️ Demo temporarily unavailable. Please check back later.")
        st.stop()
    
    # Check query limits for free users
    if not user_provided_key and st.session_state.query_count >= 3:
        st.error("🚫 **Free query limit reached!** You've used all 3 free queries.")
        st.markdown("""
        ### 🚀 **Upgrade for Unlimited Access**
        
        **Get your own OpenAI API key for:**
        - ♾️ **Unlimited queries**
        - ⚡ **Faster processing** (dedicated resources)
        - 🔒 **Your data stays private** (your own API account)
        - 💰 **Only ~$0.10-0.50 per query**
        
        👆 **Enter your API key in the sidebar to continue!**
        """)
        st.stop()
    
    if not query.strip():
        st.error("⚠️ Please enter a query to analyze.")
        st.stop()
    
    # Ensure we're processing the current query (prevent confusion from multiple submissions)
    if hasattr(st.session_state, 'current_query') and st.session_state.current_query != query.strip():
        st.warning("⚠️ Query changed during analysis. Please click 'Run Analysis' again for the new query.")
        st.stop()
    
    # Track query start
    start_time = time.time()
    user_id = st.session_state.session_id
    
    # Set the API key for the session (from environment)
    os.environ["OPENAI_API_KEY"] = openai_key
    
    st.markdown("---")
    st.title("📊 Analysis Results")
    
    # Enhanced progress indicators with detailed steps
    progress_bar = st.progress(0)
    status_text = st.empty()
    detailed_status = st.empty()
    
    # Progress tracking function
    def update_progress(step, message, details=""):
        progress = int((step / 10) * 100)
        progress_bar.progress(progress)
        status_text.text(f"🔄 Step {step}/10: {message}")
        if details:
            detailed_status.info(f"🔍 **Details:** {details}")
        time.sleep(0.2)  # Brief pause for better UX
    
    try:
        # Step 1: Initialize the agent
        update_progress(1, "Initializing AI agent...", "Loading therapeutic target discovery modules")
        agent = TherapeuticTargetAgent()
        
        # Step 2: Parse query with GPT-4
        update_progress(2, "Parsing query with GPT-4...", "Converting natural language to search parameters")
        
        # Create a wrapper to run async function with detailed progress
        async def run_analysis():
            # Parse the query first to determine if it's single or multi-target
            parser = QueryParser()
            try:
                # Step 3: Advanced query parsing
                update_progress(3, "Analyzing query structure...", "Identifying targets and filtering parameters")
                parsed = await parser.parse_query(query)
                
                # Step 4: Database preparation 
                update_progress(4, "Preparing database connections...", "Connecting to PubMed, ChEMBL, and PDB APIs")
                if len(parsed.gene_symbols) == 1:
                    # Single target analysis
                    update_progress(5, "Searching PubMed literature...", f"Finding research papers for {parsed.gene_symbols[0]}")
                    update_progress(6, "Querying ChEMBL database...", "Retrieving inhibitor and bioactivity data")
                    update_progress(7, "Fetching PDB structures...", "Downloading protein structure information")
                    result = await agent.analyze_target(
                        parsed.gene_symbols[0],
                        max_ic50_nm=parsed.max_ic50_nm,
                        min_ic50_nm=parsed.min_ic50_nm
                    )
                    update_progress(8, "Processing inhibitor data...", "Analyzing bioactivity and potency data")
                    return result
                elif len(parsed.gene_symbols) > 1:
                    # Multi-target analysis
                    update_progress(5, "Searching PubMed literature...", f"Finding papers for {len(parsed.gene_symbols)} targets")
                    update_progress(6, "Querying ChEMBL database...", "Retrieving inhibitor data for all targets")
                    update_progress(7, "Fetching PDB structures...", "Downloading protein structures for comparison")
                    result = await agent.multi_target_analysis(
                        parsed.gene_symbols,
                        max_ic50_nm=parsed.max_ic50_nm,
                        min_ic50_nm=parsed.min_ic50_nm
                    )
                    update_progress(8, "Processing inhibitor data...", "Comparing bioactivity across targets")
                    return result
                else:
                    # Disease query - use disease mapper
                    from thera_agent.disease_mapper import DiseaseTargetMapper
                    mapper = DiseaseTargetMapper()
                    targets = await mapper.map_disease_to_targets(query, max_targets=5)
                    if targets:
                        gene_symbols = [t.gene_symbol for t in targets]
                        return await agent.multi_target_analysis(gene_symbols)
                    else:
                        return {"error": "No targets found for this disease"}
            except Exception as parse_error:
                # Fallback: treat as single gene symbol
                return await agent.analyze_target(query)
        
        # Step 9: Run the analysis with final progress updates
        update_progress(9, "Calculating target scores...", "Evaluating druggability and therapeutic potential")
        
        # Use asyncio to run the async function
        results = asyncio.run(run_analysis())
        
        # Step 10: Final completion
        update_progress(10, "Analysis complete!", "Formatting results and generating summary")
        time.sleep(0.5)  # Let users see completion
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        detailed_status.empty()
        
        # Display results
        if results and not results.get("error"):
            # Handle both single target and multi-target results
            if "targets" in results:
                # Multi-target results
                targets = results["targets"]
            elif "gene_symbol" in results:
                # Single target results - wrap in list
                targets = [results]
            else:
                targets = []
            
            if targets:
                st.success("✅ Analysis completed successfully!")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                total_inhibitors = sum(len(t.get("inhibitors", [])) for t in targets)
                total_structures = sum(len(t.get("structures", [])) for t in targets)
                
                with col1:
                    st.metric("🎯 Targets Found", len(targets))
                with col2:
                    st.metric("💊 Total Inhibitors", total_inhibitors)
                with col3:
                    st.metric("🧬 Total Structures", total_structures)
                
                # Target summary table
                st.subheader("🏆 Target Ranking")
                
                table_data = []
                for target in targets:
                    # Get top PDB IDs
                    structures = target.get("structures", [])
                    top_pdbs = ", ".join([s.get("pdb_id", "N/A") for s in structures[:3]]) if structures else "None"
                    
                    # Get best inhibitor IC50
                    inhibitors = target.get("inhibitors", [])
                    best_ic50 = "N/A"
                    if inhibitors:
                        sorted_inhibitors = sorted([i for i in inhibitors if i.get("standard_value_nm")], 
                                                 key=lambda x: float(x.get("standard_value_nm", float('inf'))))
                        if sorted_inhibitors:
                            best_ic50 = f"{sorted_inhibitors[0].get('standard_value_nm', 'N/A'):.2f} nM"
                    
                    table_data.append({
                        "Target": target.get("gene_symbol", "Unknown"),
                        "Best IC50": best_ic50,
                        "Inhibitors": len(inhibitors),
                        "PDB Structures": f"{len(structures)} ({top_pdbs})",
                        "Literature": len(target.get("literature", []))
                    })
                
                df = pd.DataFrame(table_data)
                # Use styled dataframe for better formatting
                st.dataframe(
                    df, 
                    use_container_width=True,
                    column_config={
                        "Target": st.column_config.TextColumn("🎯 Target", width="medium"),
                        "Best IC50": st.column_config.TextColumn("💊 Best IC50", width="medium"),
                        "Inhibitors": st.column_config.NumberColumn("🧨 Inhibitors", width="small"),
                        "PDB Structures": st.column_config.TextColumn("🧬 PDB (Top 3)", width="large"),
                        "Literature": st.column_config.NumberColumn("📜 Papers", width="small")
                    }
                )
                
                # Top inhibitors
                st.subheader("💊 Top Inhibitors (Filtered)")
                
                # Check if we have IC50 table data (single target) or need to aggregate (multi-target)
                if "ic50_table" in results:
                    # Single target - use the IC50 table which respects filters
                    ic50_data = results["ic50_table"]
                    if ic50_data:
                        all_inhibitors = []
                        for i, row in enumerate(ic50_data[:10]):
                            all_inhibitors.append({
                                "Rank": "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}⃣",
                                "ChEMBL ID": row["chembl_id"],
                                "Target": results.get("gene_symbol", "Unknown"),
                                "IC50": row["ic50_display"],
                                "Assay Type": row["assay_type"],
                                "Phase": row.get("max_phase", "Preclinical")
                            })
                        inhibitor_df = pd.DataFrame(all_inhibitors)
                    else:
                        st.info("No inhibitors found matching the specified criteria.")
                        inhibitor_df = None
                else:
                    # Multi-target - aggregate IC50 tables from each target
                    all_inhibitors = []
                    for target in targets:
                        if "ic50_table" in target and target["ic50_table"]:
                            for row in target["ic50_table"][:5]:  # Top 5 per target
                                all_inhibitors.append({
                                    "ChEMBL ID": row["chembl_id"],
                                    "Target": target.get("gene_symbol", "Unknown"),
                                    "IC50": row["ic50_display"],
                                    "ic50_nm": row.get("ic50_nm", float('inf')),  # Add numeric value for sorting
                                    "Assay Type": row["assay_type"],
                                    "Phase": row.get("max_phase") or "Preclinical"
                                })
                    
                    if all_inhibitors:
                        # Sort by IC50 value for ranking
                        all_inhibitors.sort(key=lambda x: x.get("ic50_nm", float('inf')))
                        # Add ranking
                        for i, inhibitor in enumerate(all_inhibitors[:10]):
                            inhibitor["Rank"] = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}⃣"
                        # Create dataframe without internal sorting field
                        display_inhibitors = [{k: v for k, v in inh.items() if k != 'ic50_nm'} for inh in all_inhibitors[:10]]
                        inhibitor_df = pd.DataFrame(display_inhibitors)
                    else:
                        st.info("No inhibitors found matching the specified criteria.")
                        inhibitor_df = None
                
                if inhibitor_df is not None:
                    # Display the dataframe
                    st.dataframe(inhibitor_df, use_container_width=True)
                
                # Generate AI summary with progress tracking
                st.subheader("🎯 Target Identification Overview")
                
                # AI Summary progress indicator
                ai_progress = st.progress(0)
                ai_status = st.empty()
                
                ai_status.info("🤖 **Generating intelligent clinical analysis...** This may take 10-30 seconds as GPT-4 analyzes your results.")
                ai_progress.progress(20)
                
                # Save results temporarily for summarizer
                temp_file = f"temp_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                ai_status.info("📊 **Analyzing therapeutic potential...** GPT-4 is reviewing your target data and literature.")
                ai_progress.progress(50)
                
                try:
                    ai_status.info("📝 **Summarizing findings...** Wrapping up!")
                    ai_progress.progress(80)
                    
                    # Generate summary
                    summary = asyncio.run(result_summarizer.summarize_results(temp_file, query))
                    
                    # Complete and clear progress
                    ai_progress.progress(100)
                    time.sleep(0.5)
                    ai_progress.empty()
                    ai_status.empty()
                    
                    st.markdown(summary)
                except Exception as e:
                    ai_progress.empty()
                    ai_status.empty()
                    st.warning(f"Summary generation failed: {e}")
                    st.markdown("**Basic Analysis:** Successfully retrieved and analyzed therapeutic targets from multiple databases.")
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                # Download results
                st.subheader("💾 Download Results")
                
                json_str = json.dumps(results, indent=2, default=str)
                st.download_button(
                    label="📜 Download Literature Summary (JSON)",
                    data=json_str,
                    file_name=f"omics_oracle_literature_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # Track successful query and increment counter for free users
                processing_time = time.time() - start_time
                
                # Increment query counter for free users
                if not user_provided_key:
                    st.session_state.query_count += 1
                
                st.session_state.tracker.track_query(
                    query=query,
                    query_type="multi_target" if len(targets) > 1 else "single_target",
                    targets_found=len(targets),
                    processing_time=processing_time,
                    success=True,
                    user_id=user_id,
                    session_id=st.session_state.session_id
                )
                
                # Show upgrade message for free users after 2nd query
                if not user_provided_key and st.session_state.query_count == 2:
                    st.info("🚨 **1 free query remaining!** Consider getting your own API key for unlimited access. See sidebar for instructions.")
            else:
                st.error("❌ No targets found in results.")
        else:
            # Handle error results
            error_msg = results.get("error", "No results found")
            st.error(f"❌ {error_msg}. Please try a different query.")
            
            # Track failed query (no results)
            processing_time = time.time() - start_time
            
            # Increment query counter for free users even on failure
            if not user_provided_key:
                st.session_state.query_count += 1
            
            st.session_state.tracker.track_query(
                query=query,
                query_type="unknown",
                targets_found=0,
                processing_time=processing_time,
                success=False,
                error_message=error_msg,
                user_id=user_id,
                session_id=st.session_state.session_id
            )
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        # Track failed query (exception) and increment counter
        processing_time = time.time() - start_time
        
        # Increment query counter for free users even on error
        if not user_provided_key:
            st.session_state.query_count += 1
        
        st.session_state.tracker.track_query(
            query=query,
            query_type="error",
            targets_found=0,
            processing_time=processing_time,
            success=False,
            error_message=str(e)[:200],
            user_id=user_id,
            session_id=st.session_state.session_id
        )
        st.markdown("""
        **Possible solutions:**
        - Try a different query
        - Check back later if service is down
        - Report persistent issues
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧬 <strong>Omics Oracle</strong> - Built with ❤️ for the drug discovery community</p>
    <p>⚡ Powered by OpenAI GPT-4 | 📀 Real-time data from PubMed, ChEMBL, RCSB PDB</p>
    <p>🔒 Your API keys are secure and never stored on our servers</p>
    <p>💻 <strong>Open Source:</strong> <a href="https://github.com/anugrahat/omics-oracle_website" target="_blank" style="color: #0066cc; text-decoration: none;">⭐ View Code on GitHub</a> | 👤 Developed by <strong>Anugraha T</strong></p>
</div>
""", unsafe_allow_html=True)
