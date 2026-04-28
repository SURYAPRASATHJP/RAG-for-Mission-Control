import ollama
import matplotlib.pyplot as plt
import re
import time

MODELS = ['llama3.1:latest', 'glm-4.7-flash:latest', 'gemma4:latest']
GRADER_MODEL = 'gemma4:latest'

TEST_DATA = [
    {"question": "What were the liftoff dates, times and azimuths for the Apollo 11 mission?", "answer": """Date
    Time
    Azimuth
    July 16,
    8:32 am CDT
    72–108 degrees
    July 18,
    10:30 am CDT
    89–108 degrees
    July 21,
    11:09 am CDT
    94–108 degrees
"""},
    {"question": "What are the 9 connection points between the Saturn rocket and the umbilical tower? What is the purpose of each connection point? Is the connection point retracted pre-flight or in-flight?", "answer": """Interface
    Purpose
    Disconnect Time
    S-IC Intertank
    Provides LOX fill and drain.
    preflight
    S-IC Forward
    Provides pneumatic, electrical, and air-conditioning interfaces.
    preflight
    S-II Aft
    Provides vehicle access
    preflight
    S-II Intermediate
    Provides LH2 and LOX transfer, vent line, pneumatic, instrument cooling, electrical, and air-condition interfaces
    in-flight
    S-II Forward
    Provides GH2 vent, electrical, and pneumatic interfaces
    in-flight
    S-IVB Forward
    S-IVB Forward
    in-flight
    S-IVB Forward
    Provides LH2 and LOX transfer, vent line, pneumatic, electrical, and air-condition interfaces
    in-flight
    Serivce Module
    Provides air-conditioning, vent line, coolant, electrical, and pneumatic interfaces
    in-flight
    Command Module Access Arm
    Provides access to spacecraft through environmental chamber
    preflight
"""},
    {"question": "How can the astronauts enable the backup automatic control system? What if manual control is needed?",
     "answer": "Enable the LV Guidance switch for backup system. For manual control: enable LV guidance switch, enter a word into the S/C computer, flip AUTO/MANUAL switches to MANUAL."},
    {"question": " In Project Mercury astronaut M. Scott Carpenter was the prime pilot for the United States manned orbital flight, was he the first one to be the prime pilot?",
     "answer": "no the second prime pilot"},
    {"question": "Is the Stowage List available for the public to view from the apollo11  project?", "answer": "yes"},
    {"question": "How long was the Apollo program active?", "answer": "4 years, from 1968 to 1972"}
]

def get_response(model, prompt):
    response = ollama.chat(model=model, messages=[
        {'role': 'user', 'content': prompt},
    ])
    return response['message']['content']

def visualize_results(results):
    names = {"llama3.1:latest":"Llama3", 
             "glm-4.7-flash:latest":"GLM 4.7",
             "gemma4:latest":"Gemma 4"}
    model_names_raw = list(results.keys())
    model_names = []
    for n in model_names_raw:
        model_names.append(names[n])
        
    avg_scores = [sum(scores) / len(scores) for scores in results.values()]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(model_names, avg_scores, color=['#3498db', '#e74c3c', '#2ecc71'])
    
    plt.xlabel('Models', fontweight='bold')
    plt.ylabel('Average Score (0-10)', fontweight='bold')
    plt.title('Model Benchmarking: Response Accuracy', fontsize=14)
    plt.ylim(0, 11) # Slight overhead for clarity
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.1f}", ha='center', fontweight='bold')

    plt.tight_layout()
    plt.show()

raw_results = {model: [] for model in MODELS}

print("--- Phase 1: Collecting Responses ---")
for model in MODELS:
    print(f"Current Model: {model}\n\tStart Time: {time.time()}")
    for item in TEST_DATA:
        #print(f"  Asking: {item['question'][:30]}...")
        response_text = get_response(model, item['question'])
        
        raw_results[model].append({
            "question": item['question'],
            "correct_answer": item['answer'],
            "student_response": response_text
        })
    print("\tEnd Time", time.time())

final_scores = {model: [] for model in MODELS}
print(f"\n--- Phase 2: Grading with {GRADER_MODEL} ---")

with open("responses.txt", "w", encoding="utf-8") as fout:
    for model, tests in raw_results.items():
        fout.write(f"{model}: \n")
        print(f"Grading responses for: {model}")
        for test in tests:
            grading_prompt = f"""
            Grade the student's response based on the correct answer.
            Question: {test['question']}
            Correct Answer: {test['correct_answer']}
            Student's Response: {test['student_response']}

            Provide a score between 0 and 10. Return ONLY the numeric score.
            """
            try:
                score_raw = get_response(GRADER_MODEL, grading_prompt)
                score_match = re.search(r'\d+', score_raw)
                score = int(score_match.group()) if score_match else 0
                fout.write(f"""Score: {score} \n
                           Q: {test['question']}
                           A: {test['student_response']}
                           """)
                final_scores[model].append(score)
            except Exception as e:
                print("Grading Error", e)

fout.close()
visualize_results(final_scores)
print("\n--- Summary ---")
for model, scores in final_scores.items():
    print(f"{model.upper()}: {sum(scores)/len(scores):.2f} / 10.0")