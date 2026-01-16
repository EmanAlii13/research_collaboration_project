# mongo_setup_complete_final.py
# إعداد MongoDB لكل الحسابين (Account 1 + Account 2)
# كل الباحثين، المشاريع، والمنشورات موجودين بالكامل

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# MongoDB Account 1
# =========================
MONGO_URI_1 = os.getenv("MONGO_URI_1")
client1 = MongoClient(MONGO_URI_1)
db1 = client1["research_db"]
researchers_col1 = db1["researchers"]
projects_col1 = db1["projects"]
publications_col1 = db1["publications"]

# =========================
# MongoDB Account 2
# =========================
MONGO_URI_2 = os.getenv("MONGO_URI_2")
client2 = MongoClient(MONGO_URI_2)
db2 = client2["research_db"]
researchers_col2 = db2["researchers"]
projects_col2 = db2["projects"]
publications_col2 = db2["publications"]

# =========================
# مسح البيانات القديمة في الحسابين
# =========================
for col in [researchers_col1, projects_col1, publications_col1,
            researchers_col2, projects_col2, publications_col2]:
    col.delete_many({})
print("✅ تم مسح جميع البيانات القديمة في الحسابين!")

# =========================
# بيانات الباحثين (50 باحث)
# =========================
researchers = [
    {"name": "Eman Ali", "department": "Computer Science", "interests": ["AI", "Data Science"]},
    {"name": "Sara Ahmad", "department": "Biology", "interests": ["Genetics", "Microbiology"]},
    {"name": "Hajar Ali", "department": "Physics", "interests": ["Quantum Mechanics", "Astrophysics"]},
    {"name": "Tariq Hassan", "department": "Computer Science", "interests": ["Cybersecurity", "Networks"]},
    {"name": "Mona Youssef", "department": "Biology", "interests": ["Ecology", "Microbiology"]},
    {"name": "Ali Zaid", "department": "Physics", "interests": ["Thermodynamics", "Astrophysics"]},
    {"name": "Dina Omar", "department": "Chemistry", "interests": ["Organic Chemistry", "Nanomaterials"]},
    {"name": "Salma Tarek", "department": "Mathematics", "interests": ["Algebra", "Topology"]},
    {"name": "Khaled Mahmoud", "department": "Computer Science", "interests": ["AI", "Robotics"]},
    {"name": "Rana Youssef", "department": "Physics", "interests": ["Particle Physics", "Quantum Mechanics"]},
    {"name": "Omar Sami", "department": "Computer Science", "interests": ["Software Engineering", "Databases"]},
    {"name": "Laila Amin", "department": "Biology", "interests": ["Microbiology", "Immunology"]},
    {"name": "Youssef Nabil", "department": "Physics", "interests": ["Optics", "Quantum Mechanics"]},
    {"name": "Amira Khalid", "department": "Chemistry", "interests": ["Analytical Chemistry", "Nanomaterials"]},
    {"name": "Adel Fathy", "department": "Mathematics", "interests": ["Number Theory", "Topology"]},
    {"name": "Nour Hassan", "department": "Computer Science", "interests": ["AI", "Cybersecurity"]},
    {"name": "Fatma Adel", "department": "Biology", "interests": ["Genetics", "Ecology"]},
    {"name": "Karim Salah", "department": "Physics", "interests": ["Astrophysics", "Thermodynamics"]},
    {"name": "Mariam Nader", "department": "Chemistry", "interests": ["Organic Chemistry", "Polymer Chemistry"]},
    {"name": "Tamer Mostafa", "department": "Mathematics", "interests": ["Algebra", "Combinatorics"]},
    {"name": "Rania Khaled", "department": "Computer Science", "interests": ["Robotics", "AI"]},
    {"name": "Mahmoud Fawzy", "department": "Biology", "interests": ["Microbiology", "Genetics"]},
    {"name": "Heba Samir", "department": "Physics", "interests": ["Quantum Mechanics", "Optics"]},
    {"name": "Omar Khalil", "department": "Chemistry", "interests": ["Nanomaterials", "Organic Chemistry"]},
    {"name": "Salma Nabil", "department": "Mathematics", "interests": ["Topology", "Algebra"]},
    {"name": "Mohamed Adel", "department": "Computer Science", "interests": ["Software Engineering", "AI"]},
    {"name": "Noha Fathi", "department": "Biology", "interests": ["Ecology", "Immunology"]},
    {"name": "Hany Youssef", "department": "Physics", "interests": ["Particle Physics", "Astrophysics"]},
    {"name": "Lina Samir", "department": "Chemistry", "interests": ["Analytical Chemistry", "Nanomaterials"]},
    {"name": "Amr Tarek", "department": "Mathematics", "interests": ["Combinatorics", "Number Theory"]},
    {"name": "Aya Khalid", "department": "Computer Science", "interests": ["AI", "Networks"]},
    {"name": "Karim Nader", "department": "Biology", "interests": ["Genetics", "Microbiology"]},
    {"name": "Dalia Youssef", "department": "Physics", "interests": ["Astrophysics", "Thermodynamics"]},
    {"name": "Hossam Adel", "department": "Chemistry", "interests": ["Organic Chemistry", "Nanomaterials"]},
    {"name": "Yara Sami", "department": "Mathematics", "interests": ["Topology", "Algebra"]},
    {"name": "Ahmed Nabil", "department": "Computer Science", "interests": ["Robotics", "AI"]},
    {"name": "Salma Mahmoud", "department": "Biology", "interests": ["Ecology", "Immunology"]},
    {"name": "Huda Fathy", "department": "Physics", "interests": ["Quantum Mechanics", "Optics"]},
    {"name": "Omar Adel", "department": "Chemistry", "interests": ["Nanomaterials", "Organic Chemistry"]},
    {"name": "Mona Khalid", "department": "Mathematics", "interests": ["Algebra", "Combinatorics"]},
    {"name": "Ali Samir", "department": "Computer Science", "interests": ["AI", "Data Science"]},
    {"name": "Nada Youssef", "department": "Biology", "interests": ["Genetics", "Microbiology"]},
    {"name": "Fadi Tarek", "department": "Physics", "interests": ["Astrophysics", "Particle Physics"]},
    {"name": "Rania Sami", "department": "Chemistry", "interests": ["Organic Chemistry", "Nanomaterials"]},
    {"name": "Hassan Nader", "department": "Mathematics", "interests": ["Topology", "Number Theory"]},
    {"name": "Lamia Adel", "department": "Computer Science", "interests": ["AI", "Cybersecurity"]},
    {"name": "Salwa Khalid", "department": "Biology", "interests": ["Microbiology", "Ecology"]},
    {"name": "Amr Youssef", "department": "Physics", "interests": ["Quantum Mechanics", "Astrophysics"]},
    {"name": "Dina Fathi", "department": "Chemistry", "interests": ["Analytical Chemistry", "Organic Chemistry"]},
    {"name": "Tamer Samir", "department": "Mathematics", "interests": ["Algebra", "Topology"]},
]

# =========================
# بيانات المشاريع (20 مشروع)
# =========================
projects = [
    {"title": "AI in Healthcare", "participants": ["Eman Ali", "Tariq Hassan", "Khaled Mahmoud"], "publications": ["AI & Medicine 2026", "Healthcare AI Review"]},
    {"title": "Quantum Computing Applications", "participants": ["Hajar Ali", "Ali Zaid", "Rana Youssef"], "publications": ["Quantum Algorithms", "Quantum Simulations"]},
    {"title": "Microbiology Discoveries", "participants": ["Sara Ahmad", "Mona Youssef", "Fatma Adel"], "publications": ["Bacterial Studies 2026", "Virus Research"]},
    {"title": "Robotics and Automation", "participants": ["Eman Ali", "Aya Khalid", "Khaled Mahmoud"], "publications": ["Robotics Today", "Automation in Industry"]},
    {"title": "Cybersecurity Research", "participants": ["Tariq Hassan", "Lamia Adel", "Ahmed Nabil"], "publications": ["Cyber Threats 2026", "Network Security Advances"]},
    {"title": "Genetics and Bioinformatics", "participants": ["Sara Ahmad", "Karim Nader", "Nada Youssef"], "publications": ["Genomics Insights", "Bioinformatics Review"]},
    {"title": "Astrophysics Simulations", "participants": ["Hajar Ali", "Dalia Youssef", "Fadi Tarek"], "publications": ["Star Formation Study", "Black Hole Simulations"]},
    {"title": "Organic Chemistry Innovations", "participants": ["Dina Omar", "Amira Khalid", "Rania Sami"], "publications": ["Synthesis Advances", "Organic Reactions 2026"]},
    {"title": "Machine Learning Applications", "participants": ["Eman Ali", "Nour Hassan", "Mohamed Adel"], "publications": ["ML for Science", "Data Patterns"]},
    {"title": "Ecology and Conservation", "participants": ["Mona Youssef", "Fatma Adel", "Salma Mahmoud"], "publications": ["Ecosystem Study", "Conservation Methods"]},
    {"title": "Nanotechnology Research", "participants": ["Dina Omar", "Amira Khalid", "Omar Khalil"], "publications": ["Nano Devices", "Nanomaterials 2026"]},
    {"title": "Topology in Mathematics", "participants": ["Salma Tarek", "Amr Tarek", "Hassan Nader"], "publications": ["Topology Concepts", "Mathematics Today"]},
    {"title": "Particle Physics Experiments", "participants": ["Rana Youssef", "Hany Youssef", "Fadi Tarek"], "publications": ["Particle Collisions", "Physics Review"]},
    {"title": "Data Science Projects", "participants": ["Eman Ali", "Ali Samir", "Mohamed Adel"], "publications": ["Data Insights", "Predictive Models"]},
    {"title": "Immunology Studies", "participants": ["Laila Amin", "Noha Fathi", "Salma Mahmoud"], "publications": ["Immune Response Study", "Vaccine Research"]},
    {"title": "Software Engineering Research", "participants": ["Omar Sami", "Ahmed Nabil", "Karim Salah"], "publications": ["Software Patterns", "Agile Methods"]},
    {"title": "AI in Robotics", "participants": ["Khaled Mahmoud", "Aya Khalid", "Rania Khaled"], "publications": ["Robotics AI 2026", "Machine Learning Robotics"]},
    {"title": "Thermodynamics Research", "participants": ["Ali Zaid", "Karim Salah", "Hajar Ali"], "publications": ["Heat Transfer Study", "Energy Systems"]},
    {"title": "Organic Nanomaterials", "participants": ["Dina Omar", "Rana Sami", "Rania Sami"], "publications": ["Nano Synthesis", "Advanced Materials"]},
    {"title": "Combinatorics and Algebra", "participants": ["Salma Tarek", "Amr Tarek", "Tamer Samir"], "publications": ["Combinatorics Study", "Algebra Methods"]},
]

# =========================
# إضافة الباحثين لكل الحسابين
# =========================
for col in [researchers_col1, researchers_col2]:
    col.insert_many(researchers)
print(f"✅ تم إضافة {len(researchers)} باحثين لكل الحساب!")

# =========================
# إضافة المشاريع لكل الحسابين
# =========================
for col in [projects_col1, projects_col2]:
    col.insert_many(projects)
print(f"✅ تم إضافة {len(projects)} مشاريع لكل الحساب!")

# =========================
# إضافة المنشورات لكل الحسابين
# =========================
publications_list = []
for project in projects:
    for pub_title in project["publications"]:
        publications_list.append({
            "title": pub_title,
            "project": project["title"],
            "authors": project["participants"]
        })

for col in [publications_col1, publications_col2]:
    col.insert_many(publications_list)
print(f"✅ تم إضافة {len(publications_list)} منشورات لكل الحساب!")
