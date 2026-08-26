import re


# ============================================================
# TARGET PROFILE
# ============================================================

TARGET_ROLES = [

    "soc",
    "soc analyst",
    "soc tier 1",
    "soc tier 2",
    "soc l1",
    "soc l2",

    "security analyst",
    "cybersecurity analyst",
    "cyber security analyst",

    "security operations",
    "security operations analyst",
    "security operations specialist",

    "secops",
    "secops analyst",

    "mdr",
    "mdr analyst",
    "managed detection",

    "incident response",
    "incident responder",
    "incident analyst",

    "dfir",
    "digital forensics",
    "digital forensics incident response",

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

    "security investigator",

    "information security analyst",
    "it security analyst",

    "cybersecurity specialist",
    "cyber security specialist",
]


# ============================================================
# HIGH VALUE SKILLS
# ============================================================

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


# ============================================================
# POSITIVE SENIORITY / EXPERIENCE
# ============================================================

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

    "0-1 years",
    "0–1 years",

    "1-2 years",
    "1–2 years",

    "1+ years",
    "2+ years",

    "1 year",
    "2 years",

    "no experience required",
    "entry level position",
    "early career",
]


# ============================================================
# NEGATIVE SENIORITY
# ============================================================

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
]


# ============================================================
# HARD NEGATIVE ROLES
# ============================================================

HARD_NEGATIVE_ROLES = [

    "sales",
    "account executive",
    "business development",
    "bdr",
    "sdr",

    "marketing",

    "recruiter",
    "recruiting",
    "talent acquisition",

    "customer success",
    "customer support",

    "product manager",
    "project manager",

    "software engineer",
    "frontend",
    "front end",
    "backend",
    "back end",
    "full stack",
    "mobile engineer",

    "data scientist",
    "data science",

    "machine learning",
    "ml engineer",
    "ai engineer",

    "devops engineer",
    "cloud engineer",
    "qa engineer",
    "automation engineer",

    "financial",
    "finance",
    "legal",
    "designer",
    "human resources",
]


# ============================================================
# ISRAEL LOCATIONS
# ============================================================

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
]


# ============================================================
# SECURITY CONTEXT
# ============================================================

SECURITY_CONTEXT = [

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


# ============================================================
# HIGH VALUE SKILLS
# ============================================================

HIGH_VALUE_SKILLS = [

    "microsoft sentinel",
    "splunk",
    "qradar",

    "crowdstrike",

    "microsoft defender",

    "incident response",

    "threat hunting",
    "threat intelligence",
    "threat detection",

    "kql",

    "mitre attack",

    "detection engineering",

    "alert triage",
    "incident investigation",
]


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_year_requirements(description):

    patterns = [

        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",

        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:in|of)",

        r"experience\s*[:\-]?\s*(\d+)\s*\+?\s*(?:years?|yrs?)",

        r"minimum\s+of\s+(\d+)\s*\+?\s*(?:years?|yrs?)",

        r"at\s+least\s+(\d+)\s*\+?\s*(?:years?|yrs?)",
    ]

    numbers = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            description,
            flags=re.IGNORECASE
        )

        for value in matches:

            try:
                numbers.append(
                    int(value)
                )

            except ValueError:
                pass

    return numbers


# ============================================================
# SCORE
# ============================================================

def calculate_score(job):

    title = job.get(
        "title",
        ""
    ).lower().strip()

    description = job.get(
        "description",
        ""
    ).lower()

    location = job.get(
        "location",
        ""
    ).lower()

    text = f"{title} {description}"

    score = 0

    skills_found = []


    # ========================================================
    # 1. HARD NEGATIVE ROLE
    # ========================================================

    for word in HARD_NEGATIVE_ROLES:

        if word in title:

            score -= 80
            break


    # ========================================================
    # 2. TARGET ROLE
    # ========================================================

    target_role_found = False

    for role in TARGET_ROLES:

        if role in title:

            target_role_found = True
            score += 45
            break


    # ========================================================
    # 3. SECURITY CONTEXT
    # ========================================================

    context_matches = 0

    for word in SECURITY_CONTEXT:

        if word in text:
            context_matches += 1

    if context_matches >= 5:

        score += 15

    elif context_matches >= 3:

        score += 10

    elif context_matches >= 1:

        score += 5


    # ========================================================
    # 4. ISRAEL LOCATION
    # ========================================================

    if any(
        place in location
        for place in ISRAEL_LOCATIONS
    ):

        score += 10


    # ========================================================
    # 5. REMOTE
    # ========================================================

    if "remote" in text:

        score += 5


    # ========================================================
    # 6. SKILLS
    # ========================================================

    for skill in GOOD_SKILLS:

        if skill in text:

            if skill not in skills_found:

                skills_found.append(
                    skill
                )

            score += 2


    # ========================================================
    # 7. HIGH VALUE SKILLS
    # ========================================================

    high_value_matches = 0

    for skill in HIGH_VALUE_SKILLS:

        if skill in text:

            high_value_matches += 1

    score += min(
        high_value_matches * 4,
        20
    )


    # ========================================================
    # 8. JUNIOR / ENTRY LEVEL
    # ========================================================

    positive_match = False

    for word in POSITIVE_WORDS:

        if word in text:

            positive_match = True
            break

    if positive_match:

        score += 15


    # ========================================================
    # 9. SENIORITY PENALTY
    # ========================================================

    senior_match = False

    for word in NEGATIVE_WORDS:

        if word in title:

            senior_match = True
            break

    if senior_match:

        score -= 50


    # ========================================================
    # 10. EXPERIENCE REQUIREMENT
    # ========================================================

    experience_numbers = extract_year_requirements(
        description
    )

    if experience_numbers:

        max_years = max(
            experience_numbers
        )

        if max_years >= 7:

            score -= 35

        elif max_years >= 5:

            score -= 25

        elif max_years >= 4:

            score -= 15

        elif max_years >= 3:

            score -= 10

        elif max_years <= 2:

            score += 5


    # ========================================================
    # 11. TITLE QUALITY
    # ========================================================

    if target_role_found:

        if "analyst" in title:

            score += 5

        if "soc" in title:

            score += 5

        if (
            "tier 1" in title
            or "tier-1" in title
        ):

            score += 5

        if "l1" in title:

            score += 5


    # ========================================================
    # 12. FINAL SCORE
    # ========================================================

    score = max(
        0,
        min(
            100,
            score
        )
    )


    # ========================================================
    # RETURN
    # ========================================================

    return score, skills_found