# ConvoForge

ConvoForge is a comprehensive desktop application for collecting, managing, and interacting with conversational AI data. Built with Python and PyQt6, it provides a complete local environment for fine-tuning large language models (LLMs) by enabling robust data curation and direct model inference for comparative analysis.

This tool was designed for ML engineers and researchers who need a private, efficient, and powerful way to build high-quality datasets and test fine-tuned models on their own hardware.

## Key Features

### Chat & Inference
Load and interact with both base models and your own fine-tuned adapters. All chat sessions are automatically saved as new training data, creating a virtuous cycle of improvement.

![Chat Tab Screenshot](https://github.com/jnlentz/ConvoForge/blob/main/assets/chat_tab.jpg?raw=true)

### Data Collection
Log conversations from various sources with detailed metadata. Features a live preview pane to see the conversation history as you add new turns.

![Data Collection Tab Screenshot](https://github.com/jnlentz/ConvoForge/blob/main/assets/convo_tab.jpg?raw=true)

### Data Management
Filter your entire dataset by the source model and safely delete entire conversations with a confirmation dialog. A preview pane allows you to review a conversation before deleting it.

![Data Management Tab Screenshot](https://github.com/jnlentz/ConvoForge/blob/main/assets/data_management_tab.jpg?raw=true)

---

## Technical Details

* **Tabbed Interface:** A clean, multi-tab layout separating data collection, model interaction (chat), and data management.
* **Live Model Inference:**
    * Load and chat with different models, including base models and your own fine-tuned adapters (e.g., QLoRA).
    * Supports multiline input (`Shift+Enter`) and renders model responses as markdown.
* **Efficient & Local:**
    * Uses multithreading for non-blocking model loading and inference.
    * All data is stored locally in a SQLite database.
    * Loads models in 4-bit precision to conserve VRAM.

## Tech Stack

* **Backend & UI:** Python 3, PyQt6
* **Machine Learning:** PyTorch, Hugging Face `transformers`, `peft`, `bitsandbytes`
* **Database:** SQLite

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/jnlentz/ConvoForge.git](https://github.com/jnlentz/ConvoForge.git)
    cd ConvoForge
    ```

2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Hugging Face Login (Required for Gemma):**
    The base model for this demo (`google/gemma-2b-it`) is a gated model. You must be logged into your Hugging Face account to download it.
    ```bash
    huggingface-cli login
    ```
    Follow the prompts and paste your access token.

## Usage

1.  **Launch the application:**
    ```bash
    python main.py
    ```

2.  **Collect Data:**
    * Navigate to the "Data Collection" tab.
    * Select a source model (or type a new one).
    * Auto-generate an ID and provide a summary.
    * Paste user/assistant pairs and save.

3.  **Chat with a Model:**
    * Navigate to the "Chat" tab.
    * Select a model to load (e.g., "Base Model").
    * Click "Load Model" and wait for it to finish.
    * Create a new chat session by providing a summary and clicking "Create New Chat".
    * Start chatting! Your conversation will be saved automatically.
