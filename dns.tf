# Route53 hosted zone and DNS records for infuseth.ink.
# Replaces the Pulumi AwsRoute53Zone component and all create_*_record functions.
# All resources imported from existing AWS infrastructure — no DNS repropagation.

import {
  to = aws_route53_zone.main
  id = "Z00982262VVBPSLWSIJ10"
}

import {
  to = aws_route53_record.mx
  id = "Z00982262VVBPSLWSIJ10_infuseth.ink_MX"
}

import {
  to = aws_route53_record.spf
  id = "Z00982262VVBPSLWSIJ10_infuseth.ink_TXT"
}

import {
  to = aws_route53_record.dkim
  id = "Z00982262VVBPSLWSIJ10_default._domainkey.infuseth.ink_TXT"
}

import {
  to = aws_route53_record.dmarc
  id = "Z00982262VVBPSLWSIJ10__dmarc.infuseth.ink_TXT"
}

import {
  to = aws_route53_record.backend_a
  id = "Z00982262VVBPSLWSIJ10_backstage.infuseth.ink_A"
}

# ---------------------------------------------------------------------------

resource "aws_route53_zone" "main" {
  name = "infuseth.ink"
}

# MX — Namecheap Private Email (mail routing unchanged)
resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "infuseth.ink"
  type    = "MX"
  ttl     = 300

  records = [
    "10 mx1.privateemail.com",
    "20 mx2.privateemail.com",
  ]
}

# SPF — authorises Namecheap Private Email to send for infuseth.ink
resource "aws_route53_record" "spf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "infuseth.ink"
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
  name    = "default._domainkey.infuseth.ink"
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
  name    = "_dmarc.infuseth.ink"
  type    = "TXT"
  ttl     = 300

  records = [
    "v=DMARC1; p=none;",
  ]
}

# A — backstage.infuseth.ink → staging EC2 instance
# This will update from the old Pulumi-managed IP to the new TF-managed EC2 IP on first apply.
resource "aws_route53_record" "backend_a" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "backstage.infuseth.ink"
  type    = "A"
  ttl     = 300

  records = [aws_instance.backend.public_ip]
}
