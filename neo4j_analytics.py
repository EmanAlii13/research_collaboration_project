import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# =========================
# تحميل متغيرات البيئة من ملف .env
# =========================
load_dotenv()
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# إنشاء الاتصال مع Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# =========================
# دالة لتشغيل أي استعلام وإرجاع النتائج كقائمة
# ⚡ مهم لتحويل النتائج لقائمة لتجنب ResultConsumedError
# =========================
def run_query(query):
    with driver.session(database="neo4j") as session:
        result = session.run(query)
        return list(result)

# =========================
# 1️⃣ Top authors by publications
# =========================
print("\n--- Top Authors by Publications ---")
query_top_authors = """
MATCH (r:Researcher)-[:AUTHORED]->(p:Publication)
RETURN r.name AS Researcher, COUNT(p) AS Publications
ORDER BY Publications DESC
LIMIT 5
"""
for record in run_query(query_top_authors):
    print(f"{record['Researcher']}: {record['Publications']} publications")  # عرض النتائج بالإنجليزي

# =========================
# 2️⃣ Top co-author pairs
# =========================
print("\n--- Top Co-Author Pairs ---")
query_top_pairs = """
MATCH (r1:Researcher)-[:CO_AUTHOR]-(r2:Researcher)
WITH r1.name AS Researcher1, r2.name AS Researcher2, COUNT(*) AS Collaborations
ORDER BY Collaborations DESC
LIMIT 5
RETURN Researcher1, Researcher2, Collaborations
"""
for record in run_query(query_top_pairs):
    print(f"{record['Researcher1']} ↔ {record['Researcher2']}: {record['Collaborations']} collaborations")

# =========================
# 3️⃣ Most collaborative researchers in projects
# =========================
print("\n--- Most Collaborative Researchers in Projects ---")
query_top_teamwork = """
MATCH (r:Researcher)-[:TEAMMATE]->(colleague)
RETURN r.name AS Researcher, COUNT(DISTINCT colleague) AS Teammates
ORDER BY Teammates DESC
LIMIT 5
"""
for record in run_query(query_top_teamwork):
    print(f"{record['Researcher']}: {record['Teammates']} teammates")

# =========================
# 4️⃣ All researchers in a specific project (example: "AI Project 1")
# =========================
print("\n--- All Researchers in Project 'AI Project 1' ---")
query_project_members = """
MATCH (pr:Project {title: "AI Project 1"})<-[:WORKS_ON]-(r:Researcher)
RETURN r.name AS Researcher
"""
for record in run_query(query_project_members):
    print(f"- {record['Researcher']}")

# =========================
# 5️⃣ All collaboration relationships
# =========================
print("\n--- All Collaboration Relationships Between Researchers ---")
query_all_relations = """
MATCH (r1:Researcher)-[rel]->(r2:Researcher)
WHERE type(rel) IN ["CO_AUTHOR","TEAMMATE"]
RETURN r1.name AS From, type(rel) AS Relation, r2.name AS To
"""
for record in run_query(query_all_relations):
    print(f"{record['From']} -[{record['Relation']}]-> {record['To']}")

driver.close()
print("\n✅ All analytics completed successfully!")
