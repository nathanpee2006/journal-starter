11/03/2026

# What did I do?

Applied NSG security rules to each of the subnets in the VNet

# What worked?

Used `nslookup` to verify if resources that used a Private Endpoint such as PostgreSQL and Foundry resolved to private IP addresses

`nc` and IP Flow Verify was used to verify connectivity to resources and to know whether the NSG rules were actually being enforced

# What I struggled with, and how did I solve it?

None.