import requests

from database import (
    create_database,
    is_new_job,
    save_job
)

from job_score import calculate_score

from sources import GREENHOUSE_COMPANIES


# ==========================================
# TELEGRAM
# ==========================================

BOT_TOKEN = "8699881487:AAGypXS3cY_AtFlZ-cSFM-JpAsVHLffclEE"
CHAT_ID = "504100909"


# ==========================================
# FILTER
# ==========================================

RELEVANT_WORDS = [
    "soc",
    "security analyst",
    "cybersecurity analyst",
    "cyber security analyst",
    "mdr",
    "secops",
    "security operations",
    "incident response",
    "incident responder",
    "dfir",
    "threat intelligence",
    "threat analyst",
    "cyber analyst",
    "security research",
    "security engineer",
    "it security",
    "information security",
    "cybersecurity",
    "אבטחת מידע",
    "סייבר"
]


EXCLUDED_WORDS = [
    "senior",
    "sr.",
    "lead",
    "manager",
    "director",
    "head",
    "principal",
    "architect",
    "vp",
    "vice president",
    "chief",
    "staff"
]


# ==========================================
# RELEVANCE
# ==========================================

def is_relevant(job):

    title = job["title"].lower()

    for word in EXCLUDED_WORDS:

        if word in title:
            return False

    for word in RELEVANT_WORDS:

        if word in title:
            return True

    return False


# ==========================================
# GREENHOUSE
# ==========================================

def get_jobs(company_name, board_token):

    url = (
        "https://boards-api.greenhouse.io/v1/boards/"
        f"{board_token}/jobs?content=true"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

    except requests.RequestException as error:

        print(
            f"{company_name}: ERROR - {error}"
        )

        return []

    print(
        f"{company_name}: HTTP {response.status_code}"
    )

    if response.status_code != 200:

        return []

    try:

        data = response.json()

    except ValueError:

        print(
            f"{company_name}: Invalid JSON"
        )

        return []

    jobs = []

    for job in data.get("jobs", []):

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
            job.get("location", {})
            .get("name", "Unknown")
        )

        if not job_id:
            continue

        if not title:
            continue

        if not link:
            continue

        jobs.append({

            "job_id":
                f"{company_name}-{job_id}",

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

    return jobs


# ==========================================
# TELEGRAM
# ==========================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=20
        )

        print(
            "Telegram:",
            response.status_code
        )

        return response.status_code == 200

    except requests.RequestException as error:

        print(
            "Telegram ERROR:",
            error
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
        f"💼 {job['title']}\n"
        f"🏢 {job['company']}\n"
        f"📍 {job['location']}\n\n"
        f"🎯 Match Score: {score}/100\n"
    )

    if skills:

        message += (
            "\n🛠 Skills detected:\n"
        )

        for skill in skills[:10]:

            message += (
                f"• {skill}\n"
            )

    message += (
        "\n🔗 Apply:\n"
        f"{job['link']}"
    )

    return message


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("========================================")
    print("          SOC JOB HUNTER")
    print("========================================")


    create_database()


    # --------------------------------------
    # COLLECT
    # --------------------------------------

    all_jobs = []


    for company, token in GREENHOUSE_COMPANIES.items():

        jobs = get_jobs(
            company,
            token
        )

        print(
            f"   Jobs found: {len(jobs)}"
        )

        all_jobs.extend(jobs)


    print()
    print(
        "TOTAL JOBS FOUND:",
        len(all_jobs)
    )


    # --------------------------------------
    # DEDUPLICATE
    # --------------------------------------

    unique_jobs = {}


    for job in all_jobs:

        unique_jobs[
            job["job_id"]
        ] = job


    all_jobs = list(
        unique_jobs.values()
    )


    print(
        "UNIQUE JOBS:",
        len(all_jobs)
    )


    # --------------------------------------
    # FILTER
    # --------------------------------------

    relevant_jobs = []


    for job in all_jobs:

        if is_relevant(job):

            relevant_jobs.append(job)


    print(
        "RELEVANT JOBS:",
        len(relevant_jobs)
    )


    # --------------------------------------
    # NEW JOBS
    # --------------------------------------

    new_jobs = []


    for job in relevant_jobs:

        if is_new_job(
            job["job_id"]
        ):

            save_job(job)

            new_jobs.append(job)


    print(
        "NEW JOBS:",
        len(new_jobs)
    )


    # --------------------------------------
    # SEND
    # --------------------------------------

    for job in new_jobs:

        score, skills = calculate_score(
            job
        )

        message = create_message(
            job,
            score,
            skills
        )

        print()
        print(
            f"Sending: {job['title']}"
        )

        print(
            f"Score: {score}/100"
        )

        send_telegram(
            message
        )


    print()
    print("========================================")
    print("DONE")
    print("========================================")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()