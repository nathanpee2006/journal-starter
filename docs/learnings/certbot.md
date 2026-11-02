11/02/2026

# What did I do?

Verified that certificate renewal works using certbot.

# What worked?

A dry-run renewal was executed successfully using:

```bash
sudo certbot renew --dry-run
```

Terminal output

```text
Congratulations, all simulated renewals succeeded:
  /etc/letsencrypt/live/learnlog.online/fullchain.pem (success)
```

Verification that the timer is active is used with this command:

```bash
systemctl status certbot.timer
```

Terminal output

```
certbot.timer - Run certbot twice daily
    Loaded: loaded (/usr/lib/systemd/system/certbot.timer; enabled; preset: enabled)
    Active: active (waiting) since Sun 2026-11-01 23:44:02 UTC; 51min ago
    Trigger: Mon 2026-11-02 04:44:40 UTC; 4h 9min left
    Triggers: - certbot.service
```

# What I struggled with, and how I solved it?

Initially, when trying to obtain a certificate from Let's Encrypt certificate authority where some challenges failed.

```bash
sudo certbot --nginx -d learnlog.online -d www.learnlog.online
```

Terminal output

```text
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for learnlog.online and www.learnlog.online

Certbot failed to authenticate some domains (authenticator: nginx). The Certificate Authority reported these problems:
  Domain: learnlog.online
  Type:   connection
  Detail: 172.196.18.127: Fetching http://learnlog.online/.well-known/acme-challenge/4AOF0XYpobBzNeC3_qSp_zEd7BIIASdDdxiYVqzsJGY: Timeout during connect (likely firewall problem)

  Domain: www.learnlog.online
  Type:   connection
  Detail: 172.196.18.127: Fetching http://www.learnlog.online/.well-known/acme-challenge/pRZpLAbOx9U7I_GDZXi37wvgnBNLhPh4cyjg6nhzmFw: Timeout during connect (likely firewall problem)

Hint: The Certificate Authority failed to verify the temporary nginx configuration changes made by Certbot. Ensure the listed domains point to this nginx server and that it is accessible from the internet.

Some challenges have failed.
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.
```

From this it showed that Let's Encrypt HTTP-01 Challenge failed. 

Certbot is used as the ACME client to communicate with Let's Encrypt and automate SSL certificate issuance and renewal using the HTTP-01 challenge.

How it works:
- Certbot requests a certificate or renewal from Let's Encrypt.
- Let's Encrypt provides an HTTP-01 challenge token.
- Certbot places a challenge file under: /.well-known/acme-challenge/
- Let's Encrypt accesses that file over HTTP (port 80) to verify domain ownership.
- Once verified, Let's Encrypt issues the certificate.
- Certbot installs or renews the certificate on the server.

First thing I checked was DNS, if the IP of the domain (learnlog.online) did not match the public IP of the VM then that could be the potential issue.

```
dig +short www.learnlog.online
```
The IP in the terminal returned matched the public IP of the VM, so it was not the problem.

I also tried using the curl command to verify if I could make an HTTP request.

```
curl -v http://www.learnlog.online/
```
```
* Host www.learnlog.online:80 was resolved.
* IPv6: (none)
* IPv4: 172.196.18.127
*   Trying 172.196.18.127:80...
* connect to 172.196.18.127 port 80 from 172.23.63.129 port 42372 failed: Connection timed out
* Failed to connect to www.learnlog.online port 80 after 135279 ms: Couldn't connect to server
* Closing connection
curl: (28) Failed to connect to www.learnlog.online port 80 after 135279 ms: Couldn't connect to server
```

Next thing that I checked was the NSG inbound rules as they might not have been configured correctly to allow Let's Encrypt access the challenge file.

```
Name                            Priority  Protocol  Direction  Access  Source  Destination IP  Destination Port
------------------------------  --------  --------  ---------  ------  ------  --------------  ----------------
Allow-Internet-In-To-AppVM      110       TCP       Inbound    Allow   *       172.196.18.127  80
Allow-Internet-In-To-AppVM-443  100       TCP       Inbound    Allow   *       172.196.18.127  443
```

It turned out Azure has a DNAT that converts public IP addresses to private IP addresses. My NSG was configured to allow traffic for the public IP of the VM rather than the private IP. So when the DNAT translates the public IP `172.196.18.127` to the private IP of the VM inside the subnet (IP comes from a packet) the NSG rules do not apply, and it hits the default inbound rule `DenyAllInbound`.

The fix was to use the private IP of the VM for the NSG inbound rules.

```
az network nsg rule update \
  --resource-group rg-journalAPI-prod-newzealandnorth \
  --nsg-name <nsg-name> \
  --name Allow-Internet-In-To-AppVM \
  --destination-address-prefixes '<private-ip>'

az network nsg rule update \
  --resource-group rg-journalAPI-prod-newzealandnorth \
  --nsg-name <nsg-name> \
  --name Allow-Internet-In-To-AppVM-443 \
  --destination-address-prefixes '<private-ip>'
```

After running the command `sudo certbot --nginx -d learnlog.online -d www.learnlog.online`, it was able to successfully install the certificate in the VM.
