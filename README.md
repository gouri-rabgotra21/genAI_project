# 🧑‍🍳 AI Food Recipe & Nutritional Chart Generator

> A Generative AI project that creates custom recipes and nutritional breakdowns based on user-provided ingredients.

This project, built for our 4th Year B.Tech Computer Engineering coursework, uses a locally-run Large Language Model (Llama 3) to generate novel recipes. The app takes a list of ingredients from a user and returns a complete, step-by-step recipe along with an approximate nutritional chart (calories, protein, fat, and carbs).

## 📸 Demo

**(Note: Add a screenshot here!)**

*After you run the `streamlit_app.py`, take a screenshot of the app working and place it here. You can add it to GitHub and then edit this file to link to it.*

---

## 🎯 Problem Statement

Many home cooks face two common problems:
1.  **Recipe Repetition:** They get stuck cooking the same few dishes, unsure what else to make with the ingredients they have.
2.  **Nutritional Unawareness:** It's difficult to know the health profile (calories, macros) of a home-cooked meal.

This tool solves both issues by providing creative, on-the-fly recipes while simultaneously calculating the nutritional content, linking food preparation with health awareness.

## ✨ Features

* **Dynamic Recipe Generation:** Get unique recipes, not just fixed search results.
* **Ingredient-Based:** Uses whatever ingredients you have on hand.
* **Nutritional Analysis:** Automatically calculates and displays calories, protein, fat, and carbs for the generated recipe.
* **Local-First AI:** Runs 100% locally using **Ollama** and **Llama 3**. No API keys or internet connection (for the AI) are required.
* **Web Interface:** A simple, clean front-end built with **Streamlit**.

---

## 🛠️ Technology Stack

* **AI Model:** Llama 3 (running via [Ollama](https://ollama.com/))
* **Backend & Logic:** Python
* **Web Framework:** Streamlit
* **AI/Python Connector:** `ollama` Python library
* **Parsing:** `re` (Regular Expressions) to extract structured JSON from the model's output.

---

## 🚀 How to Run This Project Locally

This project runs 100% on your local machine.

### Prerequisites

1.  **Ollama:** You must have the [Ollama](https://ollama.com/) application installed and running.
2.  **Llama 3:** You must have the Llama 3 model pulled.
    ```bash
    ollama run llama3
    ```
3.  **Python:** Python 3.8 or newer.

### Installation & Setup

1.  **Clone the repository (or use your local folder):**
    ```bash
    git clone [https://github.com/gouri-rabgotra21/genAI_project.git](https://github.com/gouri-rabgotra21/genAI_project.git)
    cd genAI_project
    ```

2.  **Install Python dependencies:**
    (It's a good idea to create a `requirements.txt` file for this)
    ```bash
    pip install streamlit ollama
    ```

3.  **Run the Streamlit App:**
    Make sure your Ollama application is running in the background!
    ```bash
    streamlit run streamlit_app.py
    ```

Your browser will automatically open to `http://localhost:8501`, and you can start using the app.

## 👥 Project 

* **Gouri Rabgotra** ([gouri-rabgotra21](https://github.com/gouri-rabgotra21))
