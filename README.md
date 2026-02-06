Summary of the Technical Exercise

Based on the requirements provided in the interview preparation email, 
I implemented a working demonstration that showcases both a minimal solution 
and an extended design.

1.
First, I developed two API implementations:
Version 1 (Minimal Design)
Uses a single database table to store service requests containing a work description 
and customer details.
Runs on port 8000 and directly satisfies the core requirement.

Version 2 (Extended Design)
Uses a normalized schema with 3 related tables to demonstrate scalable system design 
and data integrity.
Runs on port 8001 to allow comparison with the minimal implementation.

2.
Both versions were packaged using Docker containerization, 
forming a deployment composed of three containers to ensure reproducibility 
and environment isolation.

3. Deployment
Both Version 1 and Version 2 of the solution have been deployed to Google Cloud.
- Version 1 is running on port 8000, with a live health-check endpoint 
and API documentation available at:
Health check: http://34.39.107.75:8000/health
API documentation (Swagger): http://34.39.107.75:8000/docs

- Version 2 is running on port 8001 within the same cloud environment.

4.
Finally, the source code for Version 1 and 2 have been published in a public Git repository 
for review: https://github.com/kpalaw/service-api.git
