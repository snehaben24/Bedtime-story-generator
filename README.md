# Bedtime Story Generator with Judge & User Feedback

## 📌 Overview
This project implements a multi-agent LLM system that generates bedtime stories appropriate for children ages 5–10. The design ensures both creativity and safety, combining storytelling with internal quality checks and a user feedback loop.

The system flow:
- **Classifier Agent** → Categorizes the user request (e.g., animals, adventure, bedtime-calming)
- **Storyteller Agent** → Generates the first draft based on request + category
- **Judge Agent** → Evaluates draft for coherence, age-appropriateness, warmth, clarity, and safety
- **Reviser Agent (Internal QC)** → Fixes issues if Judge identifies flaws
- A short Judge ↔ Reviser loop ensures a polished story is created before showing it to the user
- **User Feedback Loop** → User reviews the story
  - If accepted → Finalized
  - If feedback provided (e.g., "make it shorter," "add a princess") → Reviser updates the story
  - Loop limited to 2 revisions to prevent endless back-and-forth

This design guarantees that the first story a user sees is already safe and high-quality, while still letting users guide the narrative to their liking.

## ⚙️ How It Works
- **Model**: Uses gpt-3.5-turbo (per assignment requirement)
- **QC Flow**: Draft → Judge → (optional Reviser) → Judge again
- **User Feedback**: Interactive loop after internal QC
- **Failure Handling**:
  - If the Judge returns invalid JSON → system defaults to requiring revision
  - If QC loop exceeds iteration limit → latest draft is passed forward to user
- **CLI Support**:
  - Run with `-p` for prompt input
  - Prompts user for feedback until acceptance or revision cap

## 🧩 Architecture Diagram
![Architecture Diagram](./AI%20Agent%20Deployment%20Engineer%20Takehome/block_diagram.jpg)


## ✅ Features Implemented
- Story arcs enforced (setup → challenge → resolution)
- Judge rubric (age appropriateness, clarity, warmth, safety, coherence)
- Internal QC loop before showing draft to user
- Interactive user feedback with bounded iterations
- Category classification to adapt story tone
- Logging and error handling for robustness

## 🚀 How to Run

### Install dependencies:
```bash
pip install openai
```
### Set up your API key:
```bash
export OPENAI_API_KEY="your_api_key_here"
```
### Run the story generator:
#### Run the script without a prompt (you’ll be asked for input):
```bash
python main.py
```
#### Pass a prompt directly in the command line:
```bash
python main.py -p "A story about a shy turtle who learns to sing"
```
## 💬 User Feedback Process

After the internal quality check completes, the system will prompt you for feedback:

- **Press Enter** (empty input) to accept the story as-is and finalize it
- **Type specific feedback** to request revisions (e.g., "make it shorter", "add a princess", "more animal characters")

The system will incorporate your feedback and present a revised version, with a maximum of 2 revision cycles to ensure efficiency.

## 🔮 Future Enhancements

If I had additional development time, I would implement the following improvements:

### **Few-Shot Exemplars**
- Add category-specific examples to enhance consistency across story generations
- Improve tone and style alignment for each story type (adventure, calming, animal-themed, etc.)

### **Schema Validation**
- Implement Pydantic models to enforce valid JSON outputs from the Judge agent
- Ensure robust error handling and data integrity throughout the pipeline

### **Optimized Temperature Settings**
- Use deterministic low-temperature settings for Judge/Classifier passes to maintain consistency
- Reserve high creativity settings exclusively for the Storyteller agent
- Balance reliability with imaginative storytelling

### **Artifact Preservation**
- Save all intermediate artifacts (drafts, judge evaluations, revision history) to local storage
- Enable audit trails and quality monitoring capabilities
- Facilitate debugging and system improvement analysis

### **Web Interface**
- Develop a simple web UI using Streamlit or FastAPI for enhanced user experience
- Enable broader demo capabilities and user testing
- Provide visual feedback mechanisms and story browsing features

## 🎯 Alignment with Hippocratic AI's Mission

This project demonstrates my strong alignment with Hippocratic AI's core values and mission:

### **Safety-First Approach**
- The multi-layered validation system mirrors the critical need for safety in healthcare AI applications
- Built-in guardrails ensure age-appropriate, coherent, and warm content generation
- Proactive quality checks prevent problematic outputs before they reach users

### **Clinical-Grade Design Philosophy**
- The generate → evaluate → refine → deliver workflow reflects how clinical AI assistants should operate
- Continuous improvement loops mimic the iterative nature of medical diagnosis and treatment planning
- Balance between automation and human oversight ensures responsible deployment

### **Ethical Engineering Practices**
- My background in LLM engineering, prompt design, and production deployment focuses on building reliable systems
- Emphasis on transparency, auditability, and user control aligns with healthcare compliance requirements
- Commitment to creating AI that is not just powerful, but also trustworthy and beneficial

I am excited about the opportunity to apply this same rigorous, mission-driven approach to the groundbreaking work at Hippocratic AI, contributing to AI systems that prioritize patient safety and positive outcomes above all else.

## Author Information

- **Author:** Sneha Mary Bency

- **Submission Date:** 09/23/2025

- 🌐 [Portfolio Website](https://snehaben24.github.io/Portfolio/)

