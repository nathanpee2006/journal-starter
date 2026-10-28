10/26/2026

# What did I do?
Mostly dealt with merge conflicts and trying to get the different APIs to work.

# What worked?
Currently, got CRUD APIs working. However, AI analysis is still in progress.

# What I struggled with, and how did I solve it?
Merge conflicts were a bit hard to understand, but it is actually quite simple. There is what you call `origin` and `upstream`. Both of these are URLs of remote repositories in GitHub. `upstream` refers to the source repo, while `origin` is the forked repository that came from the source repo.

```text
(journal-api) vscode ➜ /workspaces (main) $ git remote -v
origin  https://github.com/nathanpee2006/journal-starter.git (fetch)
origin  https://github.com/nathanpee2006/journal-starter.git (push)
upstream        https://github.com/learntocloud/journal-starter.git (fetch)
upstream        https://github.com/learntocloud/journal-starter.git (push)
```

When merging `origin` uses `upstream` as a reference for the changes. Handling merge conflicts is easier with the editor. It showed the incoming vs. current changes and the bottom pane below shows the result of choosing either of the two.

