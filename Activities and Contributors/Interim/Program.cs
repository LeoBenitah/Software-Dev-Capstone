using Octokit;
using System.Linq;
using System.Text.Json;

namespace Exampleproject;


public class OctoKitAPICall
{
    
    public IReadOnlyList<GitHubCommit> Commits { get; set; }
    public IReadOnlyList<Issue> Issues { get;  set;}
    public IReadOnlyList<PullRequest> PullRequests { get; set;}
    
    public List<PullRequestData> pullRequestData { get; set; }
    public List<CommitData> commitData { get; set; }
    public List<IssueData> issueData { get; set; }

    

    public OctoKitAPICall()
    {
        //If the Jsons already made, then retrieve the data
        if (File.Exists("commits.json") && File.Exists("issues.json") &&  File.Exists("pullrequests.json")) { RetrieveData(); }
        else
        {
            RetrieveFromGithub();
            SaveData();
        }
        
    }

    public void RetrieveFromGithub()
    {
        //Define one year ago for filtering
        var oneYearAgo = DateTimeOffset.UtcNow.Subtract(TimeSpan.FromDays(365));
        
        //Create and Use token for authentication
        var client = new GitHubClient(new ProductHeaderValue("OllamaAnalysis"));
        client.Credentials = new Credentials(APIKey.GetAPIKey());
        
        //Retrieve Commits from past 365 days
        var commitFilter = new CommitRequest { Since = oneYearAgo };
        Commits = client.Repository.Commit.GetAll("ollama", "ollama", commitFilter).Result;
        
        // Save commits to CommitData Objects
        // First Select each commit, then construct a CommitDataObject, then turn it into a list.
        commitData = Commits.Select(c => new CommitData(
            c.Sha,
            c.Commit.Author.Date,
            //Null safeguard
            c.Author?.Login ?? c.Commit.Author.Name,
            c.Url,
            c.Parents.Count
        )).ToList();
        
        //Retrieve Issues from past 365 days
        var issueFilter = new RepositoryIssueRequest { State = ItemStateFilter.All, Since = oneYearAgo };
        Issues = client.Issue.GetAllForRepository("ollama", "ollama", issueFilter).Result;
        //Keep only those created, not modified in the last year, and those that are not pull requests.
        Issues = Issues.Where(i => i.CreatedAt >= oneYearAgo).Where(i => i.PullRequest == null).ToList();
            
        // Save issues to IssueData Objects
        issueData = Issues.Select(i => new IssueData(
            i.Number,
            i.CreatedAt,
            i.User.Login,
            i.Title,
            i.Url,
            i.State,
            i.ClosedAt
        )).ToList();
        
        //Retrieve PullRequests from past 365 days
        var pullReqFilter = new PullRequestRequest { State = ItemStateFilter.All };
        PullRequests = client.PullRequest.GetAllForRepository("ollama", "ollama", pullReqFilter).Result;
        PullRequests = PullRequests.Where(pr => pr.CreatedAt >= oneYearAgo).ToList();
        
        
        // Save PullRequests to PullRequestData Objects
        pullRequestData = PullRequests.Select(pr => new PullRequestData(
            pr.Number,
            pr.CreatedAt,
            pr.User.Login,
            pr.Title,
            pr.Url,
            pr.State,
            pr.ClosedAt,
            pr.MergedAt
        )).ToList();
    }
    public void SaveData()
    {
        //Save Data objects to Json files, for efficiency
        //Write indented to make the files more readable
        var options = new JsonSerializerOptions
        {
            WriteIndented = true
        };

        File.WriteAllText(
            "commits.json",
            JsonSerializer.Serialize(commitData, options)
        );

        File.WriteAllText(
            "issues.json",
            JsonSerializer.Serialize(issueData, options)
        );

        File.WriteAllText(
            "pullrequests.json",
            JsonSerializer.Serialize(pullRequestData, options)
        );
    }

    public void RetrieveData()
    {
        commitData =
            JsonSerializer.Deserialize<List<CommitData>>(
                File.ReadAllText("commits.json")
            ) ?? new List<CommitData>();

        issueData =
            JsonSerializer.Deserialize<List<IssueData>>(
                File.ReadAllText("issues.json")
            ) ?? new List<IssueData>();

        pullRequestData =
            JsonSerializer.Deserialize<List<PullRequestData>>(
                File.ReadAllText("pullrequests.json")
            ) ?? new List<PullRequestData>();
    }

    public static void Main()
    {
        //Call the constructor
        var api = new OctoKitAPICall();
        
        Console.WriteLine($"Commit Count: {api.commitData.Count}");
        Console.WriteLine($"Issue Count: {api.issueData.Count}");
        Console.WriteLine($"Pull Request Count: {api.pullRequestData.Count}");
            
        //Verify contributer count
        var client = new GitHubClient(new ProductHeaderValue("OllamaAnalysis"));
        client.Credentials = new Credentials(APIKey.GetAPIKey());
        var contributors = client.Repository.GetAllContributors("ollama", "ollama").Result;

        Console.WriteLine($"Contributor count: {contributors.Count}");
        
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    public void MeanNumberOfCommitsPerContributor()
    {
        var contributors = Commits.Select(c => c.Committer.Id).Distinct().ToList();
        var meanNumberOfCommitsPerContributor = (double)Commits.Count / contributors.Count;
        Console.WriteLine($"Mean number of commits per contributor: {meanNumberOfCommitsPerContributor}");
    }
    
    public void MedianNumberOfCommitsPerContributor()
    {
        var contributors = Commits.Select(c => c.Committer.Id).Distinct().ToList();
        var commitsPerContributor = contributors.Select(c => Commits.Count(c2 => c2.Committer.Id == c)).OrderBy(c => c).ToList();
        var medianNumberOfCommitsPerContributor = commitsPerContributor.ElementAt(commitsPerContributor.Count / 2);
        Console.WriteLine($"Median number of commits per contributor: {medianNumberOfCommitsPerContributor}");
    }
    
    public void MeanTimeToCloseIssues()
    {
        var client = new GitHubClient(new ProductHeaderValue("WhateverYouWant"));
        client.Credentials = new Credentials(APIKey.GetAPIKey());
        var closedIssues = Issues.Where(i => i.State == ItemState.Closed).ToList();
        var timeDiffs = closedIssues.Select(i => i.ClosedAt.Value - i.CreatedAt).ToList();
        var meanTimeToCloseIssues = TimeSpan.FromTicks((long)timeDiffs.Average(t => t.Ticks));
        Console.WriteLine($"Mean time to close issues: {meanTimeToCloseIssues}");
    }
    
    public void MedianTimeToCloseIssues()
    {
        var client = new GitHubClient(new ProductHeaderValue("WhateverYouWant"));
        client.Credentials = new Credentials(APIKey.GetAPIKey());
        var closedIssues = Issues.Where(i => i.State == ItemState.Closed).ToList();
        var timeDiffs = closedIssues.Select(i => i.ClosedAt.Value - i.CreatedAt).OrderBy(t => t).ToList();
        var medianTimeToCloseIssues = TimeSpan.FromTicks((long)timeDiffs.ElementAt(timeDiffs.Count / 2).Ticks);
        Console.WriteLine($"Median time to close issues: {medianTimeToCloseIssues}");
    }

    public void MeanTimeBetweenCommits()
    {
        var commitDates = Commits.Select(c => c.Commit.Author.Date).OrderBy(d => d).ToList();
        var timeDiffs = new List<TimeSpan>();
        for (int i = 1; i < commitDates.Count; i++)
        {
            timeDiffs.Add(commitDates[i] - commitDates[i - 1]);
        }
        var meanTimeBetweenCommits = TimeSpan.FromTicks((long)timeDiffs.Average(t => t.Ticks));
        Console.WriteLine($"Mean time between commits: {meanTimeBetweenCommits}");
    }
    
    public void MedianTimeBetweenCommits()
    {
        var commitDates = Commits.Select(c => c.Commit.Author.Date).OrderBy(d => d).ToList();
        var timeDiffs = new List<TimeSpan>();
        for (int i = 1; i < commitDates.Count; i++)
        {
            timeDiffs.Add(commitDates[i] - commitDates[i - 1]);
        }
        var medianTimeBetweenCommits = TimeSpan.FromTicks((long)timeDiffs.OrderBy(t => t.Ticks).ElementAt(timeDiffs.Count / 2).Ticks);
        Console.WriteLine($"Median time between commits: {medianTimeBetweenCommits}");
    }
    public void CommitsPerMonth()
    {
        var commitsPerMonth = Commits.GroupBy(c => new { c.Commit.Author.Date.Year, c.Commit.Author.Date.Month })
            .Select(g => new { Year = g.Key.Year, Month = g.Key.Month, Count = g.Count() })
            .OrderBy(g => g.Year).ThenBy(g => g.Month)
            .ToList();

        Console.WriteLine("Commits per month:");
        foreach (var item in commitsPerMonth)
        {
            Console.WriteLine($"{item.Year}-{item.Month}: {item.Count}");
        }
    }
}
