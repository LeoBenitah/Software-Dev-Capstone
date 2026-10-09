namespace Exampleproject;

public class ContributorData
{
    public string Username { get; set; }

    public int CommitCount { get; set; }
    public int PullRequestCount { get; set; }
    public int IssueCount { get; set; }
    public int CommentCount { get; set; }
    public int ReviewCount { get; set; }

    public int TotalActivityCount { get; set; }

    public DateTimeOffset FirstObservedActivity { get; set; }
    public DateTimeOffset LastObservedActivity { get; set; }

    public int ActiveMonths { get; set; }
    
    public int ActivitySpanMonths { get; set; }
    public double  ActivityConsistency { get; set; }
    
    public double  ActivityPerActiveMonth { get; set; }

    public ContributorData(
        string username, 
        int commitCount,
        int  pullRequestCount,
        int issueCount,
        int commentCount,
        int reviewCount,
        DateTimeOffset firstObservedActivity,
        DateTimeOffset lastObservedActivity,
        int activeMonths)
    {
        Username = username;
        CommitCount = commitCount;
        PullRequestCount = pullRequestCount;
        IssueCount = issueCount;
        CommentCount = commentCount;
        ReviewCount = reviewCount;
        FirstObservedActivity = firstObservedActivity;
        LastObservedActivity = lastObservedActivity;
        ActiveMonths = activeMonths;
        
        // Sum the total count of all activities
        TotalActivityCount =
            commitCount +
            pullRequestCount +
            issueCount +
            commentCount +
            reviewCount;
        
        // Compute the total span of active months of each user
        ActivitySpanMonths =
            ((lastObservedActivity.Year - firstObservedActivity.Year) * 12)
            + lastObservedActivity.Month
            - firstObservedActivity.Month
            + 1;
        
        // Divide the active months by the span of time the user has contributed to the repository
        // Provides a ratio of consistency
        ActivityConsistency =
            (double)activeMonths / ActivitySpanMonths;
        
        // Compute the average activity count per month of each contributor.
        ActivityPerActiveMonth =
            (double)TotalActivityCount / activeMonths;
    }
    
}