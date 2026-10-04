import pandas as pd
import matplotlib.pyplot as plt
import json


commits = pd.read_json("commits.json")
issues = pd.read_json("issues.json")
pullrequests = pd.read_json("pullrequests.json")
comments = pd.read_json("comments.json")
reviews = pd.read_json("reviews.json")
contributors = pd.read_json("contributors.json")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", None)

print("\n Contributor Involvement Analysis: ")

"""
TABLE 1
"""
print("\nTotal Activity Count Metrics: \n", contributors["TotalActivityCount"].describe(
    percentiles=[0.25, 0.50, 0.57, 0.75, 0.85, 0.90, 0.95, 0.99]
))

top10 = contributors.nlargest(10, "TotalActivityCount")

print("\nTop 10 contributors: \n", top10[["Username", "TotalActivityCount"]])

"""
TABLE 2
"""
print("\nTotal Active mMnths Metrics: \n",
    contributors["ActiveMonths"].describe(
        percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    )
)

"""
TABLE 3
"""
groups = {
    "Less than 5 contributions": contributors["TotalActivityCount"] < 5,
    "5 to 23 contributions": (
        (contributors["TotalActivityCount"] >= 5) &
        (contributors["TotalActivityCount"] <= 23)
    ),
    "24 or more contributions": contributors["TotalActivityCount"] >= 24
}
    

for name, condition in groups.items():
    print(f"\n{name}")

    print(
        "Active less than 3 months:",
        (condition & (contributors["ActiveMonths"] < 3)).sum()
    )

    print(
        "Active at least 3 months:",
        (condition & (contributors["ActiveMonths"] >= 3)).sum()
    )

    print(
        "Active at least 5 months:",
        (condition & (contributors["ActiveMonths"] >= 5)).sum()
    )


"""
Newcomer and Dormant contributor analysis
"""
print("\nNewcomer and Dormant contributor analysis: ")

recent_low_activity = contributors[
    (contributors["TotalActivityCount"] <= 3) &
    (pd.to_datetime(contributors["FirstObservedActivity"]) >= pd.Timestamp("2026-08-03", tz="UTC"))
]

print("Number of contributors with 3 or less contributions, whose first contribution was in the last 2 months: ", len(recent_low_activity))

recent_low_activity = contributors[
    (contributors["TotalActivityCount"] <= 3) &
    (pd.to_datetime(contributors["FirstObservedActivity"]) >= pd.Timestamp("2026-09-03", tz="UTC"))
]

print("Number of contributors with 5 or more contributions, whose first contribution was in the last 1 months: ", len(recent_low_activity))


dormant_activity_1 = contributors[
    (contributors["TotalActivityCount"] >= 5) &
    (pd.to_datetime(contributors["LastObservedActivity"]) <= pd.Timestamp("2026-07-03", tz="UTC"))
]
print("Number of contributors with 5 or more contributions, whose last contribution was before last 3 months: ", len(dormant_activity_1))

dormant_activity_2 = contributors[
    (contributors["TotalActivityCount"] >= 5) &
    (pd.to_datetime(contributors["LastObservedActivity"]) <= pd.Timestamp("2026-05-03", tz="UTC"))
]

print("Number of contributors with 5 or more contributions, whose last contribution was before last 5 months: ", len(dormant_activity_2))


print("\nProcess Analysis: ")

"""
PART 3: Process analysis
"""
# Turn the date columns into actual datetime values first
issues["CreatedAt"] = pd.to_datetime(issues["CreatedAt"], utc=True)
issues["ClosedAt"] = pd.to_datetime(issues["ClosedAt"], utc=True)

pullrequests["CreatedAt"] = pd.to_datetime(pullrequests["CreatedAt"], utc=True)
pullrequests["ClosedAt"] = pd.to_datetime(pullrequests["ClosedAt"], utc=True)
pullrequests["MergedAt"] = pd.to_datetime(pullrequests["MergedAt"], utc=True)

comments["CreatedAt"] = pd.to_datetime(comments["CreatedAt"], utc=True)
reviews["SubmittedAt"] = pd.to_datetime(reviews["SubmittedAt"], utc=True)


# Quick check that the issue and PR data is actually in the right date range
print("Earliest issue:", issues["CreatedAt"].min())
print("Latest issue:", issues["CreatedAt"].max())

print("Earliest PR:", pullrequests["CreatedAt"].min())
print("Latest PR:", pullrequests["CreatedAt"].max())


# Work out how long closed issues took to get resolved
closed_issues = issues[issues["ClosedAt"].notna()].copy()

closed_issues["ResolutionHours"] = (
    closed_issues["ClosedAt"] - closed_issues["CreatedAt"]
).dt.total_seconds() / 3600

median_issue_resolution_hours = closed_issues["ResolutionHours"].median()
mean_issue_resolution_hours = closed_issues["ResolutionHours"].mean()


# Work out how long merged PRs took to get merged
merged_prs = pullrequests[pullrequests["MergedAt"].notna()].copy()

merged_prs["MergeHours"] = (
    merged_prs["MergedAt"] - merged_prs["CreatedAt"]
).dt.total_seconds() / 3600

median_pr_merge_hours = merged_prs["MergeHours"].median()
mean_pr_merge_hours = merged_prs["MergeHours"].mean()


# Match comments to issues so we can find the first comment from somebody else
issue_comments = comments.merge(
    issues[["Number", "CreatedAt", "ClosedAt", "Contributor"]],
    left_on="ParentNumber",
    right_on="Number",
    how="inner",
    suffixes=("_Comment", "_Issue")
)

# Ignore comments from the person who opened the issue
issue_comments = issue_comments[
    issue_comments["Contributor_Comment"] != issue_comments["Contributor_Issue"]
]

# Find the first external comment on each issue
first_issue_comments = (
    issue_comments
    .groupby("Number")["CreatedAt_Comment"]
    .min()
    .reset_index()
    .rename(columns={"CreatedAt_Comment": "CommentTime"})
)

# Add the issue close time too, since closing the issue is also a project action
first_issue_actions = issues[
    ["Number", "CreatedAt", "ClosedAt"]
].merge(
    first_issue_comments,
    on="Number",
    how="left"
)

# Use whichever happened first: an external comment or the issue being closed
first_issue_actions["FirstActionTime"] = (
    first_issue_actions[["CommentTime", "ClosedAt"]]
    .min(axis=1)
)

# Ignore issues where nothing happened yet
first_issue_actions = first_issue_actions[
    first_issue_actions["FirstActionTime"].notna()
].copy()

# Calculate how long that first project action took
first_issue_actions["ResponseHours"] = (
    first_issue_actions["FirstActionTime"] -
    first_issue_actions["CreatedAt"]
).dt.total_seconds() / 3600

median_issue_first_response_hours = first_issue_actions["ResponseHours"].median()
mean_issue_first_response_hours = first_issue_actions["ResponseHours"].mean()


# Match comments to PRs so we can find the first external comment
pr_comments = comments.merge(
    pullrequests[["Number", "CreatedAt", "ClosedAt", "MergedAt", "Contributor"]],
    left_on="ParentNumber",
    right_on="Number",
    how="inner",
    suffixes=("_Comment", "_PR")
)

# Ignore comments written by the PR author
pr_comments = pr_comments[
    pr_comments["Contributor_Comment"] != pr_comments["Contributor_PR"]
]

# Find the first external comment on each PR
first_pr_comments = (
    pr_comments
    .groupby("Number")["CreatedAt_Comment"]
    .min()
    .reset_index()
    .rename(columns={"CreatedAt_Comment": "CommentTime"})
)


# Find the first formal review on each PR
first_pr_reviews = (
    reviews
    .groupby("PullRequestNumber")["SubmittedAt"]
    .min()
    .reset_index()
    .rename(columns={
        "PullRequestNumber": "Number",
        "SubmittedAt": "ReviewTime"
    })
)


# Put all the possible first PR actions together
first_pr_actions = (
    pullrequests[
        ["Number", "CreatedAt", "ClosedAt", "MergedAt"]
    ]
    .merge(first_pr_comments, on="Number", how="left")
    .merge(first_pr_reviews, on="Number", how="left")
)

# Use whichever happened first: comment, review, merge or closure
first_pr_actions["FirstActionTime"] = (
    first_pr_actions[
        ["CommentTime", "ReviewTime", "MergedAt", "ClosedAt"]
    ]
    .min(axis=1)
)

# Ignore PRs where nothing happened yet
first_pr_actions = first_pr_actions[
    first_pr_actions["FirstActionTime"].notna()
].copy()

# Calculate how long the first project action took
first_pr_actions["ResponseHours"] = (
    first_pr_actions["FirstActionTime"] -
    first_pr_actions["CreatedAt"]
).dt.total_seconds() / 3600

median_pr_first_response_hours = first_pr_actions["ResponseHours"].median()
mean_pr_first_response_hours = first_pr_actions["ResponseHours"].mean()


# See how much of the formal review work is done by the top 10 reviewers
reviews_per_contributor = reviews["Contributor"].value_counts()

top10_review_count = reviews_per_contributor.head(10).sum()

top10_reviewer_share_percentage = (
    top10_review_count / len(reviews) * 100
)


# Print the final process metrics
print("\nIssue Resolution Time")
print(f"Median: {median_issue_resolution_hours:.2f} hours")
print(f"Mean:   {mean_issue_resolution_hours:.2f} hours")

print("\nPR Merge Time")
print(f"Median: {median_pr_merge_hours:.2f} hours")
print(f"Mean:   {mean_pr_merge_hours:.2f} hours")

print("\nIssue First Response Time")
print(f"Median: {median_issue_first_response_hours:.2f} hours")
print(f"Mean:   {mean_issue_first_response_hours:.2f} hours")

print("\nPR First Response Time")
print(f"Median: {median_pr_first_response_hours:.2f} hours")
print(f"Mean:   {mean_pr_first_response_hours:.2f} hours")

print("\nTop 10 Reviewer Share")
print(f"{top10_reviewer_share_percentage:.2f}%")

"""
Targeted Analysis section
"""
# Find the 2 issues with the longest first project action times
top_2_slowest_issues = first_issue_actions.nlargest(
    2,
    "ResponseHours"
)

print("\nTop 2 Slowest Issue First Actions")

print(
    top_2_slowest_issues[
        ["Number", "CreatedAt", "FirstActionTime", "ResponseHours"]
    ].to_string(index=False)
)

# Find the 2 PRs with the longest first project action times
top_2_slowest_prs = first_pr_actions.nlargest(
    2,
    "ResponseHours"
)

print("\nTop 2 Slowest PR First Actions")

print(
    top_2_slowest_prs[
        ["Number", "CreatedAt", "FirstActionTime", "ResponseHours"]
    ].to_string(index=False)
)



"""
BOT DETECTION
"""
# Get the 50 contributors with the highest total activity
top_50 = contributors.nlargest(
    50,
    "TotalActivityCount"
).copy()


# These are the activity count columns we want to compare
activity_columns = [
    "CommitCount",
    "PullRequestCount",
    "IssueCount",
    "CommentCount",
    "ReviewCount"
]


# Find which activity type each contributor does the most
top_50["DominantActivityType"] = (
    top_50[activity_columns]
    .idxmax(axis=1)
    .str.replace("Count", "")
)


# Work out what percentage of their total activity comes from that activity type
top_50["DominantActivityPercentage"] = (
    top_50[activity_columns].max(axis=1)
    / top_50["TotalActivityCount"]
    * 100
)


# Keep just the columns useful for this bot analysis
top_50_activity = top_50[
    [
        "Username",
        "CommitCount",
        "PullRequestCount",
        "IssueCount",
        "CommentCount",
        "ReviewCount",
        "TotalActivityCount",
        "DominantActivityType",
        "DominantActivityPercentage"
    ]
].copy()


# Round the percentage so the table is easier to read
top_50_activity["DominantActivityPercentage"] = (
    top_50_activity["DominantActivityPercentage"].round(1)
)


# Print the whole table without pandas cutting rows off
print(
    top_50_activity.to_string(
        index=False
    )
)


"""
Similarity Matching
"""
from rapidfuzz import fuzz
from itertools import combinations

# Load contributor identity data
identities = pd.read_json("contributors.json")

usernames = identities["Username"].dropna().unique().tolist()

username_pairs = []

for a, b in combinations(usernames, 2):

    # Only convert to lowercase.
    # Do NOT remove symbols or numbers.
    score = fuzz.ratio(a.lower(), b.lower())

    if score >= 70:
        username_pairs.append({
            "Username1": a,
            "Username2": b,
            "Similarity": score
        })

similar_usernames = pd.DataFrame(username_pairs)

if not similar_usernames.empty:
    similar_usernames = similar_usernames.sort_values(
        "Similarity",
        ascending=False
    )

print("\nTOP 25 SIMILAR USERNAMES")
print(similar_usernames.head(25).to_string(index=False))

identities = pd.read_json("contributoridentities.json")


"""
Exploration
"""
shared_candidates = identities[
    (identities["Names"].apply(len) > 1) |
    (identities["Emails"].apply(len) > 1)
]

print(
    shared_candidates[
        ["Username", "Names", "Emails"]
    ].to_string(index=False)
)