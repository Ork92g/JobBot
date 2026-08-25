import requests
import re
import time
import sys

from bs4 import BeautifulSoup

from database import (
    create_database,
    is_new_job,
    save_job
)

from job_score import calculate_score


# ==========================================
# TELEGRAM
# ==========================================

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_TELEGRAM_SCORE = 65
TOP_MATCH_MIN_SCORE = 40


# ==========================================
# LINKEDIN SEARCH TERMS
# ==========================================

SEARCH_TERMS = [

    # SOC
    "SOC",
    "SOC Analyst",
    "SOC Tier 1",
    "SOC Tier 2",
    "SOC L1",
    "SOC L2",

    # Security Operations
    "Security Operations",
    "Security Operations Analyst",
    "Security Operations Center",
    "Security Operations Specialist",
    "Cyber Security Operations",
    "Cybersecurity Operations",

    # SecOps
    "SecOps",
    "SecOps Analyst",

    # Monitoring
    "Security Monitoring",
    "Security Monitoring Analyst",
    "Cybersecurity Monitoring",

    # Cyber Defense
    "Cyber Defense",
    "Cyber Defense Analyst",
    "Cybersecurity Defense",

    # Security Analyst
    "Security Analyst",
    "Cybersecurity Analyst",
    "Cyber Security Analyst",
    "Information Security Analyst",
    "IT Security Analyst",

    # MDR
    "MDR",
    "MDR Analyst",
    "Managed Detection Response",

    # Incident Response
    "Incident Response",
    "Incident Responder",
    "Incident Analyst",

    # DFIR
    "DFIR",
    "Digital Forensics",
    "Digital Forensics Incident Response",

    # Threat
    "Threat Analyst",
    "Threat Intelligence",
    "Threat Detection",
    "Threat Hunter",
    "Threat Hunting",

    # Detection
    "Detection Analyst",
    "Detection Engineer",

    # Blue Team
    "Blue Team",
    "Security Investigator",

    # General
    "Cybersecurity Specialist",
    "Cyber Security Specialist",
    "Information Security",
]


LINKEDIN_URL = (
    "https://www.linkedin.com/jobs/search/"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


# ==========================================
# GREENHOUSE
# ==========================================

GREENHOUSE_COMPANIES = {

    "Transmit Security": "transmitsecurity",
    "Armis Security": "armissecurity",

}


# ==========================================
# LEVER
# ==========================================

LEVER_COMPANIES = {

    "CYE": "CYE",

}


# ==========================================
# RELEVANT TITLE WORDS
# ==========================================

RELEVANT_TITLE_WORDS = [

    "soc",
    "soc analyst",

    "security analyst",
    "cybersecurity analyst",
    "cyber security analyst",

    "security operations",
    "security operations analyst",
    "security operations center",
    "security operations specialist",

    "cyber security operations",
    "cybersecurity operations",

    "secops",
    "secops analyst",

    "security monitoring",
    "security monitoring analyst",

    "cyber defense",
    "cyber defense analyst",

    "mdr",
    "mdr analyst",

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

    "blue team",

    "security investigator",

    "information security analyst",
    "it security analyst",

    "cybersecurity specialist",
    "cyber security specialist",

]


# ==========================================
# HARD IRRELEVANT
# ==========================================

HARD_IRRELEVANT = [

    # Management
    "senior",
    "sr.",
    "lead",
    "manager",
    "director",
    "head of",
    "principal",
    "vp",
    "vice president",
    "chief",

    # Sales
    "account executive",
    "sales",
    "sales engineer",
    "business development",
    "bdr",
    "sdr",

    # Marketing
    "marketing",
    "content",
    "communications",

    # Recruiting
    "recruiter",
    "recruiting",
    "talent acquisition",

    # Software engineering
    "software engineer",
    "frontend",
    "front end",
    "backend",
    "back end",
    "full stack",
    "mobile engineer",

    # Data / AI
    "data scientist",
    "data science",
    "machine learning",
    "ml engineer",
    "ai engineer",

    # Product
    "product manager",
    "product owner",
    "project manager",

    # Business
    "customer success",
    "finance",
    "financial",
    "legal",
    "designer",

    # Architecture / GRC
    "security architect",
    "cyber security architect",
    "cybersecurity architect",
    "solution architect",
    "enterprise architect",
    "grc",
    "governance risk compliance",

]


# ==========================================
# ADDITIONAL NEGATIVE TITLE WORDS
# ==========================================

NEGATIVE_TITLE_WORDS = [

    "architect",
    "architecture",
    "manager",
    "lead",
    "director",
    "principal",
    "head",
    "chief",
    "vp",

]


# ==========================================
# TITLE RELEVANCE
# ==========================================

def title_is_relevant(title):

    title_lower = title.lower().strip()

    # Hard exclusions first
    for word in HARD_IRRELEVANT:

        if word in title_lower:

            return False

    # Relevant terms
    for word in RELEVANT_TITLE_WORDS:

        if word in title_lower:

            return True

    return False


# ==========================================
# JOB ID
# ==========================================

def extract_job_id(link):

    match = re.search(
        r"/jobs/view/(\d+)",
        link
    )

    if match:

        return match.group(1)

    return None


# ==========================================
# LINKEDIN
# ==========================================

def get_linkedin_jobs(search_term):

    params = {

        "keywords": search_term,

        "location": "Israel",

    }

    response = requests.get(

        LINKEDIN_URL,

        params=params,

        headers=HEADERS,

        timeout=20

    )

    print(
        f"LinkedIn status: "
        f"{response.status_code}"
    )

    if response.status_code != 200:

        return []

    soup = BeautifulSoup(

        response.text,

        "html.parser"

    )

    cards = soup.find_all(

        "div",

        class_="base-card"

    )

    results = []

    for card in cards:

        title = card.find("h3")

        company = card.find("h4")

        location = card.find(

            "span",

            class_="job-search-card__location"

        )

        link_element = card.find("a")

        if not title:

            continue

        if not company:

            continue

        if not link_element:

            continue

        link = link_element.get("href")

        if not link:

            continue

        job_id = extract_job_id(link)

        if not job_id:

            continue

        results.append({

            "job_id":
                f"linkedin-{job_id}",

            "title":
                title.get_text(
                    strip=True
                ),

            "company":
                company.get_text(
                    strip=True
                ),

            "location":
                (
                    location.get_text(
                        strip=True
                    )
                    if location
                    else "Unknown"
                ),

            "link":
                link,

            "description":
                ""

        })

    return results


# ==========================================
# GREENHOUSE
# ==========================================

def get_greenhouse_jobs(
    company_name,
    board_token
):

    url = (

        "https://boards-api.greenhouse.io/"

        f"v1/boards/{board_token}/jobs"

        "?content=true"

    )

    try:

        response = requests.get(

            url,

            timeout=20

        )

    except requests.RequestException as error:

        print(
            f"{company_name}: ERROR "
            f"{error}"
        )

        return []

    print(

        f"{company_name}: "
        f"HTTP {response.status_code}"

    )

    if response.status_code != 200:

        return []

    try:

        data = response.json()

    except ValueError:

        return []

    results = []

    for job in data.get(
        "jobs",
        []
    ):

        job_id = job.get("id")

        title = job.get(
            "title",
            ""
        )

        link = job.get(
            "absolute_url",
            ""
        )

        description = job.get(
            "content",
            ""
        )

        location = (

            job

            .get(
                "location",
                {}
            )

            .get(
                "name",
                "Unknown"
            )

        )

        if not job_id:

            continue

        if not title:

            continue

        if not link:

            continue

        results.append({

            "job_id": (

                f"greenhouse-"
                f"{company_name}-"
                f"{job_id}"

            ),

            "title":
                title,

            "company":
                company_name,

            "location":
                location,

            "link":
                link,

            "description":
                description

        })

    return results


# ==========================================
# LEVER
# ==========================================

def get_lever_jobs(
    company_name,
    company_slug
):

    url = (

        "https://api.lever.co/v0/postings/"

        f"{company_slug}"

        "?mode=json"

    )

    try:

        response = requests.get(

            url,

            timeout=20

        )

    except requests.RequestException as error:

        print(
            f"{company_name}: ERROR "
            f"{error}"
        )

        return []

    print(

        f"{company_name}: "
        f"HTTP {response.status_code}"

    )

    if response.status_code != 200:

        return []

    try:

        data = response.json()

    except ValueError:

        return []

    results = []

    for job in data:

        job_id = job.get(
            "id"
        )

        title = job.get(
            "text",
            ""
        )

        link = job.get(
            "hostedUrl",
            ""
        )

        description = (

            job.get(
                "descriptionPlain",
                ""
            )

        )

        categories = job.get(
            "categories",
            {}
        )

        location = categories.get(
            "location",
            "Unknown"
        )

        if not job_id:

            continue

        if not title:

            continue

        if not link:

            continue

        results.append({

            "job_id": (

                f"lever-"
                f"{company_name}-"
                f"{job_id}"

            ),

            "title":
                title,

            "company":
                company_name,

            "location":
                location,

            "link":
                link,

            "description":
                description

        })

    return results


# ==========================================
# DUPLICATES
# ==========================================

def remove_duplicates(jobs):

    unique = {}

    for job in jobs:

        job_id = job.get(
            "job_id"
        )

        if not job_id:

            continue

        if job_id not in unique:

            unique[job_id] = job

    return list(
        unique.values()
    )


# ==========================================
# TELEGRAM
# ==========================================

def send_telegram(message):

    url = (

        "https://api.telegram.org/"

        f"bot{BOT_TOKEN}/sendMessage"

    )

    data = {

        "chat_id":
            CHAT_ID,

        "text":
            message,

        "disable_web_page_preview":
            False

    }

    try:

        response = requests.post(

            url,

            data=data,

            timeout=20

        )

        print(
            f"Telegram: "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print(
                response.text
            )

            return False

        return True

    except requests.RequestException as error:

        print(
            f"Telegram ERROR: "
            f"{error}"
        )

        return False


# ==========================================
# TELEGRAM MESSAGE
# ==========================================

def create_message(
    job,
    score,
    skills
):

    message = (

        "🚨 NEW SOC JOB\n\n"

        f"🎯 MATCH: {score}/100\n\n"

        f"💼 {job['title']}\n"

        f"🏢 {job['company']}\n"

        f"📍 {job['location']}\n"

    )

    if skills:

        message += (
            "\n🛠 Relevant skills:\n"
        )

        for skill in skills[:10]:

            message += (
                f"• {skill}\n"
            )

    message += (

        "\n🔗 APPLY:\n"

        f"{job['link']}"

    )

    return message


# ==========================================
# MAIN
# ==========================================

def main():

    test_alert = (
        "--test-alert"
        in sys.argv
    )

    print()

    print(
        "========================================"
    )

    print(
        "          SOC JOB HUNTER V5"
    )

    print(
        "========================================"
    )

    if test_alert:

        print()
        print(
            "⚠️ TEST ALERT MODE ENABLED"
        )


    # ======================================
    # DATABASE
    # ======================================

    create_database()


    all_jobs = []


    # ======================================
    # LINKEDIN
    # ======================================

    print()

    print(
        "========== LINKEDIN =========="
    )


    for search_term in SEARCH_TERMS:

        print()

        print(
            f"Searching: "
            f"{search_term}"
        )

        try:

            jobs = get_linkedin_jobs(
                search_term
            )

            print(
                f"Found: "
                f"{len(jobs)}"
            )

            all_jobs.extend(
                jobs
            )

        except Exception as error:

            print(
                f"ERROR: "
                f"{error}"
            )

        time.sleep(2)


    # ======================================
    # GREENHOUSE
    # ======================================

    print()

    print(
        "========== GREENHOUSE =========="
    )


    for company, token in (
        GREENHOUSE_COMPANIES.items()
    ):

        jobs = get_greenhouse_jobs(
            company,
            token
        )

        print(
            f"Found: "
            f"{len(jobs)}"
        )

        all_jobs.extend(
            jobs
        )


    # ======================================
    # LEVER
    # ======================================

    print()

    print(
        "========== LEVER =========="
    )


    for company, slug in (
        LEVER_COMPANIES.items()
    ):

        jobs = get_lever_jobs(
            company,
            slug
        )

        print(
            f"Found: "
            f"{len(jobs)}"
        )

        all_jobs.extend(
            jobs
        )


    # ======================================
    # UNIQUE
    # ======================================

    unique_jobs = remove_duplicates(
        all_jobs
    )


    # ======================================
    # SCORE
    # ======================================

    scored_jobs = []


    for job in unique_jobs:

        if not title_is_relevant(
            job["title"]
        ):

            continue

        score, skills = calculate_score(
            job
        )

        job["score"] = score

        job["skills"] = skills

        scored_jobs.append(
            job
        )


    # ======================================
    # SORT
    # ======================================

    scored_jobs.sort(

        key=lambda job:
            job["score"],

        reverse=True

    )


    # ======================================
    # DATABASE
    # ======================================

    new_jobs = []


    for job in scored_jobs:

        if is_new_job(
            job["job_id"]
        ):

            save_job(
                job
            )

            new_jobs.append(
                job
            )


    # ======================================
    # SUMMARY
    # ======================================

    print()

    print(
        "========================================"
    )

    print(
        "             FINAL SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        f"TOTAL RAW JOBS: "
        f"{len(all_jobs)}"
    )

    print(
        f"TOTAL UNIQUE JOBS: "
        f"{len(unique_jobs)}"
    )

    print(
        f"RELEVANT JOBS: "
        f"{len(scored_jobs)}"
    )

    print(
        f"NEW JOBS: "
        f"{len(new_jobs)}"
    )


    # ======================================
    # TOP MATCHES
    # ======================================

    print()

    print(
        "========================================"
    )

    print(
        "             TOP MATCHES"
    )

    print(
        "========================================"
    )


    displayed = 0


    for job in scored_jobs:

        if job["score"] < TOP_MATCH_MIN_SCORE:

            continue

        displayed += 1

        print()

        print(
            f"{displayed}. "
            f"{job['title']}"
        )

        print(
            f"   Company: "
            f"{job['company']}"
        )

        print(
            f"   Location: "
            f"{job['location']}"
        )

        print(
            f"   SCORE: "
            f"{job['score']}/100"
        )

        if job["skills"]:

            print(
                "   Skills: "
                + ", ".join(
                    job["skills"][:10]
                )
            )

        print(
            f"   Link: "
            f"{job['link']}"
        )

    if displayed == 0:

        print(
            "No strong matches found."
        )


    # ======================================
    # TELEGRAM
    # ======================================

    print()

    print(
        "========================================"
    )

    print(
        "          TELEGRAM ALERTS"
    )

    print(
        "========================================"
    )


    telegram_count = 0


    # TEST MODE
    if test_alert:

        test_job = None

        for job in scored_jobs:

            if job["score"] >= MIN_TELEGRAM_SCORE:

                test_job = job

                break

        if test_job:

            print()

            print(
                "Sending TEST alert: "
                f"{test_job['title']} "
                f"({test_job['score']}/100)"
            )

            message = create_message(

                test_job,

                test_job["score"],

                test_job["skills"]

            )

            if send_telegram(message):

                telegram_count += 1

        else:

            print(
                "No job with sufficient "
                "score for test alert."
            )


    # NORMAL MODE
    else:

        for job in new_jobs:

            if job["score"] < MIN_TELEGRAM_SCORE:

                continue

            message = create_message(

                job,

                job["score"],

                job["skills"]

            )

            if send_telegram(message):

                telegram_count += 1


    print()

    print(
        f"TELEGRAM SENT: "
        f"{telegram_count}"
    )


    # ======================================
    # DONE
    # ======================================

    print()

    print(
        "========================================"
    )

    print(
        "DONE"
    )

    print(
        "========================================"
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()