ConvoForge
ConvoForge is a comprehensive desktop application for collecting, managing, and interacting with conversational AI data. Built with Python and PyQt6, it provides a complete environment for fine-tuning large language models (LLMs) by enabling robust data curation and direct model inference for comparative analysis.

This tool was designed for ML engineers and researchers who need a local, private, and efficient way to build high-quality datasets and test fine-tuned models.

<!-- It's highly recommended to add a screenshot of the app here -->

Features
Tabbed Interface: A clean, multi-tab layout separating data collection, model interaction (chat), and data management.

Structured Data Collection:

Log conversations from various sources with detailed metadata (model name, summary, etc.).

Live preview of conversation history as you add data.

Auto-generate unique conversation IDs.

Live Model Inference:

Load and chat with different models, including base models and your own fine-tuned adapters (e.g., QLoRA).

Automatically saves your chat sessions as new, high-quality training data.

Supports multiline input (Shift+Enter) and renders model responses as markdown.

Data Management:

View high-level statistics about your dataset (conversation count, word count, etc.).

Filter conversations by model.

Safely delete entire conversations with a confirmation dialog.

Efficient & Local:

Uses multithreading for non-blocking model loading and inference.

All data is stored locally in a SQLite database.

Loads models in 4-bit precision to conserve VRAM.

Tech Stack
Backend & UI: Python 3, PyQt6

Machine Learning: PyTorch, Hugging Face transformers, peft, bitsandbytes

Database: SQLite

Setup
Clone the repository:

git clone https://github.com/your-username/ConvoForge.git
cd ConvoForge

Create a Python virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

Hugging Face Login (Required for Gemma):
The base model for this demo (google/gemma-2b-it) is a gated model. You must be logged into your Hugging Face account.

huggingface-cli login

Follow the prompts and paste your access token.

Usage
Launch the application:

python main.py

Collect Data:

Navigate to the "Data Collection" tab.

Select a source model (or type a new one).

Auto-generate an ID and provide a summary.

Paste user/assistant pairs and save.

Chat with a Model:

Navigate to the "Chat" tab.

Select a model to load (e.g., "Base Model").

Click "Load Model" and wait for it to finish.

Create a new chat session by providing a summary and clicking "Create New Chat".

Start chatting! Your conversation will be saved automatically.