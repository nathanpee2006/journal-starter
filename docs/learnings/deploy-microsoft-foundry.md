10/30/2026

# What did I do?

I was able to deploy the Microsoft Foundry endpoint behind a private endpoint inside a separate subnet, and make API sentiment analysis work in Azure virtual network.

# What worked?

Adding a private endpoint prohibited public access to the Microsoft Foundry endpoint, which improves security. This ensures that the application subnet is the only one allowed to communicate with the AI subnet.

When deciding which subnet to place the private endpoint I had two options. I could either place in DB subnet which also has a private endpoint for the database or create a new subnet for the AI endpoint. I ultimately chose the latter as it is clearer and mostly did it for separation of concerns.

# What I struggled with, and how did I solve it?

Initially when I was trying to connect to the domain learnlog.online I got a 502 Bad Gateway error.

First thing I did was to verify nginx was working.
```bash
sudo journalctl -u nginx.service
```

Noticed it was not starting up for some reason, the logs produced by it were not too helpful.

Next thing I tried was to verify if the API was working.
```bash
sudo journalctl -u journal.service
```

Then I noticed this log message.

```text
Oct 30 01:39:51 [hostname] uvicorn[4861]:   File "<frozen importlib._bootstrap>", line 1406, in _gcd_import
Oct 30 01:39:51 [hostname] uvicorn[4861]:   File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
...
Oct 30 01:39:51 [hostname] uvicorn[4861]:   File "/[app_root]/api/__init__.py", line 4, in <module>
Oct 30 01:39:51 [hostname] uvicorn[4861]:     from api.routers.journal_router import router as journal_router
Oct 30 01:39:51 [hostname] uvicorn[4861]:   File "/[app_root]/api/routers/journal_router.py", line 21, in <module>
Oct 30 01:39:51 [hostname] uvicorn[4861]:     from api.services.llm_service import InvalidAnalysisResponseError, analyze_journal_entry
Oct 30 01:39:51 [hostname] uvicorn[4861]:   File "/[app_root]/api/services/llm_service.py", line 14, in <module>
Oct 30 01:39:51 [hostname] uvicorn[4861]:     import httpx2
Oct 30 01:39:51 [hostname] uvicorn[4861]: ModuleNotFoundError: No module named 'httpx2'
Oct 30 01:39:51 [hostname] systemd[1]: journal.service: Main process exited, code=exited, status=1/FAILURE
```

It turned out that my API server's dependencies were not in sync with the new dependencies.

The fix was simple. The command installs the latest dependencies to the API server.
```bash
uv sync
```

I checked the status of API server, and it was back working.
```text
Oct 30 01:44:09 [hostname] systemd[1]: Started journal.service - Journal Starter FastAPI app.
Oct 30 01:44:10 [hostname] uvicorn[5072]: INFO:     Started server process [5072]
Oct 30 01:44:10 [hostname] INFO:     Waiting for application startup.
Oct 30 01:44:11 [hostname] 10/30/2026 01:44:11 AM - INFO:  database: ready
Oct 30 01:44:11 [hostname] 10/30/2026 01:44:11 AM - INFO:  application: serving
Oct 30 01:44:11 [hostname] INFO:     Application startup complete.
Oct 30 01:44:11 [hostname] INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

_Useful notes:_

// Update systemd's awareness of files

sudo systemctl daemon-reload

// Restart the process

sudo systemctl restart <service_name>

// Confirm it came back up successfully

sudo systemctl status <service_name>