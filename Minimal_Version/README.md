# Minimal Version - Multi-Agent Social Media Post Generator

A simplified version of the multi-agent social media content generation system using Flask, vanilla JavaScript, and SQLite.

## Features

- **Brand Configuration**: Define brand tone, audience, guidelines
- **Trend Analysis**: LLM-powered trend identification
- **Multi-Agent Debate**: 6 specialized agents analyze and debate content
- **Post Generation**: Generate 1-3 post variations with titles, content, hashtags, and image prompts
- **Dark Theme UI**: Clean, modern interface

## Project Structure

```
Minimal_Version/
├── database/
│   ├── __init__.py
│   ├── database.py           # SQLite database manager
│   └── minimal_version.db    # SQLite database file
├── agents/
│   ├── __init__.py
│   ├── trend_agent.py        # Trend analysis agent
│   ├── brand_agent.py        # Brand consistency agent
│   ├── compliance_agent.py   # Compliance checking agent
│   ├── risk_agent.py         # Risk assessment agent
│   ├── engagement_agent.py   # Engagement optimization agent
│   └── cmo_agent.py          # Chief Marketing Officer (arbitrator)
├── utils/
│   ├── __init__.py
│   ├── llm_client.py         # Groq LLM client
│   ├── debate_orchestrator.py # Debate management
│   └── post_generator.py     # Post generation logic
├── static/
│   ├── css/
│   │   └── output.css        # TailwindCSS compiled output
│   └── js/
│       └── scripts.js        # Frontend JavaScript
├── templates/
│   ├── index.html            # Brand configuration page
│   ├── create-post.html      # Post input page
│   ├── debate.html           # Agent debate viewer
│   └── results.html          # Generated posts viewer
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Edit `.env` file with your Groq API key

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Application**:
   - Open browser at `http://localhost:5000`

## Workflow

1. **Brand Setup**: Configure brand details on the homepage
2. **Create Post**: Fill in post requirements and objectives
3. **Debate Process**: Watch agents analyze and debate the content
4. **View Results**: See 1-3 generated post variations

## Agents

- **TrendAgent**: Identifies viral opportunities
- **BrandAgent**: Ensures brand consistency
- **ComplianceAgent**: Checks legal and platform compliance
- **RiskAgent**: Assesses reputation risks
- **EngagementAgent**: Optimizes for audience interaction
- **CMOAgent**: Makes final decisions and arbitrates conflicts

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **LLM**: Groq API (Llama 3.3 70B)
- **Frontend**: HTML + TailwindCSS + Vanilla JS
- **Theme**: Dark Mode
