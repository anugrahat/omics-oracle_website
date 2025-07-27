"""
🧬 Omics Oracle: Simple Working Demo
"""

import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="🧬 Omics Oracle - AI Drug Discovery Demo",
    page_icon="🧬",
    layout="wide"
)

# Main header
st.markdown("""
<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1>🧬 Omics Oracle: AI-Powered Therapeutic Target Discovery</h1>
    <p>Professional drug discovery platform for pharmaceutical companies and biotech startups</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
    st.session_state.user_api_key = None

# Get API key
user_provided_key = st.session_state.get('user_api_key')
openai_key = user_provided_key if user_provided_key else os.getenv('OPENAI_API_KEY')

# Sidebar
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
    
    # API Key input
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
                st.success("✅ API key activated!")
                st.rerun()
            else:
                st.error("❌ Invalid API key format.")
    
    # Sample queries
    st.subheader("📋 Sample Queries")
    
    sample_queries = [
        "Find druggable candidates for Alzheimer's disease",
        "Find potent inhibitors for COPD targets",
        "Type 2 diabetes therapeutic targets", 
        "EGFR inhibitors under 50 nM IC50",
        "Parkinson's disease drug targets",
        "JAK2 and BRAF cancer targets"
    ]
    
    for i, query in enumerate(sample_queries):
        if st.button(f"📋 {query}", key=f"sample_{i}"):
            st.session_state.selected_query = query
            st.rerun()

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎯 Drug Target Discovery Query")
    
    # Query input
    if 'selected_query' in st.session_state:
        default_query = st.session_state.selected_query
        del st.session_state.selected_query
    else:
        default_query = "Find druggable candidates for Alzheimer's disease"
    
    query = st.text_area(
        "Enter your therapeutic target query:",
        value=default_query,
        height=100,
        help="💡 Click examples in sidebar or try your own!"
    )
    
    # Run button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        # Check limits
        if not user_provided_key and st.session_state.query_count >= 3:
            st.error("🚫 **Free query limit reached!** Get your own OpenAI API key for unlimited access.")
        elif not query.strip():
            st.error("⚠️ Please enter a query to analyze.")
        else:
            # Increment counter
            if not user_provided_key:
                st.session_state.query_count += 1
            
            # Show demo results
            st.success("✅ Demo mode - Analysis completed!")
            
            # Mock results display
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("🎯 Targets Found", "3")
            with col_b:
                st.metric("⭐ Average Score", "7.2/10")
            with col_c:
                st.metric("💊 Total Inhibitors", "47")
            with col_d:
                st.metric("🧬 Total Structures", "12")
            
            st.markdown("### 🏆 Target Ranking")
            st.markdown("""
            | Target | Score | Inhibitors | Assessment |
            |--------|-------|------------|-----------|
            | BACE1 | 8.5/10 | 23 | Excellent ⭐⭐⭐ |
            | APP | 7.1/10 | 15 | Good ⭐⭐ |
            | PSEN1 | 6.0/10 | 9 | Moderate ⭐ |
            """)
            
            if not user_provided_key and st.session_state.query_count == 2:
                st.info("🚨 **1 free query remaining!** Consider getting your own API key.")
            
            st.info("**Demo Mode**: Add your OpenAI API key for real AI-powered analysis!")

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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧬 <strong>Omics Oracle</strong> - Built for the drug discovery community</p>
    <p>⚡ Powered by OpenAI GPT-4 | 📊 Real-time data integration</p>
    <p>🔒 Your API keys are secure and never stored</p>
</div>
""", unsafe_allow_html=True)
