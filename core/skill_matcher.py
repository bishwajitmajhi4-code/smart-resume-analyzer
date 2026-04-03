# Ek basic skills ki list. Aage chal kar tum isme aur skills add kar sakte ho!
TECH_SKILLS = [
    "python", "java", "c++", "c", "sql", "mysql", "mongodb",
    "html", "css", "javascript", "react", "node.js",
    "flask", "django", "machine learning", "ai", "data analysis",
    "git", "github", "docker", "aws", "linux", "excel"
]

def analyze_resume_text(resume_text):
    detected_skills = []
    
    # Check karo ki list ka kaunsa skill resume ke text mein majood hai
    for skill in TECH_SKILLS:
        if skill in resume_text:
            detected_skills.append(skill)
            
    # Score Calculation: Hum maan rahe hain ki minimum 8 skills hone chahiye achhe score ke liye
    target_skills = 8
    
    if len(detected_skills) == 0:
        score = 0
    else:
        score = int((len(detected_skills) / target_skills) * 100)
        
    # Score 100 se upar nahi jana chahiye
    if score > 100:
        score = 100
        
    # Database mein save karne ke liye skills ko ek string (text) bana diya
    skills_string = ", ".join(detected_skills)
    
    return score, skills_string