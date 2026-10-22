import pandas as pd
from pathlib import Path


dir = Path(__file__).resolve().parent.parent / "Health 1-3 - Final" / "contributors.json"
contributors = pd.read_json(dir)

# Group 1: Exactly one non-comment, non-review contribution
group1 = contributors[(contributors["TotalActivityCount"] == 1) & (contributors["CommentCount"] == 0) & (contributors["ReviewCount"] == 0)]

# Group 2: 2-4 contributions with at least one non-comment, non-review
group2 = contributors[
    ((contributors["TotalActivityCount"] >= 2)
      & (contributors["TotalActivityCount"] <= 4))
        & ((contributors["CommitCount"] > 0) | (contributors["PullRequestCount"] > 0) | (contributors["IssueCount"] > 0))
    ]

sample1 = group1.sample(n=5)
sample2 = group2.sample(n=5)

print(sample1)

print(sample2)