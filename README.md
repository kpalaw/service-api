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

3.
The solution (for Version 1 ) was then deployed to Google Cloud, and a live health-check endpoint 
is available here: http://34.39.107.75:8000/health and api docment here: http://34.39.107.75:8000/docs

4.
Finally, the source code for Version 1 has been published in a public Git repository 
for review: https://github.com/kpalaw/service-api.git
