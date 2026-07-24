from groq import Groq


def build_candidate_context(rankings: list) -> str:
    
    context_parts = []

    for i, candidate in enumerate(rankings, start=1):
        part = (
            f"Rank {i}: {candidate['name']} — Overall Score: {candidate['overall']}%\n"
            f"  Skills Match: {candidate['skills']}%\n"
            f"  Experience Match: {candidate['experience']}%\n"
            f"  Education Match: {candidate['education']}%\n"
            f"  Certifications Match: {candidate['certifications']}%\n"
            f"  Projects Match: {candidate['projects']}%\n"
            f"  Matched Skills: {', '.join(candidate['matched_skills']) if candidate['matched_skills'] else 'None'}\n"
            f"  Missing Skills: {', '.join(candidate['missing_skills']) if candidate['missing_skills'] else 'None'}\n"
        )
        context_parts.append(part)

    return "\n".join(context_parts)
def get_chatbot_response(user_question: str, rankings: list, api_key: str, chat_history: list = None) -> str:
    
    if chat_history is None:
        chat_history = []

    try:
        client = Groq(api_key=api_key)

        candidate_context = build_candidate_context(rankings)

        system_prompt = (
            "You are an HR assistant helping recruiters evaluate job candidates. "
            "You have access to the following candidate ranking data:\n\n"
            f"{candidate_context}\n\n"
            "Answer questions about these candidates clearly and concisely, "
            "referencing specific scores and skills where relevant. "
            "Be honest about each candidate's strengths and weaknesses."
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_question})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.5,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I ran into an error contacting the AI assistant: {e}"
