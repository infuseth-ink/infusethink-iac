# Route53 hosted zone and email DNS records for var.domain_name.
# Shared across all environments — one zone, shared email identity.

resource "aws_route53_zone" "main" {
  name = var.domain_name
}

# MX — Namecheap Private Email (mail routing)
resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "MX"
  ttl     = 300

  records = [
    "10 mx1.privateemail.com",
    "20 mx2.privateemail.com",
  ]
}

# SPF — authorises Namecheap Private Email to send for the domain
resource "aws_route53_record" "spf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = 300

  records = [
    "v=spf1 include:spf.privateemail.com ~all",
  ]
}

# DKIM — public key for Namecheap Private Email signing
# Split across two strings because each TXT string is capped at 255 bytes (RFC 4408).
resource "aws_route53_record" "dkim" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "default._domainkey.${var.domain_name}"
  type    = "TXT"
  ttl     = 300

  records = [
    "v=DKIM1;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqHfS1n3GDYIg+/WlerdvooNBs/1XeFtm1nh3cCxFFktUbXoYNkDMTLHITpT8ngk6CZ7s+qHegqPzh6O7i0jKTCMfPrK7FbZBTPXMctzY6FSWe0xGYK+LakLtvXktnZd90SAtKyBnUe62hqB9EXNpvRF2vHQlavCIuLEj2Ci8MeOHLx9jNvZH6CaTEtb/AxxMQPr",
    "wwFOZ5at4ta83RxQNKQtlAPBIfrDt1i/E+yC6yskVK1CC2UEYZINQrFuz3CFPX1Et0ES60gL/H4tLtZ8N3bnfthS3qWPCt79a+lsSCmrIwggjZjA2+oVPMmiOATZCeCZVze33T++xDnJNj3pN+wIDAQAB",
  ]
}

# DMARC — policy record (monitoring only, no enforcement)
resource "aws_route53_record" "dmarc" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "_dmarc.${var.domain_name}"
  type    = "TXT"
  ttl     = 300

  records = [
    "v=DMARC1; p=none;",
  ]
}
