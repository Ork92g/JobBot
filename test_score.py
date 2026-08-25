from job_score import calculate_score


job = {

    "title": "Security Analyst",

    "description": """
    We are looking for a Security Analyst
    to join our Security Operations team.

    The candidate will monitor SIEM alerts,
    investigate security incidents,
    work with Microsoft Sentinel and EDR,
    perform threat hunting,
    analyze Windows and Linux events,
    and use MITRE ATT&CK.

    Experience with Splunk and CrowdStrike
    is an advantage.

    1-2 years of experience preferred.
    """
}


score, skills = calculate_score(job)


print()
print("==============================")
print("JOB SCORE")
print("==============================")

print(
    "Score:",
    score,
    "/ 100"
)

print(
    "Matched skills:"
)

for skill in skills:

    print(
        "-",
        skill
    )