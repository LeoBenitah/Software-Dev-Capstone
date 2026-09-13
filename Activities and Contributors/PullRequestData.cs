using Octokit;

namespace Exampleproject;

public class PullRequestData
{
    public int Number { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public string Contributor { get; set; }
    public string Title { get; set; }
    public string Url { get; set; }
    public StringEnum<ItemState> State { get; set; }
    public DateTimeOffset? ClosedAt { get; set; }
    public DateTimeOffset? MergedAt { get; set; }

    public PullRequestData(int number, DateTimeOffset createdAt, string contributor,  string title,  string url, StringEnum<ItemState> state, DateTimeOffset? closedAt, DateTimeOffset? mergedAt)
    {
        Number = number;
        CreatedAt = createdAt;
        Contributor = contributor;
        Title = title;
        Url = url;
        State = state;
        ClosedAt = closedAt;
        MergedAt = mergedAt;
    }
}