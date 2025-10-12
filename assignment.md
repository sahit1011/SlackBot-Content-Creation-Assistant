# Slackbot Content Creation Assistant - Assignment Requirements

## Objective

Build a Slackbot that helps a content team streamline keyword-based content creation. The bot should allow users to upload raw keyword lists, automatically segment them into groups, generate outlines by analyzing top-ranking web content, suggest post ideas and finally generate a detailed report of the complete results.

---

## Features

### 1. Input & Keyword Management
- Accept input as:
  - File upload (CSV containing keywords)
  - Direct keyword list pasted in Slack
- Clean, deduplicate, and normalize keywords
- Segment keywords into logical groups (semantic similarity)

### 2. Outline Creation
- Fetch/search top-ranking web content for each keyword group
- Extract headings/meta info
- Generate a structured outline (intro, sections, conclusion)

### 3. Post Idea Generation
- For each keyword group, generate a single post idea
- Can use a rule-based approach or LLM integration
- Use only free to use LLM APIs or ones with free trials

### 4. Real-Time Slack Integration
- Display results inside Slack in a clean, formatted message
- Notify users when processing is complete

### 5. Report Generation
- After a full cycle (input → segmentation → outline → ideas), generate a detailed report containing:
  - Uploaded keywords (raw + cleaned)
  - Grouped clusters
  - Suggested post ideas
  - Generated outlines
- Provide report as a downloadable PDF
- (Optional but encouraged) Mail the PDF to the user via SendGrid

### 6. (Bonus) Extra Features
- Allow users to refine/re-generate outlines with a Slack command
- Store results in Notion or Google Sheets
- Provide a `/history` command to view past processed keyword batches

---

## Tech Stack

### Backend Language
- JavaScript / Python (may use another industrially used language)

### Slack Integration
- Slack SDK

### Database
- Supabase (PostgreSQL)

### Vector Search (for semantic grouping)
- Pinecone / OpenAI Embeddings / pgvector (Supabase extension) or any free alternative

### Cache / Shared State
- Upstash Redis

### Email (for report delivery)
- SendGrid

### Report Generation
- ReportLab / Puppeteer (PDF export)

### Deployment
- Render.com

---

## Core Features (MVP)

1. **Keyword Upload + Parsing** (CSV/text → cleaned list)
2. **Keyword Segmentation** (grouping into clusters)
3. **Outline Suggestion** (top-ranking web results)
4. **Post Ideas** (at least one per cluster)
5. **Slack Output** (formatted message)
6. **Report Generation**
   - Generate a comprehensive PDF report
   - Make it downloadable inside Slack
   - Optionally email it to the user

---

## Evaluation Criteria

### Deployment
- Bundle backend + dependencies into a single Dockerfile (no docker-compose)
- Deploy on Render.com

### Slack Functionality
- Proper Slack app integration with slash commands and message handling

### Keyword Handling
- Efficient parsing, cleaning, and grouping logic

### Post Ideas & Outlines
- Relevant and logically structured suggestions

### Report Generation
- Comprehensive PDF report with all the result details
- Correct formatting and availability for download
- Bonus if emailed automatically to user

### UI/UX inside Slack
- Clear, readable, and neatly formatted messages

### Bonus Points
- Storage of results (Notion/Google Sheets)
- Regeneration commands
- GitHub Actions CI/CD integration

---

## Resources (Free Tiers Only)

- **Redis:** Upstash
- **Database:** Supabase (Postgres with pgvector if needed)
- **Deployment:** Render.com (Docker-based deployment)
- **Web Search API:** SerpAPI free tier / Brave Search API free tier
- **Vector Store (optional):** Pinecone free tier or pgvector on Supabase
- **Email API (for report delivery):** SendGrid
- **PDF Generation:** ReportLab (Python) / Puppeteer (Node.js)
- **Cron Jobs (keep alive):** cron-job.org

---

## Deliverables

1. A link to the hosted Slackbot (deployed and accessible)
2. GitHub public repo URL containing all code, Dockerfile, and instructions
3. A detailed 2 page documentation of the project (AI check would be done on the documentation)
4. PDF Resume

---

## Project Timeline

**Recommended Timeline: 10 days**

- Days 1-2: Setup, architecture, and environment configuration
- Days 3-5: Core feature development (keyword processing, clustering, outline generation)
- Day 6: Integration and pipeline orchestration
- Day 7: Dockerization and deployment
- Day 8: Bonus features implementation
- Days 9-10: Testing, documentation, and polish

---

## Key Success Criteria

✅ Slackbot responds to commands correctly  
✅ Keyword processing is accurate and handles edge cases  
✅ Clustering produces logical, semantically similar groups  
✅ Outlines are well-structured and relevant  
✅ PDF report is comprehensive and professionally formatted  
✅ Docker deployment works on Render.com  
✅ All features work end-to-end without errors  
✅ Documentation is clear and human-written (not AI-generated)

---

## Notes

- Use only **free tier APIs** for all services
- Focus on **core MVP features** first, then add bonuses
- Ensure **error handling** is robust throughout
- Test with **small datasets** first (5-10 keywords) before scaling
- **Document as you code** - don't leave it for the end
- Keep Slack messages **clean and user-friendly**

---

## Support Resources

- Slack API Documentation: https://api.slack.com/
- Supabase Docs: https://supabase.com/docs
- Upstash Redis Docs: https://upstash.com/docs
- Render Deployment Guide: https://render.com/docs
- SerpAPI Docs: https://serpapi.com/
- SendGrid API Docs: https://docs.sendgrid.com/

---

**Assignment Version:** 1.0  
**Last Updated:** October 2025