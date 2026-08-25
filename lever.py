import requests


# ==========================================
# LEVER COMPANIES
# ==========================================

LEVER_COMPANIES = {
    "CYE": "CYE",
}


# ==========================================
# GET LEVER JOBS
# ==========================================

def get_lever_jobs(company_name, company_slug):

    url = (
        f"https://api.lever.co/v0/postings/"
        f"{company_slug}?mode=json"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

    except requests.RequestException as error:

        print(
            f"{company_name}: ERROR {error}"
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

        print(
            f"{company_name}: INVALID JSON"
        )

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

        description = job.get(
            "descriptionPlain",
            ""
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

            "job_id":
                f"lever-{company_name}-{job_id}",

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
# TEST
# ==========================================

def main():

    print()
    print("========================================")
    print("             LEVER TEST")
    print("========================================")

    all_jobs = []

    for company, slug in LEVER_COMPANIES.items():

        print()
        print(
            f"Searching: {company}"
        )

        jobs = get_lever_jobs(
            company,
            slug
        )

        print(
            f"Found: {len(jobs)}"
        )

        all_jobs.extend(
            jobs
        )

    print()
    print("========================================")
    print(
        f"TOTAL LEVER JOBS: {len(all_jobs)}"
    )
    print("========================================")

    for number, job in enumerate(
        all_jobs,
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


if __name__ == "__main__":

    main()