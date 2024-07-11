from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import PyPDF2
import docx
import os
import torch
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'


device = torch.device("cpu")

# Loading facebook/bart-large-cnn from hf
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn").to(device)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}

def extract_text_from_file(file_path):
    text = ''
    if file_path.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file_path)
        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text()
            if page_text:
                text += page_text + " "
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + " "
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            text = file.read()
    return text

def chunk_text(text, max_length=1024, overlap=200):
    tokens = tokenizer(text, return_tensors='pt')['input_ids'][0]
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_length - 10, len(tokens))  # edge case
        chunk = tokens[start:end]
        if len(chunk) <= 1024:  # 1024 is the limit for this model
            chunks.append(chunk)
        else:
            print(f"Skipping chunk of length {len(chunk)} as it exceeds the max length.")
        start += max_length - overlap
    return chunks

def summarize_chunks(chunks):
    summaries = []
    for i, chunk in enumerate(chunks):
      #  print(f"Processing chunk {i+1}/{len(chunks)}, length: {len(chunk)}")
        if len(chunk) > 1014:  # Ensure the chunk length is well within the model's limit
        #    print(f"Chunk size {len(chunk)} exceeds maximum length")
            continue
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
       # print(f"Chunk {i+1} text: {chunk_text}")  # Print the entire chunk text for verification
        input_length = len(chunk_text.split())
        if input_length < 3:  # Skip chunks that are too short
        #    print(f"Skipping chunk: '{chunk_text}' is too short")
            continue
        try:
            max_length = min(200, max(100, int(input_length / 2)))  # Increase min_length and max_length
        #    print(f"Input length: {input_length}, max_length set to: {max_length}")
            summary = summarizer(chunk_text, max_length=max_length, min_length=50, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            print(f"Error summarizing chunk {i+1}: {e}")
            print(f"Chunk tokens: {chunk.tolist()}")
    combined_summary = " ".join(summaries)
    try:
        input_length = len(combined_summary.split())
        max_length = min(400, max(100, int(input_length / 2)))  # Increase final summary length
       # print(f"Combined input length: {input_length}, max_length for final summary set to: {max_length}")
        final_summary = summarizer(combined_summary, max_length=max_length, min_length=100, do_sample=False)[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing combined summary: {e}")
        final_summary = combined_summary
    return final_summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
       
        text = extract_text_from_file(file_path)

       # print(f"Total length of extracted text: {len(text)}")
       # print(f"Extracted text: {text}")  # Print the extracted text for verification
        
        # Splitting the text into chunks 
        chunks = chunk_text(text.strip())
       # print(f"Total chunks created: {len(chunks)}")
        summary = summarize_chunks(chunks)
        
        session['summary'] = summary
        
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Invalid file type"})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if user_message:
        chunks = chunk_text(user_message.strip())
        summary = summarize_chunks(chunks)
        return jsonify({"reply": summary})
    return jsonify({"reply": "I didn't understand that. Please try again."})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Perform authentication (placeholder for now)
        if username == 'user' and password == 'pass':
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
