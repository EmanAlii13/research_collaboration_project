from pymongo import MongoClient

# =========================
# 1️⃣ الاتصال بـ MongoDB Atlas
# =========================
connection_string = "mongodb+srv://eman_user:moon123Ali@research-cluster.jnmku4p.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)

# اختيار قاعدة البيانات والـ Collections
db = client["research_db"]
researchers_collection = db["researchers"]
projects_collection = db["projects"]
publications_collection = db["publications"]

print("تم الاتصال بMongoDB Atlas بنجاح!")

# =========================
# 2️⃣ مسح جميع البيانات القديمة
# =========================
researchers_collection.delete_many({})
projects_collection.delete_many({})
publications_collection.delete_many({})
print("تم مسح جميع البيانات القديمة!")

# =========================
# 3️⃣ بيانات الباحثين (20 باحث)
# =========================
sample_researchers = [
    {"name": "Eman Ali", "department": "Computer Science", "interests": ["AI", "Data Science"]},
    {"name": "Sara Ahmad", "department": "Biology", "interests": ["Genetics", "Microbiology"]},
    {"name": "Hajar Ali", "department": "Physics", "interests": ["Quantum Mechanics", "Astrophysics"]},
    {"name": "Omar Khalid", "department": "Mathematics", "interests": ["Statistics", "Topology"]},
    {"name": "Lina Samir", "department": "Chemistry", "interests": ["Organic Chemistry", "Biochemistry"]},
    {"name": "Tariq Hassan", "department": "Computer Science", "interests": ["AI", "Networks"]},
    {"name": "Mona Youssef", "department": "Biology", "interests": ["Microbiology", "Genetics"]},
    {"name": "Ali Zaid", "department": "Physics", "interests": ["Quantum Mechanics", "Thermodynamics"]},
    {"name": "Dina Omar", "department": "Mathematics", "interests": ["Algebra", "Calculus"]},
    {"name": "Khaled Sami", "department": "Computer Science", "interests": ["AI", "Data Science"]},
    {"name": "Rana Mahdi", "department": "Biology", "interests": ["Genetics", "Botany"]},
    {"name": "Fadi Nasser", "department": "Physics", "interests": ["Optics", "Astrophysics"]},
    {"name": "Yara Khalil", "department": "Chemistry", "interests": ["Analytical Chemistry", "Biochemistry"]},
    {"name": "Ziad Omar", "department": "Computer Science", "interests": ["Cybersecurity", "Networks"]},
    {"name": "Salma Tarek", "department": "Mathematics", "interests": ["Statistics", "Topology"]},
    {"name": "Hani Jaber", "department": "Physics", "interests": ["Thermodynamics", "Astrophysics"]},
    {"name": "Maha Adel", "department": "Biology", "interests": ["Botany", "Genetics"]},
    {"name": "Omar Youssef", "department": "Computer Science", "interests": ["AI", "Machine Learning"]},
    {"name": "Laila Hani", "department": "Mathematics", "interests": ["Algebra", "Calculus"]},
    {"name": "Sami Fadi", "department": "Physics", "interests": ["Quantum Mechanics", "Optics"]}
]

researchers_collection.insert_many(sample_researchers)
print(f"تم إضافة {len(sample_researchers)} باحثين بنجاح!")

# =========================
# 4️⃣ بيانات المنشورات (25 منشور)
# =========================
sample_publications = [
    {"title": f"AI in Healthcare {i}", "year": 2025, "authors": ["Eman Ali", "Tariq Hassan"]} for i in range(1, 11)
] + [
    {"title": f"Genetics Breakthrough {i}", "year": 2024, "authors": ["Sara Ahmad", "Mona Youssef"]} for i in range(1, 6)
] + [
    {"title": f"Physics Insights {i}", "year": 2023, "authors": ["Hajar Ali", "Ali Zaid"]} for i in range(1, 6)
] + [
    {"title": f"Math Advances {i}", "year": 2022, "authors": ["Dina Omar", "Salma Tarek"]} for i in range(1, 5)
]

publications_collection.insert_many(sample_publications)
print(f"تم إضافة {len(sample_publications)} منشورات بنجاح!")

# =========================
# 5️⃣ بيانات المشاريع (30 مشروع)
# =========================
sample_projects = [
    {"title": f"AI Project {i}", "researchers": ["Eman Ali", "Tariq Hassan"], "publications": [f"AI in Healthcare {i}"]} for i in range(1, 11)
] + [
    {"title": f"Genetics Project {i}", "researchers": ["Sara Ahmad", "Mona Youssef"], "publications": [f"Genetics Breakthrough {i}"]} for i in range(1, 6)
] + [
    {"title": f"Physics Project {i}", "researchers": ["Hajar Ali", "Ali Zaid"], "publications": [f"Physics Insights {i}"]} for i in range(1, 6)
] + [
    {"title": f"Math Project {i}", "researchers": ["Dina Omar", "Salma Tarek"], "publications": [f"Math Advances {i}"]} for i in range(1, 9)
]

projects_collection.insert_many(sample_projects)
print(f"تم إضافة {len(sample_projects)} مشاريع بنجاح!")
