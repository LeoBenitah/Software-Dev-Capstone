import pandas as pd
import matplotlib.pyplot as plt


# Read the JSON files downloaded previously
commits = pd.read_json("commits.json")
issues = pd.read_json("issues.json")
pull_requests = pd.read_json("pullrequests.json")

# Convert dates and createdAt inputs to pd datetime types.
commits["Date"] = pd.to_datetime(commits["Date"])
issues["CreatedAt"] = pd.to_datetime(issues["CreatedAt"])
pull_requests["CreatedAt"] = pd.to_datetime(pull_requests["CreatedAt"])

# Group dates by month
commits["Month"] = commits["Date"].dt.strftime("%Y-%m")
issues["Month"] = issues["CreatedAt"].dt.strftime("%Y-%m")
pull_requests["Month"] = pull_requests["CreatedAt"].dt.strftime("%Y-%m")

# Count each activity per month
commits_monthly = commits.groupby("Month").size()
issues_monthly = issues.groupby("Month").size()
prs_monthly = pull_requests.groupby("Month").size()

# Combine them into a single dataframe
activities = pd.DataFrame({
    "Commits": commits_monthly,
    "Issues": issues_monthly,
    "Pull Requests": prs_monthly
}).fillna(0)

# Make sure every month is included
months = pd.date_range(
    start="2025-08-01",
    end="2026-09-01",
    freq="MS"
).strftime("%Y-%m")

# ensure the dataframe uses the labels stored in months
activities = activities.reindex(months, fill_value=0)

# Print the dataframe to ensure it looks correct
# print(activities)

# Plot the dataframe
activities.plot(marker="o")

plt.title("Ollama GitHub activity over the past year")
plt.xlabel("Month")
plt.ylabel("Number of activities")
plt.xticks(
    range(len(activities.index)),
    activities.index,
    rotation=45
)


plt.tight_layout()
plt.savefig("ollama_activities.png", dpi=300)
# plt.show()

# Count commits issues and pull requests by each contributor
commit_counts = commits["Contributor"].value_counts()
issue_counts = issues["Contributor"].value_counts()
pr_counts = pull_requests["Contributor"].value_counts()

# Create a dataframe containing the counts of each activity per contributor
contributors = pd.DataFrame({
    "Commits": commit_counts,
    "Issues": issue_counts,
    "Pull Requests": pr_counts
}).fillna(0)

# Calculate the total contribution column by adding Commits, Issues, and PR's by each contributor
contributors["Total"] = (
    contributors["Commits"] +
    contributors["Issues"] +
    contributors["Pull Requests"]
)
# Sort the DF by the total column
contributors = contributors.sort_values("Total", ascending=False)
# Select only the top 10 contributors
print(contributors.head(10))


contributors = [
    # "dhiltgen",
    # "ParthSareen",
    # "jmorganca",
    # "jessegross",
    # "hoyyeva",
    # "pdevine",
    # "mxyng",
    # "drifkin",
    # "BruceMacD",
    # "deepshekhardas"
]

for name in contributors:
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_colwidth", None)
    print("\n", name)

    print(
        pull_requests[
            pull_requests["Contributor"] == name
        ][["Title", "Url"]].head(20).to_string(index=False)
    )

    print(
        issues[
            issues["Contributor"] == name
        ][["Title", "Url"]]
    )

    print(
        commits[
            commits["Contributor"] == name
        ][["Url"]]
    )