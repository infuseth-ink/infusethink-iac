aws_region  = "ap-southeast-1"
domain_name = "infuseth.ink"

# Allowlist for shared Postgres (5432). Update via PR when your IP changes.
# Use /32 for a single IP; widen to /24 if your ISP rotates the last octet.
db_allowed_cidrs = [
  "156.236.93.0/24", # mike — home/ISP /24
]
