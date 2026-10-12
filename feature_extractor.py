"""
Simplified Feature Extractor for Phishing URL Detection
Course: AI Systems and Applications (AISA) - Mini Project

This module extracts 15 pure lexical and structural features directly from any URL.
Key Advantages:
1. Ultra-fast (<1 millisecond per URL).
2. Zero external network dependencies (no slow scraping, no server timeout issues).
3. Highly interpretable for academic viva and project demonstrations.
"""

import re
from urllib.parse import urlparse

# Common keywords frequently exploited in phishing URLs for social engineering
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'update', 'secure', 'account', 'banking',
    'signin', 'confirm', 'password', 'webscr', 'wallet', 'security',
    'support', 'service', 'validation', 'authenticate', 'recover'
]

# Regular expression to test if domain is a raw IPv4 address
IPV4_REGEX = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

FEATURE_NAMES = [
    "url_length",
    "domain_length",
    "is_ip_address",
    "count_dots",
    "count_hyphens",
    "count_at",
    "count_question",
    "count_equals",
    "count_slash",
    "count_digits",
    "count_letters",
    "digit_ratio",
    "is_https",
    "has_suspicious_keyword",
    "subdomain_count"
]


def extract_url_features(url_str: str):
    """
    Extracts 15 lightweight, high-signal lexical features from a URL.
    Returns:
        features_dict: dict mapping feature name to numeric value
        metadata: human-readable metadata for user interfaces
    """
    url_str = str(url_str).strip()
    
    # Normalize URL scheme if missing for proper parsing
    normalized_url = url_str
    if not (url_str.startswith("http://") or url_str.startswith("https://")):
        normalized_url = "http://" + url_str

    parsed = urlparse(normalized_url)
    domain = parsed.netloc.split(':')[0].strip()

    # If domain couldn't be parsed properly, fallback to first token
    if not domain and '/' in url_str:
        domain = url_str.split('/')[0]

    # 1. Length metrics
    url_length = len(url_str)
    domain_length = len(domain)

    # 2. Host type check (IP vs domain)
    is_ip = 1 if IPV4_REGEX.match(domain) else 0

    # 3. Special character counts
    cnt_dots = url_str.count('.')
    cnt_hyphen = url_str.count('-')
    cnt_at = url_str.count('@')
    cnt_quest = url_str.count('?')
    cnt_eq = url_str.count('=')
    cnt_slash = url_str.count('/')

    # 4. Character distribution
    cnt_digits = sum(c.isdigit() for c in url_str)
    cnt_letters = sum(c.isalpha() for c in url_str)
    digit_ratio = round(cnt_digits / max(url_length, 1), 4)

    # 5. Protocol security
    is_https = 1 if url_str.lower().startswith('https://') else 0

    # 6. Keyword heuristics
    url_lower = url_str.lower()
    matched_keywords = [w for w in SUSPICIOUS_KEYWORDS if w in url_lower]
    has_suspicious_keyword = 1 if len(matched_keywords) > 0 else 0

    # 7. Subdomains count
    if is_ip:
        subdomain_count = 0
    else:
        # Standard domains have at least one dot (domain.tld)
        subdomain_count = max(0, domain.count('.') - 1)

    features = {
        "url_length": url_length,
        "domain_length": domain_length,
        "is_ip_address": is_ip,
        "count_dots": cnt_dots,
        "count_hyphens": cnt_hyphen,
        "count_at": cnt_at,
        "count_question": cnt_quest,
        "count_equals": cnt_eq,
        "count_slash": cnt_slash,
        "count_digits": cnt_digits,
        "count_letters": cnt_letters,
        "digit_ratio": digit_ratio,
        "is_https": is_https,
        "has_suspicious_keyword": has_suspicious_keyword,
        "subdomain_count": subdomain_count
    }

    metadata = {
        "url": url_str,
        "normalized_url": normalized_url,
        "scheme": parsed.scheme if parsed.scheme else ("https" if is_https else "http"),
        "domain": domain,
        "path": parsed.path if parsed.path else "/",
        "query": parsed.query if parsed.query else "",
        "fragment": parsed.fragment if parsed.fragment else "",
        "is_https": bool(is_https),
        "is_ip": bool(is_ip),
        "matched_keywords": matched_keywords,
        "subdomains": subdomain_count,
        "special_chars_count": cnt_dots + cnt_hyphen + cnt_at + cnt_quest + cnt_eq + cnt_slash,
    }

    return features, metadata


def analyze_url_risk_reasons(features: dict, metadata: dict, is_legit: bool = False):
    """
    Analyzes extracted features and metadata to explain WHY a URL is
    considered fraudulent / phishing, or why it appears safe.
    
    Returns:
        fraud_reasons: list of dicts describing each specific security risk detected
        safety_factors: list of dicts describing legitimate security signals
        risk_summary: str high-level risk assessment verdict
    """
    fraud_reasons = []
    safety_factors = []

    # 1. Raw IP Address
    if features.get("is_ip_address", 0) == 1:
        fraud_reasons.append({
            "factor": "Raw IP Address Used as Hostname",
            "severity": "Critical",
            "icon": "🚨",
            "evidence": f"Host is a raw IPv4 address `{metadata.get('domain', '')}` instead of a registered domain.",
            "explanation": "Legitimate banks and organizations use certified domain names. Attackers use raw IP addresses to bypass domain reputation blocklists and evade domain registration verification."
        })
    else:
        safety_factors.append({
            "factor": "Registered Domain Name",
            "icon": "🛡️",
            "evidence": f"Uses standard registered domain `{metadata.get('domain', '')}` instead of a raw IP address."
        })

    # 2. Insecure Protocol (HTTP vs HTTPS)
    if features.get("is_https", 1) == 0:
        fraud_reasons.append({
            "factor": "Unencrypted HTTP Protocol (No SSL/TLS)",
            "severity": "High",
            "icon": "🔓",
            "evidence": "Website uses insecure `http://` with zero encryption.",
            "explanation": "Authentic modern websites, payment gateways, and login portals enforce HTTPS. Phishing kits frequently host fake sites on unencrypted HTTP servers to avoid SSL identity verification."
        })
    else:
        safety_factors.append({
            "factor": "HTTPS Encryption Active",
            "icon": "🔒",
            "evidence": "URL uses `https://` protocol with cryptographic SSL/TLS transmission security."
        })

    # 3. Credential Bait / Social Engineering Keywords
    keywords = metadata.get("matched_keywords", [])
    if keywords:
        fraud_reasons.append({
            "factor": "Social Engineering / Credential Bait Keywords",
            "severity": "High",
            "icon": "🎣",
            "evidence": f"Detected sensitive lure keyword(s): `{', '.join(keywords)}`",
            "explanation": "Phishers embed words like 'login', 'verify', 'update', or 'account' in deceptive URLs to create urgency and trick victims into submitting passwords or banking OTPs."
        })
    else:
        safety_factors.append({
            "factor": "No Credential-Harvesting Keywords",
            "icon": "✅",
            "evidence": "No sensitive lure words (e.g., login, verify, banking, account) found in the URL."
        })

    # 4. Authority Hijacking via '@' Symbol
    cnt_at = features.get("count_at", 0)
    if cnt_at > 0:
        fraud_reasons.append({
            "factor": "URL Redirection Cloaking ('@' Symbol)",
            "severity": "Critical",
            "icon": "🚨",
            "evidence": f"Contains `{cnt_at}` '@' symbol(s) in URL structure.",
            "explanation": "In standard URL specifications (RFC 3986), web browsers treat everything before '@' as user credentials and ignore it, invisibly routing victims to the malicious domain placed after the '@'."
        })

    # 5. Subdomain Stacking
    subdomains = features.get("subdomain_count", 0)
    if subdomains >= 2:
        sev = "High" if subdomains >= 3 else "Medium"
        fraud_reasons.append({
            "factor": "Excessive Subdomain Stacking",
            "severity": sev,
            "icon": "🌐",
            "evidence": f"Detected `{subdomains}` levels of subdomains.",
            "explanation": "Attackers chain multiple subdomains (e.g., `paypal.com.verify-user.badsite.xyz`) so that victims reading only the first part of the address mistake it for the authentic brand."
        })
    elif subdomains <= 1 and not features.get("is_ip_address", 0):
        safety_factors.append({
            "factor": "Clean Domain Structure",
            "icon": "✅",
            "evidence": f"Standard domain hierarchy with {subdomains} subdomain level(s)."
        })

    # 6. Hyphen Count (Brand Spoofing)
    cnt_hyphen = features.get("count_hyphens", 0)
    if cnt_hyphen >= 2:
        sev = "High" if cnt_hyphen >= 3 else "Medium"
        fraud_reasons.append({
            "factor": "Brand Impersonation via Hyphenation",
            "severity": sev,
            "icon": "➖",
            "evidence": f"Found `{cnt_hyphen}` hyphens in URL string.",
            "explanation": "Attackers construct hyphenated domains (such as `secure-login-chase-update.com`) to closely imitate legitimate brand names without owning the actual trademarked domain."
        })

    # 7. Abnormal URL Length
    url_len = features.get("url_length", 0)
    if url_len > 75:
        fraud_reasons.append({
            "factor": "Suspiciously Long URL Length",
            "severity": "Medium",
            "icon": "📏",
            "evidence": f"URL length is `{url_len}` characters (standard legitimate links average under 50).",
            "explanation": "Excessively long URLs are commonly used by phishing kits to conceal malicious domain endpoints on mobile browsers and pack obfuscated redirect tokens."
        })
    elif url_len < 55:
        safety_factors.append({
            "factor": "Compact URL Length",
            "icon": "✅",
            "evidence": f"URL length is compact ({url_len} characters), typical of standard genuine websites."
        })

    # 8. Excessive Domain Length
    dom_len = features.get("domain_length", 0)
    if dom_len > 28:
        fraud_reasons.append({
            "factor": "Unusually Long Domain Name",
            "severity": "Medium",
            "icon": "🏷️",
            "evidence": f"Domain name length is `{dom_len}` characters.",
            "explanation": "Legitimate enterprises register concise, memorable domain names. Long domain names often indicate disposable or algorithmically generated phishing domains."
        })

    # 9. Excessive Dots in URL
    cnt_dots = features.get("count_dots", 0)
    if cnt_dots >= 3 and not features.get("is_ip_address", 0):
        fraud_reasons.append({
            "factor": "High Dot Density",
            "severity": "Medium",
            "icon": "💬",
            "evidence": f"Contains `{cnt_dots}` dots across the URL.",
            "explanation": "Excessive dots indicate multi-layered subdomains, deceptive file extensions (e.g. `.account.html.php`), or chained redirection proxies."
        })

    # 10. High Numeric / Digit Density
    d_ratio = features.get("digit_ratio", 0)
    d_count = features.get("count_digits", 0)
    if d_ratio > 0.15 and d_count >= 5:
        fraud_reasons.append({
            "factor": "High Digit / Obfuscation Density",
            "severity": "Medium",
            "icon": "🔢",
            "evidence": f"`{d_ratio * 100:.1f}%` of URL characters are numbers ({d_count} digits).",
            "explanation": "High numeric density is a signature of automated campaign tokens, randomized hash strings, or port/IP camouflage rather than human-readable brand links."
        })

    # 11. Deep Path Nesting
    cnt_slash = features.get("count_slash", 0)
    if cnt_slash >= 4:
        fraud_reasons.append({
            "factor": "Deep Directory Path Nesting",
            "severity": "Low",
            "icon": "📁",
            "evidence": f"Contains `{cnt_slash}` path slashes.",
            "explanation": "Phishing kits are frequently hosted deep inside compromised servers' subdirectories (e.g. `/wp-content/plugins/.../login/`) to avoid immediate detection by webmasters."
        })

    # Classification specific summary and fallback
    if is_legit:
        risk_summary = "SAFE: Legitimate Website Profile"
    else:
        if not fraud_reasons:
            fraud_reasons.append({
                "factor": "Complex Multi-Feature Pattern Match",
                "severity": "Medium",
                "icon": "🤖",
                "evidence": "Cumulative structural metrics align with phishing profiles.",
                "explanation": "The Random Forest model identified a non-linear combination of lexical signals (character ratios, path depth, and lexical structure) typical of phishing URLs."
            })

        severities = [r["severity"] for r in fraud_reasons]
        if "Critical" in severities:
            risk_summary = "CRITICAL RISK: Highly Dangerous Malicious URL"
        elif "High" in severities:
            risk_summary = "HIGH RISK: Multiple Severe Phishing Indicators"
        elif "Medium" in severities:
            risk_summary = "MODERATE RISK: Suspicious URL Characteristics"
        else:
            risk_summary = "LOW RISK: Minor Structural Irregularities"

    return fraud_reasons, safety_factors, risk_summary


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Test sample URLs
    test_urls = [
        ("https://www.google.com", True),
        ("http://paypal-security-update.account-verification.xyz/login.php?user=alert", False),
        ("http://192.168.1.105/online-banking/signin.htm", False)
    ]
    print("Testing Simplified Feature Extractor with Risk Reasons:")
    for u, is_safe in test_urls:
        feats, meta = extract_url_features(u)
        reasons, safe_f, summary = analyze_url_risk_reasons(feats, meta, is_legit=is_safe)
        print(f"\nURL: {u}")
        print(f"Summary: {summary}")
        if not is_safe:
            print(f"Fraud Reasons ({len(reasons)}):")
            for r in reasons:
                print(f"  [{r['severity']}] {r['factor']}: {r['evidence']}")
        else:
            print(f"Safety Factors ({len(safe_f)}):")
            for s in safe_f:
                print(f"  [{s['factor']}]: {s['evidence']}")


