# 🚀 **Deploy Omics Oracle - Freemium Web Demo**

## 🎯 **Business Model**: Freemium + Analytics

- **Free Users**: 3 queries using your API key
- **Unlimited Users**: Their own OpenAI API key
- **You Get**: Usage analytics, lead generation, cost control

---

## ⚡ **Quick Deploy (5 minutes)**

### **Step 1: Set Up Your API Key**
```bash
# In website/ folder, create .env file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### **Step 2: Deploy to Streamlit Cloud**
1. **Push to GitHub**: `git push origin main`
2. **Visit**: [share.streamlit.io](https://share.streamlit.io)
3. **New app** → Select your repo
4. **Main file**: `website/app.py` ⚠️ **CRITICAL**
5. **Advanced settings** → Environment variables:
   - `OPENAI_API_KEY` = `your-api-key-here`
6. **Deploy!** → Get URL like `https://omics-oracle.streamlit.app`

### **Step 3: Monitor Usage**
- **Admin Dashboard**: Run `streamlit run admin_dashboard.py`
- **View**: Query counts, popular searches, user analytics
- **Export**: CSV data for lead generation

---

## 📊 **What You Get from Users**

### **Free Users (3 queries max)**
- Contact info from interested recruiters
- Query patterns to understand market needs  
- Demo conversion rate to paid API keys
- Cost: ~$1.50 per user (3 queries × $0.50)

### **Unlimited Users (their API key)**
- Zero cost to you
- Shows serious interest in your skills
- Great for portfolio demonstrations
- Scales indefinitely

---

## 🎯 **Perfect for Recruiters**

### **User Journey:**
1. **Visit your URL** (no signup required)
2. **Try 3 free queries** (diabetes, cancer targets, etc.)
3. **See impressive AI-powered results**
4. **Get upgrade prompt** after 3 queries
5. **Either contact you or get own API key**

### **Value Proposition:**
- \"Try before you hire\" approach
- Shows real AI/LLM engineering skills
- Demonstrates production deployment ability
- Proves you can build user-facing AI tools

---

## 🔧 **Cost Management**

### **Monthly Estimates:**
- **100 free users** × 3 queries = $150/month
- **10 users upgrade** to own keys = $0 cost
- **Lead generation value** >> costs

### **Cost Controls:**
- Query limit enforced per session
- Your API key never exposed to users
- Usage analytics to monitor spending
- Easy to adjust limits in code

---

## 📈 **Analytics Dashboard Features**

- **Total queries** and **unique users**
- **Popular search patterns** (great for interviews!)
- **Success rates** and **error tracking**
- **Daily usage trends**
- **Export data** for lead follow-up

---

## 🛡️ **Security Features**

- User API keys stored only in browser session
- Your API key hidden in environment variables
- No personal data collection
- Privacy-safe analytics (hashed user IDs)
- HTTPS via Streamlit Cloud

---

## 💡 **Pro Tips**

1. **Share URL** on LinkedIn, resume, GitHub
2. **Add to portfolio** as live demo
3. **Mention in interviews**: "Here's a live AI tool I built"
4. **Track popular queries** to prep for interviews
5. **Export user data** for networking follow-up

---

## 🎉 **Result: Professional AI Demo**

**Your URL becomes a powerful interview tool:**
- Recruiters test your AI agent live
- Zero friction (no setup required)
- Scales to thousands of users
- Shows production deployment skills
- Generates leads and conversations

**Perfect for pharmaceutical, biotech, and AI/ML roles!** 🧬
