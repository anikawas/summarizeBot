# Text Summarizer Chatbot
## Description
***This project is a Flask-based web application that allows users to upload documents (PDF, DOCX, TXT) and receive summarized text. The application also features a chatbot interface where users can interact with the summarizer in a conversational manner.***

## Features
Support for PDF, DOCX, and TXT files.
Chatbot interface for interactive summarization.
User authentication (login/logout).
Summarize uploaded documents and chat inputs.
Exclude virtual environment and unnecessary files from version control.

## Installation
### Prerequisites
Python 3.x
Git

### Setup
1. Clone the Repository:
   
bash
*git clone https://github.com/your-username/text-summarizer-chatbot.git
*cd text-summarizer-chatbot

2. Create and Activate a Virtual Environment:
    
bash
*python -m venv chat
*source chat/bin/activate  # On Windows: chat\Scripts\activate

3. Install Dependencies:

bash
*pip install -r requirements.txt


### File Structure
php
Copy code
project_root/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── login.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/
├── chat/  # Your virtual environment directory (not included in Git)
└── README.md


Go to the GitHub repository and create a pull request for your changes.

## Contributing
Contributions are welcome! Please open an issue or create a pull request with your improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
* Flask
* Hugging Face Transformers
* PyPDF2
* python-docx
