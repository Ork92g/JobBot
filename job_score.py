import re

# ==========================================
# TARGET PROFILE
# ==========================================

TARGET_ROLES = [
    "soc",
    "soc analyst",
    "soc tier 1",
    "soc tier 2",
    "soc analyst tier 1",
    "soc analyst tier 2",
    "security analyst",
    "cybersecurity analyst",
    "cyber security analyst",
    "security operations",
    "security operations analyst",
    "security operations specialist",
    "security operations center",
    "secops",
    "mdr",
    "mdr analyst",
    "managed detection",
    "incident response",
    "incident responder",
    "incident analyst",
    "dfir",
    "digital forensics",
    "threat analyst",
    "threat intelligence",
    "threat detection",
    "threat hunter",
    "threat hunting",
    "detection analyst",
    "detection engineer",
    "security monitoring",
    "security monitoring analyst",
    "cyber defense",
    "cyber defense analyst",
    "cybersecurity defense",
    "security investigator",
    "information security analyst",
    "it security analyst",
    "cybersecurity specialist",
    "cyber security specialist",
    "security engineer",
    "blue team",
    "cyber defense analyst",
]

# ==========================================
# HIGH VALUE SKILLS
# ==========================================

GOOD_SKILLS = [
    "microsoft sentinel",
    "sentinel",
    "splunk",
    "qradar",
    "siem",
    "edr",
    "xdr",
    "crowdstrike",
    "defender",
    "defender for endpoint",
    "mde",
    "microsoft defender",
    "incident response",
    "threat hunting",
    "threat intelligence",
    "threat detection",
    "detection engineering",
    "windows",
    "linux",
    "powershell",
    "kql",
    "sysmon",
    "mitre",
    "mitre attack",
    "network security",
    "networking",
    "tcp/ip",
    "dns",
    "firewall",
    "vpn",
    "security monitoring",
    "log analysis",
    "alert triage",
    "incident investigation",
    "malware analysis",
    "forensics",
]

# ==========================================
# POSITIVE SENIORITY
# ==========================================

POSITIVE_WORDS = [
    "junior",
    "entry level",
    "entry-level",
    "associate",
    "tier 1",
    "tier-1",
    "tier 2",
    "tier-2",
    "l1",
    "l2",
    "0-1",
    "0–1",
    "1-2",
    "1–2",
    "1+ years",
    "2+ years",
    "1 year",
    "2 years",
    "0 years",
    "no experience",
    "without experience",
    "graduates",
    "graduate",
    "early career",
]

# ==========================================
# NEGATIVE SENIORITY
# ==========================================

NEGATIVE_WORDS = [
    "senior",
    "sr.",
    "sr ",
    "lead",
    "manager",
    "director",
    "head",
    "principal",
    "architect",
    "vp",
    "vice president",
    "chief",
    "staff security",
]

# ==========================================
# HARD NEGATIVE ROLES
# ==========================================

HARD_NEGATIVE_ROLES = [
    "sales",
    "account executive",
    "business development",
    "bdr",
    "marketing",
    "recruiter",
    "recruiting",
    "customer success",
    "customer support",
    "product manager",
    "project manager",
    "software engineer",
    "frontend",
    "backend",
    "full stack",
    "mobile engineer",
    "data scientist",
    "machine learning",
    "ai engineer",
    "devops engineer",
    "cloud engineer",
    "qa engineer",
    "automation engineer",
    "financial",
    "finance",
    "legal",
    "designer",
    "hr",
    "human resources",
]

# ==========================================
# LOCATION
# ==========================================

ISRAEL_LOCATIONS = [
    "israel",
    "tel aviv",
    "tel-aviv",
    "tel-aviv-yafo",
    "ramat gan",
    "petah tikva",
    "petah-tikva",
    "herzliya",
    "rishon",
    "rishon lezion",
    "haifa",
    "jerusalem",
    "yoqneam",
    "yokneam",
    "center district",
    "gush dan",
    "israel remote",
    "remote israel",
]

# ==========================================
# CALCULATE SCORE
# ==========================================

def calculate_score(job):

    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    location = job.get("location", "").lower()

    text = f"{title} {description}"

    score = 0
    skills_found = []

    # ======================================
    # HARD NEGATIVE ROLE
    # ======================================

    for word in HARD_NEGATIVE_ROLES:
        if word in title:
            score -= 70
            break

    # ======================================
    # TARGET ROLE IN TITLE
    # ======================================

    role_match = False

    for role in TARGET_ROLES:
        if role in title:
            role_match = True
            score += 40
            break

    # ======================================
    # SECURITY CONTEXT
    # ======================================

    security_context = [
        "security",
        "cybersecurity",
        "cyber security",
        "soc",
        "secops",
        "incident",
        "threat",
        "defense",
        "defence",
        "detection",
        "forensics",
        "siem",
        "edr",
        "mdr",
    ]

    context_matches = 0

    for word in security_context:
        if word in text:
            context_matches += 1

    if context_matches >= 3:
        score += 15
    elif context_matches >= 1:
        score += 5

    # ======================================
    # ISRAEL
    # ======================================

    is_israel = False

    for place in ISRAEL_LOCATIONS:
        if place in location or place in text:
            is_israel = True
            score += 15
            break

    # ======================================
    # REMOTE
    # ======================================

    if "remote" in text:
        score += 5

    # ======================================
    # SECURITY SKILLS
    # ======================================

    for skill in GOOD_SKILLS:

        if skill in text:

            if skill not in skills_found:
                skills_found.append(skill)

            score += 3

    # ======================================
    # HIGH VALUE SKILLS BONUS
    # ======================================

    high_value = [
        "microsoft sentinel",
        "splunk",
        "crowdstrike",
        "microsoft defender",
        "incident response",
        "threat hunting",
        "kql",
        "mitre attack",
        "detection engineering",
        "alert triage",
    ]

    high_value_matches = 0

    for skill in high_value:
        if skill in text:
            high_value_matches += 1

    score += min(high_value_matches * 4, 20)

    # ======================================
    # JUNIOR / ENTRY
    # ======================================

    for word in POSITIVE_WORDS:

        if word in text:
            score += 12
            break

    # ======================================
    # SENIORITY PENALTY
    # ======================================

    for word in NEGATIVE_WORDS:

        if word in title:
            score -= 40
            break

    # ======================================
    # EXPERIENCE REQUIREMENT
    # ======================================

    experience_numbers = re.findall(
        r"(\d+)\s*\+?\s*(?:years?|yrs?)",
        description
    )

    if experience_numbers:

        try:

            max_years = max(
                int(x)
                for x in experience_numbers
            )

            if max_years >= 7:
                score -= 30

            elif max_years >= 5:
                score -= 20

            elif max_years >= 3:
                score -= 10

        except ValueError:
            pass

    # ======================================
    # STRONG JUNIOR BONUS
    # ======================================

    junior_signals = [
        "junior",
        "entry level",
        "entry-level",
        "tier 1",
        "tier-1",
        "l1",
        "0-1 years",
        "0–1 years",
        "1-2 years",
        "1–2 years",
        "no experience",
        "without experience",
        "graduates",
        "early career",
    ]

    junior_matches = 0

    for word in junior_signals:
        if word in text:
            junior_matches += 1

    if junior_matches >= 1:
        score += 8

    # ======================================
    # STRONG SENIOR EXPERIENCE PENALTY
    # ======================================

    if re.search(r"\b(?:6|7|8|9|10|\d{2,})\+?\s*(?:years?|yrs?)", description):
        score -= 15

    # ======================================
    # NON-ISRAEL PENALTY
    # ======================================

    if not is_israel:
        score -= 20

    # ======================================
    # FINAL SCORE
    # ======================================

    score = max(
        0,
        min(
            100,
            score
        )
    )

    return score, skills_found
