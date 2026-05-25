PROJECT_TYPES = ["Roof Replacement", "Roof Repair", "Siding", "Gutters", "Windows", "HVAC", "Pest Control", "General Home Service", "Other"]
LEAD_STATUSES = ["New Lead", "Inspection Scheduled", "Inspection Completed", "Estimate Presented", "Proposal Sent", "Needs Follow-Up", "Verbal Yes / Pending Signature", "Closed Lost"]
OBJECTIONS = ["None", "Price", "Need to Think About It", "Getting Other Quotes", "Spouse / Decision Maker", "Timing", "Financing", "Other"]
TONES = ["Friendly", "Professional", "Urgent", "Direct", "Consultative", "Reassuring", "High-Confidence", "No-Pressure"]
URGENCY_LEVELS = ["Low", "Medium", "High"]
FINANCING_OPTIONS = ["No", "Yes"]
FOLLOWUP_INTENSITIES = ["Light Touch", "Standard", "Persistent", "Last Attempt"]
CHANNEL_OPTIONS = ["All", "Text", "Email", "Phone Call", "Voicemail", "CRM Note"]

SAMPLE_SCENARIOS = {
    "Blank / Custom": {},
    "Price Objection": {
        "customer": "Avery Johnson",
        "company": "Summit Home Services",
        "project_type": "Roof Replacement",
        "lead_status": "Estimate Presented",
        "context": "Customer liked the project plan but said the price was higher than expected and wanted to review options before making a decision.",
        "objection": "Price",
        "financing": "Yes",
        "urgency": "High",
        "tone": "Consultative",
        "days_since": 1,
        "intensity": "Standard",
        "channel": "All",
    },
    "Needs Spouse Approval": {
        "customer": "Morgan Ellis",
        "company": "Summit Home Services",
        "project_type": "Siding",
        "lead_status": "Proposal Sent",
        "context": "Customer liked the siding option but said they needed to review the color, budget, and timeline with their spouse before moving forward.",
        "objection": "Spouse / Decision Maker",
        "financing": "No",
        "urgency": "Medium",
        "tone": "Reassuring",
        "days_since": 2,
        "intensity": "Standard",
        "channel": "All",
    },
    "Proposal Sent / No Response": {
        "customer": "Jordan Miller",
        "company": "Summit Home Services",
        "project_type": "Gutters",
        "lead_status": "Proposal Sent",
        "context": "Proposal was sent four days ago. Customer has not responded yet. The project was originally described as important before the next heavy rain.",
        "objection": "Timing",
        "financing": "No",
        "urgency": "Medium",
        "tone": "Direct",
        "days_since": 4,
        "intensity": "Persistent",
        "channel": "All",
    },
    "Financing Concern": {
        "customer": "Taylor Brooks",
        "company": "Summit Home Services",
        "project_type": "Windows",
        "lead_status": "Estimate Presented",
        "context": "Customer wants the project completed but was unsure about monthly payment options and total project cost.",
        "objection": "Financing",
        "financing": "Yes",
        "urgency": "Medium",
        "tone": "No-Pressure",
        "days_since": 1,
        "intensity": "Light Touch",
        "channel": "All",
    },
}
