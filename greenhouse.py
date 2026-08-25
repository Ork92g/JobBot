import requests
import re


# ==========================================
# COMPANIES
# ==========================================

COMPANIES = {
    "Transmit Security": "transmitsecurity",
}


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
    "chief"
]


def is_relevant(job):

    title = job["title"].lower()

    # Reject obvious senior/management jobs
    for word in EXCLUDED_WORDS:

        if word in title:
            return False

    # Accept relevant jobs
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

    response = requests.get(
        url,
        timeout=20
    )

    print(
        f"{company_name}: {response.status_code}"
    )

    if response.status_code != 200:

        return []

    data = response.json()

    jobs = []

    for job in data.get("jobs", []):

        location = job.get(
            "location",
            {}
        ).get(
            "name",
            "Unknown"
        )

        jobs.append({

            "job_id": str(
                job.get("id", "")
            ),

            "title": job.get(
                "title",
                ""
            ),

            "company": company_name,

            "location": location,

            "link": job.get(
                "absolute_url",
                ""
            ),

            "description": job.get(
                "content",
                ""
            )
        })

    return jobs


# ==========================================
# MAIN
# ==========================================

all_jobs = []


print()
print("========================================")
print("       GREENHOUSE JOB SEARCH")
print("========================================")


for company, token in COMPANIES.items():

    jobs = get_jobs(
        company,
        token
    )

    all_jobs.extend(jobs)


# ==========================================
# FILTER
# ==========================================

relevant_jobs = []


for job in all_jobs:

    if is_relevant(job):

        relevant_jobs.append(job)


# ==========================================
# RESULTS
# ==========================================

print()
print("========================================")
print("             RESULTS")
print("========================================")

print(
    "TOTAL JOBS:",
    len(all_jobs)
)

print(
    "RELEVANT JOBS:",
    len(relevant_jobs)
)


for number, job in enumerate(
    relevant_jobs,
    start=1
):

    print()
    print(
        f"{number}. {job['title']}"
    )

    print(
        f"   Company: {job['company']}"
    )

    print(
        f"   Location: {job['location']}"
    )

    print(
        f"   Link: {job['link']}"
    )