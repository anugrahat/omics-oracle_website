"""
📊 Omics Oracle - Admin Analytics Dashboard
View usage statistics and user behavior insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import UsageTracker
from datetime import datetime, timedelta
import sqlite3

# Page configuration
st.set_page_config(
    page_title="📊 Omics Oracle - Admin Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Admin authentication (simple password protection)
def check_admin_access():
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.title("🔐 Admin Access")
        password = st.text_input("Enter admin password:", type="password")
        if st.button("Login"):
            if password == "omics_admin_2024":  # Change this password!
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid password")
        st.stop()

check_admin_access()

# Initialize tracker
tracker = UsageTracker()

# Main dashboard
st.title("📊 Omics Oracle - Usage Analytics Dashboard")
st.markdown("**Real-time insights into user behavior and system performance**")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()

# Get statistics
stats = tracker.get_usage_stats()
trends = tracker.get_daily_trends(days=30)

# Overview metrics
st.header("📈 Overview Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Queries",
        stats['total_queries'],
        help="Total number of queries processed"
    )

with col2:
    st.metric(
        "Unique Users",
        stats['total_users'],
        help="Number of unique user sessions"
    )

with col3:
    st.metric(
        "Success Rate",
        f"{stats['success_rate_percent']:.1f}%",
        help="Percentage of successful queries"
    )

with col4:
    st.metric(
        "Recent Activity",
        f"{stats['recent_queries_7d']} queries",
        help="Queries in the last 7 days"
    )

# Daily trends chart
if trends['daily_data']:
    st.header("📊 Daily Usage Trends")
    
    df = pd.DataFrame(trends['daily_data'], columns=['Date', 'Queries', 'Users', 'Success Rate'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_queries = px.line(df, x='Date', y='Queries', 
                             title='Daily Query Volume',
                             markers=True)
        fig_queries.update_layout(showlegend=False)
        st.plotly_chart(fig_queries, use_container_width=True)
    
    with col2:
        fig_users = px.bar(df, x='Date', y='Users',
                          title='Daily Unique Users',
                          color='Users',
                          color_continuous_scale='viridis')
        st.plotly_chart(fig_users, use_container_width=True)

# Query type analysis
st.header("🎯 Query Analysis")

col1, col2 = st.columns(2)

with col1:
    if stats['popular_query_types']:
        st.subheader("📈 Popular Query Types")
        query_types_df = pd.DataFrame(stats['popular_query_types'], columns=['Type', 'Count'])
        
        fig_pie = px.pie(query_types_df, values='Count', names='Type',
                        title="Query Type Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    if stats['popular_queries']:
        st.subheader("🔥 Popular Query Patterns")
        popular_df = pd.DataFrame(stats['popular_queries'], columns=['Query Preview', 'Count'])
        
        # Display as a table with bars
        for _, row in popular_df.head(10).iterrows():
            query_text = row['Query Preview']
            count = row['Count']
            st.write(f"**{count}x** - {query_text}...")

# Detailed query log
st.header("📋 Recent Query Log")

# Get recent queries from database
conn = sqlite3.connect(tracker.db_path)
recent_queries = pd.read_sql_query("""
    SELECT 
        timestamp,
        SUBSTR(query_text, 1, 60) as query_preview,
        query_type,
        targets_found,
        processing_time_seconds,
        success,
        error_message
    FROM queries 
    ORDER BY timestamp DESC 
    LIMIT 50
""", conn)
conn.close()

if not recent_queries.empty:
    # Add status emoji
    recent_queries['Status'] = recent_queries['success'].apply(
        lambda x: '✅ Success' if x else '❌ Failed'
    )
    
    # Format processing time
    recent_queries['Processing Time'] = recent_queries['processing_time_seconds'].apply(
        lambda x: f"{x:.1f}s" if pd.notnull(x) else "N/A"
    )
    
    # Display table
    display_columns = ['timestamp', 'query_preview', 'query_type', 'targets_found', 
                      'Processing Time', 'Status', 'error_message']
    
    st.dataframe(
        recent_queries[display_columns].rename(columns={
            'timestamp': 'Time',
            'query_preview': 'Query Preview',
            'query_type': 'Type',
            'targets_found': 'Targets',
            'error_message': 'Error'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No queries recorded yet.")

# Performance metrics
st.header("⚡ Performance Metrics")

if not recent_queries.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_time = recent_queries['processing_time_seconds'].mean()
        st.metric("Average Processing Time", f"{avg_time:.1f}s")
    
    with col2:
        successful_queries = recent_queries[recent_queries['success'] == True]
        avg_targets = successful_queries['targets_found'].mean()
        st.metric("Average Targets Found", f"{avg_targets:.1f}")
    
    with col3:
        error_rate = (len(recent_queries[recent_queries['success'] == False]) / len(recent_queries)) * 100
        st.metric("Error Rate", f"{error_rate:.1f}%")

# Export data
st.header("💾 Data Export")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Export All Queries (CSV)"):
        conn = sqlite3.connect(tracker.db_path)
        all_queries = pd.read_sql_query("SELECT * FROM queries ORDER BY timestamp DESC", conn)
        conn.close()
        
        csv = all_queries.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"omics_oracle_queries_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 Export Daily Stats (CSV)"):
        conn = sqlite3.connect(tracker.db_path)
        daily_stats = pd.read_sql_query("SELECT * FROM daily_stats ORDER BY date DESC", conn)
        conn.close()
        
        csv = daily_stats.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"omics_oracle_daily_stats_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("**🔒 Admin Dashboard** - Confidential usage analytics for Omics Oracle")
st.markdown("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
