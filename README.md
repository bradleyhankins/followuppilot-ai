# FollowUpPilot AI

FollowUpPilot AI is a sales follow-up workflow assistant for field-sales and home-service teams. It turns customer context into next-best actions, priority scoring, lead temperature, deal risk, text messages, emails, voicemail scripts, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch follow-up sequences.

## Live Demo

[Launch FollowUpPilot AI](https://followuppilot-ai.streamlit.app/)

## Why this project exists

Small and mid-sized businesses often lose revenue because follow-up is inconsistent, CRM notes are incomplete, and reps do not always know the best next step after a customer interaction.

FollowUpPilot AI helps standardize the follow-up process and gives teams a faster way to create clear, professional, context-aware communication and documentation.

## Who this helps

FollowUpPilot AI is designed for:

- Home-service companies
- Field-sales teams
- Sales representatives
- Sales managers
- Small business owners
- Revenue operations teams
- Teams that need stronger CRM discipline and follow-up consistency

## Current Version: v2.3

FollowUpPilot AI v2.3 includes:

- Portfolio Hub-style executive design
- Public-safe fictional sample scenarios
- Sample scenario loader
- Lead status workflow
- Priority scoring
- Lead temperature
- Deal risk scoring
- Main risk diagnosis
- Next best action recommendation
- Why-this-recommendation explanation
- Days since last contact input
- Follow-up intensity selector
- Communication channel selector
- Expanded tone selector
- Copy Center for text, email, voicemail, CRM note, and coaching note
- Follow-up timeline
- Customer text message generator
- Customer email generator
- Voicemail script generator
- CRM-ready note generator
- Call script generator
- Objection guidance
- Manager coaching note
- Downloadable Markdown follow-up plan
- Privacy note

## What it analyzes

The workflow considers:

- Customer/project context
- Project type
- Lead status
- Main concern or objection
- Urgency level
- Financing discussion status
- Preferred communication tone
- Days since last contact
- Follow-up intensity
- Preferred communication channel
- Sales follow-up timing
- Manager coaching priority

## Workflow Outputs

The app generates:

- Follow-up priority level
- Priority score
- Lead temperature
- Deal risk
- Main risk
- Recommended follow-up timing
- Next best action
- Explanation of the recommendation
- Copy-ready text message
- Copy-ready email
- Voicemail script
- CRM note
- Call script
- Objection-handling guidance
- Manager coaching note
- Suggested follow-up sequence
- Downloadable Markdown follow-up plan

## Suggested Test Flow

1. Launch the live demo.
2. Load the “Price Objection” sample scenario.
3. Generate the follow-up plan.
4. Review the follow-up priority, lead temperature, deal risk, and next best action.
5. Review the Copy Center and follow-up timeline.
6. Review the objection guidance, manager coaching note, and follow-up sequence.
7. Download the follow-up plan.

## Screenshots

### Recommendation, Copy Center, and Timeline

![FollowUpPilot AI Copy Center and Timeline](screenshots/copy-center-timeline.svg)

## Tech Stack

- Python
- Streamlit
- Rules-based AI-style workflow logic
- Markdown report export
- GitHub
- Streamlit Community Cloud

## Run Locally

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Public Demo Note

All sample data, names, companies, and scenarios used in this project are fictional and created for public portfolio demonstration purposes.

## Portfolio Purpose

This project was built as part of Bradley Hankins' AI operations and workflow automation portfolio.

FollowUpPilot AI demonstrates how practical AI-assisted tools can help small and mid-sized businesses improve sales follow-up consistency, CRM discipline, customer communication, objection handling, manager coaching, and revenue operations workflows.

## Case Study

### Problem

Field-sales and home-service teams often lose opportunities because follow-up is inconsistent, CRM notes are incomplete, and sales representatives do not always have a clear next step after a customer interaction.

Common issues include:

- Slow follow-up after estimates or proposals
- Inconsistent text and email quality
- Weak CRM documentation
- Missed objection-handling opportunities
- Lack of manager visibility into next-step discipline
- Reps relying on memory instead of a repeatable process

### Solution

FollowUpPilot AI was built as a lightweight AI-assisted workflow tool that helps sales representatives and managers create stronger follow-up communication and cleaner CRM documentation.

The app allows users to load a fictional sample scenario or enter their own customer context. It then generates a complete follow-up workflow, including next best action, lead temperature, deal risk, messaging, voicemail, CRM notes, call scripts, manager coaching notes, and a downloadable plan.

### My Role

I designed and built this project from concept to deployment, including:

- Defining the business workflow problem
- Mapping the sales follow-up process
- Designing the input structure
- Building the Streamlit app
- Writing the rules-based AI-style generation logic
- Creating next-best-action recommendations
- Creating downloadable Markdown reports
- Preparing fictional sample scenarios for public portfolio use
- Publishing the project on GitHub
- Deploying the live demo

### Business Value

FollowUpPilot AI helps small and mid-sized businesses improve sales execution by creating a more consistent follow-up process.

The tool can help teams:

- Respond faster after customer interactions
- Improve text and email quality
- Standardize CRM notes
- Add voicemail scripts to the follow-up workflow
- Coach reps on objections
- Reduce missed follow-up opportunities
- Create a repeatable customer communication workflow
- Turn sales context into action-ready communication

### Future Improvements

Planned future improvements include:

- OpenAI API integration for dynamic message generation
- CRM export templates
- Follow-up sequence scheduling
- Saved customer profiles
- Team-level follow-up reporting
- Rep performance tracking
- Integration with lead status CSV uploads
- PDF follow-up plan downloads

## Built By

Bradley Hankins  
Operations & Revenue Leader | AI Workflow Automation | RevOps & Process Improvement
