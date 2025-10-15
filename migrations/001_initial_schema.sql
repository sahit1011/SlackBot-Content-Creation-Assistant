-- Initial database schema for Slackbot Content Creation Assistant
-- Run this script in Supabase SQL Editor

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