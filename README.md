# PhishShield: Web Threat Intelligence & Phishing URL Detector
**Course:** AI Systems and Applications (AISA) – Mini Project  
**Department:** Department of Computer Engineering and Technology  
**Academic Year:** 2026-27 | **Semester:** 5  

---

## 📌 Project Overview
**PhishShield** is an enterprise-grade cybersecurity web intelligence platform designed to detect, classify, and explain fraudulent and phishing URLs in real time.

Powered by a **Random Forest Classifier (100 Trees)** trained on a balanced benchmark of **40,000 URLs** from the **PhiUSIIL Phishing URL Dataset** (UCI Machine Learning Repository), PhishShield combines machine learning precision with an **Explainable AI (XAI)** threat engine that breaks down the exact technical reasons why a URL is flagged as fraudulent.

---

## 🚀 Key Architectural Features

1. **Full-Width Cybersecurity UI (Zero Left Sidebar):**
   - Clean, professional dark theme (midnight / obsidian palette).
   - Slim horizontal top navigation bar featuring:
     - Brand identity: `PhishShield` | `WEB THREAT INTELLIGENCE`
     - Status badge: `● ENGINE ONLINE | Random Forest 99.56%`
     - Quick navigation: `🔍 URL Scanner`, `⚡ Threat Overview`, `🔬 URL Intelligence`, `📜 Scan History`, `📊 Model Insights`.

2. **Explainable AI (XAI) Threat Breakdown:**
   - Evaluates 11 specific cybersecurity threat vectors with severity levels (`[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`):
     - **Raw IP Address Hostname:** Evading domain KYC and reputation blacklists.
     - **Unencrypted HTTP Protocol:** Transmitting credentials in plaintext without SSL/TLS.
     - **Social Engineering Keywords:** Bait keywords like `login`, `verify`, `update`, `banking`, `account`.
     - **Subdomain Stacking:** Chaining multiple subdomains to disguise the real host.
     - **Redirection Cloaking (`@` Symbol):** Browser authority masking per RFC 3986.
     - **Brand Impersonation via Hyphenation:** Typosquatting domains (e.g. `paypal-security-update.xyz`).
     - **Abnormal URL & Domain Length:** Pushing deceptive URLs off-screen on mobile devices.
     - **Numeric / Digit Obfuscation:** Automated campaign IDs and hash tokens.
     - **Deep Directory Nesting:** Backdoor phishing kits uploaded in compromised server folders.
   - For legitimate sites, displays confirmed positive security trust signals.

3. **Multi-Mode Scanning:**
   - **Single URL Deep Inspection:** Real-time analysis with instant verdict, confidence percentages, threat cards, and actionable recommendations.
   - **Batch URL Scanner:** Multi-line bulk scanning with threat summary, downloadable CSV report, and drill-down inspection.

4. **URL Intelligence Workspace:**
   - Deep structural inspection of URL components (Scheme, Host, Path, Query string, Fragment).
   - Complete Security Feature Scorecard comparing extracted values to safe baselines (`✅ Pass (Safe)` vs `🚨 Flagged (Risk)`).

5. **Real-Time Session Analytics & Scan History:**
   - Tracks total scans, phishing detections, legitimate sites, and threat rate.
   - Searchable, filterable session scan log with one-click re-inspection.

6. **Model Insights & Verified Metrics:**
   - Random Forest (100 Trees) benchmarked against Decision Tree.
   - **Accuracy:** `99.56%` | **Precision:** `99.25%` | **Recall:** `99.88%` | **F1-Score:** `99.56%` | **ROC-AUC:** `0.9979`.
   - Confusion Matrix (8,000 test set): `3,970 TN`, `30 FP`, `5 FN`, `3,995 TP`.
   - Feature Importance ranking chart.

---

## 🔬 The 15 Lexical Features

1. `url_length`: Overall character count of the URL.
2. `domain_length`: Character length of the host domain.
3. `is_ip_address`: Binary flag indicating whether the host is a raw IPv4 address.
4. `count_dots`: Count of period characters (`.`) used in subdomains or extensions.
5. `count_hyphens`: Count of hyphens (`-`) used to mimic brand names.
6. `count_at`: Count of `@` symbols (RFC 3986 redirection cloaking).
7. `count_question`: Presence and count of query string delimiters (`?`).
8. `count_equals`: Parameter key-value delimiters (`=`).
9. `count_slash`: Directory depth count (`/`).
10. `count_digits`: Numeric character count across the URL.
11. `count_letters`: Alphabetic letter count.
12. `digit_ratio`: Ratio of digits to total characters.
13. `is_https`: Cryptographic protocol security flag (HTTPS vs HTTP).
14. `has_suspicious_keyword`: Flag for lure keywords (`login`, `verify`, `update`, `banking`, `secure`, `account`, etc.).
15. `subdomain_count`: Number of sub-domain levels beyond the registered root domain.

---

## 📁 Project Structure

```
p2/
├── app.py                                       # Main Streamlit web application & controller
├── ui.py                                        # Modern SaaS dark UI theme & component rendering
├── feature_extractor.py                         # 15-feature extraction & Explainable AI logic
├── train_model.py                               # Training pipeline (Random Forest vs Decision Tree)
├── run_all.py                                   # Master terminal menu launcher
├── phishing_model.joblib                        # Serialized Random Forest Classifier
├── model_metrics.json                           # Verified evaluation metrics & confusion matrix
├── confusion_matrix.png                         # High-res confusion matrix heatmap
├── feature_importance.png                       # Top feature importance bar chart
├── model_comparison.png                         # Random Forest vs Decision Tree benchmark
├── generate_report_pdf.py                       # Academic PDF report generator (ReportLab)
├── generate_presentation_pptx.py                # 12-Slide widescreen presentation generator (python-pptx)
├── generate_friends_guide_pdf.py                # Student's friendly project explanation guide PDF
├── Phishing_URL_Detection_Project_Report.pdf    # Compiled academic PDF report
├── Phishing_URL_Detection_Presentation.pptx     # Compiled 12-slide PowerPoint presentation
├── PhishShield_Project_Explained_Simple_Guide.pdf # Compiled friendly explanation guide
├── requirements.txt                             # Python dependencies
└── README.md                                    # Comprehensive documentation
```

---

## 💻 Quick Start & Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Web Application (Recommended)
```bash
streamlit run app.py
```
Or use the launcher:
```bash
python run_all.py
```

### 3. Generate Project Deliverables

#### Generate 12-Slide PowerPoint Presentation:
```bash
python generate_presentation_pptx.py
```
*Outputs: `Phishing_URL_Detection_Presentation.pptx`*

#### Generate Academic Project Report (PDF):
```bash
python generate_report_pdf.py
```
*Outputs: `Phishing_URL_Detection_Project_Report.pdf`*

#### Generate Friends & Viva Explanation Guide (PDF):
```bash
python generate_friends_guide_pdf.py
```
*Outputs: `PhishShield_Project_Explained_Simple_Guide.pdf`*

#### Retrain Model (Optional):
```bash
python train_model.py
```

---

## 📊 Evaluation Summary

| Metric | Random Forest (100 Trees) | Decision Tree (Baseline) |
| :--- | :---: | :---: |
| **Accuracy** | **99.56%** | 99.54% |
| **Precision** | **99.25%** | 99.23% |
| **Recall** | **99.88%** | 99.85% |
| **F1-Score** | **99.56%** | 99.54% |
| **ROC-AUC** | **0.9979** | 0.9959 |
| **Inference Latency** | **< 0.8 ms** | < 0.5 ms |
