AVAILABLE_MODELS = [
    "tinyllama:1.1b",
    "phi3:mini",
    "mistral:7b-instruct-q4_0"
]

OUTPUT_TYPES = ["summary", "reasoning", "code"]

SYSTEM_PROMPTS = {
    "summary": """You are a summarization assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "summary": "one paragraph summary here",
  "key_points": ["point 1", "point 2", "point 3"],
  "word_count": 42
}""",

    "reasoning": """You are a reasoning assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "answer": "final answer here",
  "reasoning_steps": ["step 1", "step 2", "step 3"],
  "confidence": "high"
}
confidence must be exactly one of: high, medium, low""",

    "code": """You are a coding assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "code": "def your_function():\\n    pass",
  "language": "python",
  "explanation": "brief explanation here"
}"""
}

RETRY_SYSTEM_PROMPTS = {
    "summary": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "summary": "your summary here",
  "key_points": ["point 1", "point 2"],
  "word_count": 10
}""",

    "reasoning": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "answer": "your answer here",
  "reasoning_steps": ["step 1", "step 2"],
  "confidence": "high"
}
confidence must be exactly one of: high, medium, low""",

    "code": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "code": "your code here",
  "language": "python",
  "explanation": "your explanation here"
}"""
}

TEMPERATURE_PROMPTS = [
    {
        "id": "temp_1",
        "prompt": "Write a one sentence tagline for a coffee shop."
    },
    {
        "id": "temp_2",
        "prompt": "Explain what gravity is in one sentence."
    },
    {
        "id": "temp_3",
        "prompt": "Write a one sentence description of the color blue."
    },
    {
        "id": "temp_4",
        "prompt": "What is the capital of France? Answer in one sentence."
    },
    {
        "id": "temp_5",
        "prompt": "Write a one sentence motivational quote."
    }
]

TEMPERATURES = [0.0, 0.7]
RUNS_PER_TEMP = 3


MEMORY_MEASUREMENT_PROMPTS = [
    "Explain what artificial intelligence is in 3 sentences.",
    "Write a Python function that sorts a list of numbers.",
    "Summarize the pros and cons of electric vehicles in 4 bullet points."
]
PROMPTS = [
    # --- Healthcare & Medical (5 prompts) ---
    {
        "id": "health_1",
        "category": "healthcare",
        "prompt": "A patient reports chest pain, shortness of breath, and sweating. List the possible conditions this could indicate and what immediate steps should be taken."
    },
    {
        "id": "health_2",
        "category": "healthcare",
        "prompt": "Explain the difference between Type 1 and Type 2 diabetes in simple terms a patient could understand."
    },
    {
        "id": "health_3",
        "category": "healthcare",
        "prompt": "A 45-year-old patient has a BMI of 32, high blood pressure, and high cholesterol. Summarize their risk factors and suggest lifestyle changes."
    },
    {
        "id": "health_4",
        "category": "healthcare",
        "prompt": "Explain what an MRI scan is, when it is used, and how it differs from a CT scan in 3 sentences."
    },
    {
        "id": "health_5",
        "category": "healthcare",
        "prompt": "What are the early warning signs of a stroke and what should a bystander do immediately?"
    },

    # --- Legal & Compliance (5 prompts) ---
    {
        "id": "legal_1",
        "category": "legal",
        "prompt": "Summarize what GDPR is and what obligations it places on companies that handle personal data."
    },
    {
        "id": "legal_2",
        "category": "legal",
        "prompt": "Explain the difference between a non-disclosure agreement and a non-compete agreement in simple terms."
    },
    {
        "id": "legal_3",
        "category": "legal",
        "prompt": "A software company wants to use an open source library licensed under GPL in their commercial product. What are the legal implications?"
    },
    {
        "id": "legal_4",
        "category": "legal",
        "prompt": "What is intellectual property? Explain the 4 main types: copyright, trademark, patent, and trade secret in 2 sentences each."
    },
    {
        "id": "legal_5",
        "category": "legal",
        "prompt": "What is the difference between civil law and criminal law? Give one example of each."
    },

    # --- Finance & Banking (5 prompts) ---
    {
        "id": "finance_1",
        "category": "finance",
        "prompt": "Explain what compound interest is and why it matters for long-term savings. Give a simple example."
    },
    {
        "id": "finance_2",
        "category": "finance",
        "prompt": "A company has revenue of $500,000, cost of goods sold of $200,000, and operating expenses of $150,000. What is the gross profit and operating profit?"
    },
    {
        "id": "finance_3",
        "category": "finance",
        "prompt": "Explain the difference between a stock and a bond in simple terms a beginner investor could understand."
    },
    {
        "id": "finance_4",
        "category": "finance",
        "prompt": "What is a credit score, what factors affect it, and why does it matter when applying for a loan?"
    },
    {
        "id": "finance_5",
        "category": "finance",
        "prompt": "What is the difference between a bull market and a bear market? How should an investor behave during each?"
    },

    # --- Code & Engineering (5 prompts) ---
    {
        "id": "code_1",
        "category": "code",
        "prompt": "Write a Python function that takes a list of numbers and returns the average. Handle the case where the list is empty."
    },
    {
        "id": "code_2",
        "category": "code",
        "prompt": "Write a Python function that checks if a string is a palindrome. Ignore spaces and capitalization."
    },
    {
        "id": "code_3",
        "category": "code",
        "prompt": "Write a Python class that represents a bank account with methods for deposit, withdrawal, and checking balance. Prevent negative balances."
    },
    {
        "id": "code_4",
        "category": "code",
        "prompt": "Write a Python function that takes a list of dictionaries representing employees with name and salary fields, and returns the top 3 highest paid employees."
    },
    {
        "id": "code_5",
        "category": "code",
        "prompt": "Write a Python function that reads a CSV file and returns the data as a list of dictionaries. Handle the case where the file does not exist."
    },

    # --- Education & Tutoring (5 prompts) ---
    {
        "id": "edu_1",
        "category": "education",
        "prompt": "Explain the Pythagorean theorem to a 12-year-old student. Use a real-world example to illustrate it."
    },
    {
        "id": "edu_2",
        "category": "education",
        "prompt": "A student is struggling to understand the difference between mitosis and meiosis. Explain both processes clearly and highlight the key differences."
    },
    {
        "id": "edu_3",
        "category": "education",
        "prompt": "Explain why the sky is blue in terms simple enough for a 10-year-old to understand."
    },
    {
        "id": "edu_4",
        "category": "education",
        "prompt": "A student asks: why do we need to learn algebra if we have calculators? Give a thoughtful and convincing answer."
    },
    {
        "id": "edu_5",
        "category": "education",
        "prompt": "Explain the causes of World War 1 in simple terms suitable for a high school student."
    },

    # --- Marketing & Content (5 prompts) ---
    {
        "id": "marketing_1",
        "category": "marketing",
        "prompt": "Write a compelling 3-sentence product description for a premium wireless noise-cancelling headphone targeted at remote workers."
    },
    {
        "id": "marketing_2",
        "category": "marketing",
        "prompt": "A coffee shop is launching a new seasonal pumpkin spice latte. Write a short Instagram caption with relevant hashtags."
    },
    {
        "id": "marketing_3",
        "category": "marketing",
        "prompt": "Explain the difference between B2B and B2C marketing strategies in 3 bullet points."
    },
    {
        "id": "marketing_4",
        "category": "marketing",
        "prompt": "Write a cold email subject line and opening paragraph for a SaaS product that helps small businesses manage their invoices."
    },
    {
        "id": "marketing_5",
        "category": "marketing",
        "prompt": "What are the key elements of a strong brand identity? List and briefly explain 5 elements."
    },

    # --- HR & Recruiting (5 prompts) ---
    {
        "id": "hr_1",
        "category": "hr",
        "prompt": "Write a job description for a mid-level Python backend engineer at a fintech startup. Include responsibilities and required skills."
    },
    {
        "id": "hr_2",
        "category": "hr",
        "prompt": "A manager needs to give difficult feedback to an employee who is technically strong but consistently misses deadlines. Write a script for that conversation."
    },
    {
        "id": "hr_3",
        "category": "hr",
        "prompt": "What are the 5 most important questions to ask a candidate during a software engineering interview? Explain why each question matters."
    },
    {
        "id": "hr_4",
        "category": "hr",
        "prompt": "An employee has submitted a resignation letter. Write a professional response from HR acknowledging the resignation and outlining the offboarding process."
    },
    {
        "id": "hr_5",
        "category": "hr",
        "prompt": "What is unconscious bias in hiring and what are 3 practical steps a company can take to reduce it?"
    },

    # --- Customer Support (5 prompts) ---
    {
        "id": "support_1",
        "category": "customer_support",
        "prompt": "A customer is angry because their order arrived 2 weeks late and some items were damaged. Write a professional and empathetic response on behalf of the company."
    },
    {
        "id": "support_2",
        "category": "customer_support",
        "prompt": "A customer asks: what is your refund policy for digital products? Write a clear and friendly explanation assuming a standard 30-day no-questions-asked policy."
    },
    {
        "id": "support_3",
        "category": "customer_support",
        "prompt": "Classify the following customer message as: billing issue, technical problem, or general inquiry. Message: 'I was charged twice for my subscription this month and I need it fixed immediately.'"
    },
    {
        "id": "support_4",
        "category": "customer_support",
        "prompt": "A customer wants to cancel their subscription. Write a retention response that acknowledges their request, asks for a reason, and offers an alternative solution."
    },
    {
        "id": "support_5",
        "category": "customer_support",
        "prompt": "A customer reports that the mobile app keeps crashing when they try to upload a photo. Write a step-by-step troubleshooting response."
    }
]