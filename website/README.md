# 🌐 Omics Oracle - Web Interface

**Beautiful Streamlit demo for recruiters and hiring managers**

## 🚀 **LIVE DEPLOYMENT** - 3 Easy Steps

### **Option 1: Streamlit Cloud (FREE)**
1. **Visit**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub and select this repo
3. **Set main file**: `website/app.py`
4. **Deploy!** → Get URL like `https://omics-oracle.streamlit.app`

### **Option 2: Hugging Face Spaces (FREE)**
1. **Visit**: [huggingface.co/spaces](https://huggingface.co/spaces)
2. **Create Space** with Streamlit template
3. **Upload** this `website/` folder
4. **Auto-deploy** → Get URL like `https://huggingface.co/spaces/username/omics-oracle`

### **🌟 Result: Public Website!**
- Recruiters visit your URL
- No installation needed
- Works on any device
- Enter OpenAI key and test!

## 🔧 Local Development

```bash
# From main omics-oracle directory
pip install -r requirements.txt -r website/requirements.txt

# Launch web app
cd website
streamlit run app.py
```

## 🎯 For Hiring Managers

### What You Need:
- ✅ **OpenAI API Key** ([get here](https://platform.openai.com/api-keys))
- ✅ **$5-10 in credits** (enough for extensive testing)

### How to Test:
1. **Visit the demo URL** 
2. **Enter your API key** in sidebar (secure - browser only)
3. **Try example queries**:
   - `"type 2 diabetes therapeutic targets"`
   - `"Find EGFR inhibitors under 50 nM"`
   - `"ovarian cancer drug targets"`

### What You'll See:
- 🧠 **AI-powered analysis** with GPT-4
- 📊 **Real-time data** from 3 scientific databases
- 🎯 **Target rankings** with druggability scores
- 💊 **Inhibitor discovery** with IC50 values
- 🧬 **Structural data** from Protein Data Bank
- 📋 **Clinical insights** and recommendations

## 🏆 Technical Features

- **RAG Architecture**: Retrieval-Augmented Generation
- **Multi-Database Integration**: PubMed + ChEMBL + RCSB PDB
- **Async Performance**: Concurrent API calls
- **Intelligent Caching**: SQLite with TTL
- **Fallback Systems**: Works without OpenAI key
- **Production Ready**: Error handling, rate limiting

## 🔒 Security

- API keys stored only in browser session
- No server-side key storage
- HTTPS encryption via Streamlit Cloud
- No personal data collection

---

**Perfect for showcasing AI/ML engineering skills to pharmaceutical companies and biotech startups!** 🧬
