## EPIC-001: Project Setup & Infrastructure
**Priority:** P0 (Blocker)  
**Story Points:** 8  
**Duration:** 1 Day  
**Owner:** Developer  

### Tasks:

#### SLACK-001: Create All Service Accounts ⭐ START HERE
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 1 hour  

**Description:**
Set up all required external service accounts and obtain API credentials.

**Acceptance Criteria:**
- [ ] Slack workspace created
- [ ] Slack app created at api.slack.com/apps
- [ ] Bot token and signing secret obtained
- [ ] Supabase project created
- [ ] Upstash Redis database created
- [ ] Brave Search API key obtained (or SerpAPI)
- [ ] Groq API key obtained
- [ ] SendGrid account created and sender verified

**Deliverables:**
- Document with all credentials (store securely)
- Screenshot of each service dashboard

**Dependencies:** None

**Subtasks:**
- [ ] Create Slack app with Bot Token Scopes: `chat:write`, `files:write`, `files:read`, `commands`
- [ ] Enable Socket Mode or Events API
- [ ] Create slash commands: `/process_keywords`, `/history`, `/regenerate`
- [ ] Create Supabase project and get URL + anon key
- [ ] Create Upstash Redis database and get REST URL
- [ ] Sign up for Brave Search API (2000 free queries/month)
- [ ] Create Groq account and get API key
- [ ] Create SendGrid account, verify sender email

**Testing:**
- Verify each API key works with a test request

---

#### SLACK-002: Initialize Project Structure
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 30 minutes  

**Description:**
Create the project directory structure and initialize version control.

**Acceptance Criteria:**
- [ ] Git repository initialized
- [ ] Project structure created
- [ ] Virtual environment set up
- [ ] .gitignore configured

**Deliverables:**
- Working project structure
- Initial Git commit

**Dependencies:** None

**Implementation Steps:**
```bash
# Create project
mkdir slackbot-content-assistant
cd slackbot-content-assistant
git init

# Create structure
mkdir -p app/{handlers,services,utils,models}
touch app/__init__.py
touch app/main.py
touch app/config.py
touch requirements.txt
touch Dockerfile
touch .env
touch .env.example
touch README.md
touch .gitignore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Create .gitignore
echo "venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.log
*.pdf
.DS_Store" > .gitignore
```

**Testing:**
- Verify directory structure is correct
- Ensure virtual environment activates

---

#### SLACK-003: Configure Environment Variables
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 1  
**Estimated Time:** 20 minutes  

**Description:**
Create configuration management for all API keys and settings.

**Acceptance Criteria:**
- [ ] .env.example file created with all variables
- [ ] config.py loads environment variables
- [ ] Sensitive data not committed to Git

**Deliverables:**
- `app/config.py` with Config class
- `.env.example` template

**Dependencies:** SLACK-001, SLACK-002

**Code Template:**
```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
    
    # Database
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL')
    
    # APIs
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    
    # Application
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_KEYWORDS = int(os.getenv('MAX_KEYWORDS', '1000'))
```

**Testing:**
- Import config and verify variables load
- Test with missing .env file (should not crash)

---

#### SLACK-004: Set Up Database Schema
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 45 minutes  

**Description:**
Create all database tables in Supabase.

**Acceptance Criteria:**
- [ ] All 4 tables created (users, keyword_batches, keyword_clusters, reports)
- [ ] Indexes created
- [ ] Foreign key relationships established
- [ ] Test data inserted successfully

**Deliverables:**
- SQL migration file
- Database connection test script

**Dependencies:** SLACK-001, SLACK-003

**SQL Script:**
```sql
-- Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slack_user_id VARCHAR(50) UNIQUE NOT NULL,
  slack_team_id VARCHAR(50),
  email VARCHAR(255),
  display_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_active_at TIMESTAMP DEFAULT NOW()
);

-- Create keyword_batches table
CREATE TABLE keyword_batches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  batch_name VARCHAR(255),
  status VARCHAR(50) NOT NULL,
  raw_keywords TEXT[],
  cleaned_keywords TEXT[],
  keyword_count INT,
  cluster_count INT,
  source_type VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  error_message TEXT
);

CREATE INDEX idx_batches_user ON keyword_batches(user_id);
CREATE INDEX idx_batches_status ON keyword_batches(status);

-- Create keyword_clusters table
CREATE TABLE keyword_clusters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
  cluster_number INT NOT NULL,
  cluster_name VARCHAR(255) NOT NULL,
  keywords TEXT[] NOT NULL,
  keyword_count INT,
  post_idea TEXT,
  post_idea_metadata JSONB,
  outline_json JSONB,
  top_urls TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clusters_batch ON keyword_clusters(batch_id);

-- Create reports table
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  batch_id UUID REFERENCES keyword_batches(id) ON DELETE CASCADE,
  pdf_filename VARCHAR(255),
  pdf_url TEXT,
  file_size_kb INT,
  sent_via_email BOOLEAN DEFAULT FALSE,
  email_sent_to VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_batch ON reports(batch_id);
```

**Testing:**
- Run SQL in Supabase SQL editor
- Test insert/select on each table
- Verify foreign keys work

---

#### SLACK-005: Install Dependencies
**Type:** Setup  
**Priority:** Critical  
**Story Points:** 1  
**Estimated Time:** 15 minutes  

**Description:**
Install all required Python packages.

**Acceptance Criteria:**
- [ ] requirements.txt created with all dependencies
- [ ] All packages install without errors
- [ ] Version conflicts resolved

**Deliverables:**
- Complete requirements.txt file

**Dependencies:** SLACK-002

**Requirements File:**
```txt
# requirements.txt
slack-bolt==1.18.0
slack-sdk==3.23.0
python-dotenv==1.0.0

# Database & Cache
supabase==2.0.3
redis==5.0.1

# ML & Data Processing
sentence-transformers==2.2.2
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.0

# Web Scraping & Search
requests==2.31.0
beautifulsoup4==4.12.2

# LLM
groq==0.4.1

# PDF Generation
reportlab==4.0.7

# Email
sendgrid==6.11.0

# Utilities
python-slugify==8.0.1
```

**Installation:**
```bash
pip install -r requirements.txt
```

**Testing:**
- Import each major library in Python REPL
- No import errors
