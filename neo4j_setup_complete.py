from pymongo import MongoClient
from neo4j import GraphDatabase

# =========================
# MongoDB connection
# =========================
mongo_client = MongoClient("mongodb+srv://eman_user:moon123Ali@research-cluster.jnmku4p.mongodb.net/?retryWrites=true&w=majority")
mongo_db = mongo_client["research_db"]
researchers_col = mongo_db["researchers"]
projects_col = mongo_db["projects"]
publications_col = mongo_db["publications"]

# =========================
# Neo4j connection
# =========================
NEO4J_URI = "neo4j+s://9982f29b.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "civGZXIM4SsxeInLYNr3sW0j-W_24AYw0dT4MkoBAUY"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# =========================
# مسح كل البيانات القديمة في Neo4j
# =========================
def clear_neo4j(tx):
    tx.run("MATCH (n) DETACH DELETE n")

with driver.session() as session:
    session.write_transaction(clear_neo4j)
    print("تم مسح جميع البيانات القديمة في Neo4j!")

# =========================
# إضافة الباحثين
# =========================
def create_researcher(tx, name, department, interests):
    tx.run("""
        MERGE (r:Researcher {name: $name})
        SET r.department = $department, r.interests = $interests
    """, name=name, department=department, interests=interests)

# =========================
# إضافة المشاريع
# =========================
def create_project(tx, title):
    tx.run("""
        MERGE (p:Project {title: $title})
    """, title=title)

# =========================
# إضافة المنشورات
# =========================
def create_publication(tx, title):
    tx.run("""
        MERGE (pub:Publication {title: $title})
    """, title=title)

# =========================
# إضافة العلاقات
# =========================
def create_relationships(tx):
    # الباحث ↔ المشاريع
    for project in projects_col.find():
        for researcher_name in project["participants"]:
            tx.run("""
                MATCH (r:Researcher {name: $r_name}), (p:Project {title: $p_title})
                MERGE (r)-[:WORKED_ON]->(p)
            """, r_name=researcher_name, p_title=project["title"])

    # المشروع ↔ المنشورات
    for publication in publications_col.find():
        tx.run("""
            MATCH (p:Project {title: $p_title}), (pub:Publication {title: $pub_title})
            MERGE (p)-[:HAS_PUBLICATION]->(pub)
        """, p_title=publication["project"], pub_title=publication["title"])

    # الباحث ↔ المنشورات
    for publication in publications_col.find():
        for author_name in publication["authors"]:
            tx.run("""
                MATCH (r:Researcher {name: $r_name}), (pub:Publication {title: $pub_title})
                MERGE (r)-[:AUTHORED]->(pub)
            """, r_name=author_name, pub_title=publication["title"])

    # علاقات CO_AUTHOR بين الباحثين الذين شاركوا في نفس المنشورات
    for publication in publications_col.find():
        authors = publication["authors"]
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                tx.run("""
                    MATCH (a:Researcher {name: $a1}), (b:Researcher {name: $a2})
                    MERGE (a)-[:CO_AUTHOR]->(b)
                """, a1=authors[i], a2=authors[j])

    # علاقات TEAMMATE بين الباحثين في نفس المشروع
    for project in projects_col.find():
        participants = project["participants"]
        for i in range(len(participants)):
            for j in range(i + 1, len(participants)):
                tx.run("""
                    MATCH (a:Researcher {name: $a1}), (b:Researcher {name: $a2})
                    MERGE (a)-[:TEAMMATE]->(b)
                """, a1=participants[i], a2=participants[j])

# =========================
# تشغيل الإضافة
# =========================
with driver.session() as session:
    # إضافة الباحثين
    for r in researchers_col.find():
        session.write_transaction(create_researcher, r["name"], r["department"], r["interests"])
    print(f"تم إضافة {researchers_col.count_documents({})} باحثين إلى Neo4j!")

    # إضافة المشاريع
    for p in projects_col.find():
        session.write_transaction(create_project, p["title"])
    print(f"تم إضافة {projects_col.count_documents({})} مشاريع إلى Neo4j!")

    # إضافة المنشورات
    for pub in publications_col.find():
        session.write_transaction(create_publication, pub["title"])
    print(f"تم إضافة {publications_col.count_documents({})} منشورات إلى Neo4j!")

    # إضافة العلاقات
    session.write_transaction(create_relationships)
    print("تم إنشاء جميع العلاقات بين الباحثين، المشاريع، والمنشورات بنجاح!")

driver.close()
