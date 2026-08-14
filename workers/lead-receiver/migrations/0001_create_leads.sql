CREATE TABLE IF NOT EXISTS leads (
  lead_id TEXT PRIMARY KEY,
  received_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL DEFAULT '',
  product TEXT NOT NULL,
  quantity TEXT NOT NULL DEFAULT '',
  market TEXT NOT NULL DEFAULT '',
  timeline TEXT NOT NULL DEFAULT '',
  message TEXT NOT NULL,
  source_page TEXT NOT NULL DEFAULT '',
  landing_page TEXT NOT NULL DEFAULT '',
  referrer TEXT NOT NULL DEFAULT '',
  traffic_channel TEXT NOT NULL DEFAULT '',
  traffic_source TEXT NOT NULL DEFAULT '',
  campaign_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'closed', 'deleted'))
);

CREATE INDEX IF NOT EXISTS leads_received_at_idx ON leads(received_at DESC);
CREATE INDEX IF NOT EXISTS leads_status_received_at_idx ON leads(status, received_at DESC);
CREATE INDEX IF NOT EXISTS leads_email_idx ON leads(email);
CREATE INDEX IF NOT EXISTS leads_retention_until_idx ON leads(retention_until);

CREATE TABLE IF NOT EXISTS lead_rate_limits (
  bucket_key TEXT NOT NULL,
  bucket_start INTEGER NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (bucket_key, bucket_start)
);

CREATE INDEX IF NOT EXISTS lead_rate_limits_bucket_start_idx ON lead_rate_limits(bucket_start);
