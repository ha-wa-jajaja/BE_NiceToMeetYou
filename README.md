# OneAI Backend Engineer Recruitment Mini-Project

## Core Requirements

1. Try not using LLM for this test.
2. Scrape the featured news from [https://tw-nba.udn.com/nba/index](https://tw-nba.udn.com/nba/index).
3. Design an appropriate Model using any framework (FastAPI, Django, Gin) and store the scraped news in a DB.
4. Implement the following pages using AJAX:
    - Featured news list
    - News detail page
5. Need to compose the basic implementations in frontend.
6. Deploy this demo to a server and ensure it runs correctly.
7. Create Your own public repository and make multiple pull requests and commits to that repository, and reply back the github public repository link when it's finished.

## Database Management Requirements

1. Implement database migrations using Alembic:
    - Create proper migration scripts for all database changes.
    - Include both upgrade and downgrade paths.
2. Implement proper database indexing strategies for optimal query performance.

## Code Quality Requirements

1. Follow PEP 8 style guide for Python code.
2. Well Doc-String for all major functions and classes.
3. Implement type hints for better code clarity.

## Advanced Requirements (Optional, not required, just a bonus)

1. Use Docker to containerize the application and database, and provide a `docker-compose.yml` file for easy deployment.
2. Implement unit tests for at least 90% coverage rate.
3. Implement automated scheduled scraping.
4. Use a Websocket service to immediately notify the frontend when new news is scraped.
5. The implemented news list API should be able to withstand a 100 QPS load test.

## Submission Requirements

1. Include a comprehensive README.md with:
    - Setup instructions
    - API documentation
    - Testing instructions
    - Migration commands
2. Provide environment configuration examples.
3. Document any assumptions or design decisions made.

This enhanced version includes more specific technical requirements while maintaining the original scope. The additions focus on best practices in software development, particularly around database management, testing, and deployment automation.
