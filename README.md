# edgecenter-dns_exporter

Docker image to export metrics from [EdgeCenter DNS](https://edgecenter.ru/dns) to prometheus

**Parameters**

- port : http port (default : 9886)
- interval : interval between collect in seconds (default: 300)
- edgecenter_dns_api_key : EdgeCenter DNS application key


**docker compose sample**

```yml
version: "2.1"

services:

  edgecenter-dns_exporter:
    image: hroost/edgecenter-dns_exporter:latest
    container_name: edgecenter-dns_exporter
    ports:
      - "9886:9886"
    environment:
      - EDGECENTER_DNS_API_KEY=xxxxxxxxxxx
```

## How to Use:

1. Generate EdgeCenter API token https://accounts.edgecenter.ru/profile/api-tokens

You'll want to grant an 'Engineers' role for API Token.

Further documentation on the DNS API endpoint can be found here: https://apidocs.edgecenter.ru/dns

2. Use the generated key and configure it in docker-compose.yml
3. docker-compose up
