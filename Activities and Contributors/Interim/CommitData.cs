namespace Exampleproject;

public class CommitData
{
    public string Sha { get; set; }
    public DateTimeOffset Date { get; set; }
    public string Contributor { get; set; }
    public string Url { get; set; }
    public int ParentCount { get; set; }
    
    public CommitData(string sha, DateTimeOffset date, string contributor,  string url, int parentCount)
    {
        Sha = sha;
        Date = date;
        Contributor = contributor;
        Url = url;
        ParentCount = parentCount;
    }
}