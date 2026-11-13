
# ==========================================
# MULTIPLE DISEASE PREDICTION
# HEALTHCARE CHATBOT ENGINE
# ==========================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Healthcare Knowledge Base
knowledge_base = [

    # DIABETES
    {
        "question": "What is diabetes?",
        "answer": "Diabetes is a chronic condition in which blood glucose levels become too high because the body does not produce enough insulin or cannot use insulin effectively."
    },
    {
        "question": "What are the symptoms of diabetes?",
        "answer": "Common symptoms include frequent urination, excessive thirst, increased hunger, fatigue, blurred vision and unexplained weight loss."
    },
    {
        "question": "How can diabetes be prevented?",
        "answer": "Type 2 diabetes risk can be reduced through regular physical activity, balanced nutrition, maintaining a healthy weight and regular health checkups. Prevention is not guaranteed."
    },
    {
        "question": "What causes diabetes?",
        "answer": "Diabetes has different causes depending on its type. Type 1 involves autoimmune destruction of insulin-producing cells, while Type 2 involves insulin resistance and other metabolic factors."
    },

    # HEART DISEASE
    {
        "question": "What is heart disease?",
        "answer": "Heart disease refers to conditions affecting the heart, including coronary artery disease, heart rhythm disorders and problems with heart structure."
    },
    {
        "question": "What are the symptoms of heart disease?",
        "answer": "Symptoms may include chest discomfort, shortness of breath, fatigue, dizziness and irregular heartbeat. Sudden chest pain or breathing difficulty requires urgent medical attention."
    },
    {
        "question": "What causes heart disease?",
        "answer": "Risk factors include high blood pressure, high cholesterol, smoking, diabetes, physical inactivity and family history."
    },
    {
        "question": "How can heart disease be prevented?",
        "answer": "Risk can be reduced through physical activity, a balanced diet, avoiding tobacco, managing blood pressure and cholesterol, and regular medical checkups."
    },

    # PARKINSON'S DISEASE
    {
        "question": "What is Parkinson's disease?",
        "answer": "Parkinson's disease is a progressive neurological disorder that affects movement and is associated with changes in dopamine-producing brain cells."
    },
    {
        "question": "What are the symptoms of Parkinson's disease?",
        "answer": "Common symptoms include tremors, muscle stiffness, slowed movement and balance difficulties. Symptoms vary between individuals."
    },
    {
        "question": "What causes Parkinson's disease?",
        "answer": "The exact cause is not fully understood. A combination of genetic and environmental factors may contribute."
    },
    {
        "question": "Can Parkinson's disease be cured?",
        "answer": "There is currently no established cure for Parkinson's disease, but medications, rehabilitation and other treatments can help manage symptoms."
    },

    # GENERAL HEALTH
    {
        "question": "What is BMI?",
        "answer": "BMI stands for Body Mass Index. It is calculated using weight in kilograms divided by height in metres squared. It is a screening measure, not a complete assessment of health."
    },
    {
        "question": "Why are regular health checkups important?",
        "answer": "Regular health checkups can help identify health risks, monitor existing conditions and support early medical intervention."
    },
    {
        "question": "What is blood pressure?",
        "answer": "Blood pressure measures the force of blood against artery walls. It is recorded using two numbers: systolic and diastolic pressure."
    },
    {
        "question": "Can this chatbot diagnose diseases?",
        "answer": "No. This chatbot provides general healthcare information only. It cannot diagnose diseases or replace advice from a qualified healthcare professional."
    }
]

print("Knowledge base loaded successfully!")
print("Total questions:", len(knowledge_base))
# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Extract questions from the knowledge base
questions = [item["question"] for item in knowledge_base]

# Convert questions into TF-IDF vectors
question_vectors = vectorizer.fit_transform(questions)

print("TF-IDF vectorization completed!")
print("Vector shape:", question_vectors.shape)
# Import cosine similarity
from sklearn.metrics.pairwise import cosine_similarity


def get_best_match(user_question):
    # Convert user's question into a TF-IDF vector
    user_vector = vectorizer.transform([user_question])

    # Compare user question with all knowledge-base questions
    similarity_scores = cosine_similarity(
        user_vector,
        question_vectors
    )

    # Find the index of the highest similarity score
    best_match_index = similarity_scores.argmax()

    # Get the similarity score
    best_score = similarity_scores[0][best_match_index]

    # Get the matching answer
    # Set minimum similarity threshold
    THRESHOLD = 0.60

    if best_score < THRESHOLD:
        return (
        "I'm sorry, I couldn't understand your question. "
        "I can help with diabetes, heart disease, Parkinson's "
        "disease and general health topics. Please try rephrasing.",
        best_score
    )

    best_answer = knowledge_base[best_match_index]["answer"]
    

    return best_answer, best_score

if __name__ == "__main__":
    test_questions = [
        "What are the symptoms of diabetes?",
        "How do I repair a car engine?",
        "What causes heart disease?",
        "Tell me about the weather today."
    ]

    for question in test_questions:
        answer, score = get_best_match(question)

        print("\nQuestion:", question)
        print("Answer:", answer)
        print("Similarity:", round(float(score), 3))