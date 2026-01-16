# main_demo_fixed.py
# Research Collaboration Management System
# MongoDB (2 Accounts) + Neo4j + Redis

from pymongo import MongoClient
from neo4j import GraphDatabase
import redis
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

# -----------------------------
# MongoDB Account 1
# -----------------------------
MONGO_URI_1 = os.getenv("MONGO_URI_1")
client1 = MongoClient(MONGO_URI_1)
db1 = client1["research_db"]
researchers_col1 = db1["researchers"]
projects_col1 = db1["projects"]
publications_col1 = db1["publications"]

# -----------------------------
# MongoDB Account 2
# -----------------------------
MONGO_URI_2 = os.getenv("MONGO_URI_2")
client2 = MongoClient(MONGO_URI_2)
db2 = client2["research_db"]
researchers_col2 = db2["researchers"]
projects_col2 = db2["projects"]
publications_col2 = db2["publications"]

# -----------------------------
# Neo4j connection
# -----------------------------
NEO_URI = os.getenv("NEO4J_URI")
NEO_USER = os.getenv("NEO4J_USERNAME")
NEO_PASS = os.getenv("NEO4J_PASSWORD")
neo_driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))

# -----------------------------
# Redis connection
# -----------------------------
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASS = os.getenv("REDIS_PASSWORD")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)

# -----------------------------
# Caching function for researcher
# -----------------------------
def cache_researcher(name):
    start_time = time.perf_counter()
    data = r.get(f"researcher:{name}")
    if data:
        elapsed = time.perf_counter() - start_time
        print(f"✅ Data fetched from Redis in {elapsed:.6f} seconds")
        return json.loads(data)

    # Search in both MongoDB accounts
    researcher = researchers_col1.find_one({"name": name}) or researchers_col2.find_one({"name": name})
    if not researcher:
        elapsed = time.perf_counter() - start_time
        print(f"No researcher found (checked MongoDB in {elapsed:.6f} seconds)")
        return None

    if "_id" in researcher:
        researcher["_id"] = str(researcher["_id"])

    r.set(f"researcher:{name}", json.dumps(researcher), ex=60)
    elapsed = time.perf_counter() - start_time
    print(f"✅ Data fetched from MongoDB and cached in Redis in {elapsed:.6f} seconds")
    return researcher

# -----------------------------
# Show All Researchers
# -----------------------------
def show_all_researchers():
    print("\n--- Account 1 Researchers ---")
    for r_data in researchers_col1.find():
        print(f"{r_data['name']} - {r_data['department']}")

    print("\n--- Account 2 Researchers ---")
    for r_data in researchers_col2.find():
        print(f"{r_data['name']} - {r_data['department']}")

# -----------------------------
# Show All Projects
# -----------------------------
def show_all_projects():
    print("\n--- Account 1 Projects ---")
    for p in projects_col1.find():
        print(f"{p['title']} - Participants: {', '.join(p.get('participants',[]))}")

    print("\n--- Account 2 Projects ---")
    for p in projects_col2.find():
        print(f"{p['title']} - Participants: {', '.join(p.get('participants',[]))}")

# -----------------------------
# Show All Publications
# -----------------------------
def show_all_publications():
    print("\n--- Account 1 Publications ---")
    for pub in publications_col1.find():
        print(f"{pub['title']} - Authors: {', '.join(pub.get('authors',[]))} - Project: {pub.get('project')}")

    print("\n--- Account 2 Publications ---")
    for pub in publications_col2.find():
        print(f"{pub['title']} - Authors: {', '.join(pub.get('authors',[]))} - Project: {pub.get('project')}")

# -----------------------------
# Show Researcher by Name
# -----------------------------
def show_researcher_by_name(name):
    r_data = cache_researcher(name)
    if not r_data:
        print(f"No researcher found with name '{name}'")
        return
    print(f"\nName: {r_data.get('name','')}, Department: {r_data.get('department','')}, Interests: {', '.join(r_data.get('interests',[]))}")
    projects1 = projects_col1.find({"participants": name})
    projects2 = projects_col2.find({"participants": name})
    all_projects = list(projects1) + list(projects2)
    print("Projects:")
    for p in all_projects:
        print(f" - {p.get('title')}")

# -----------------------------
# Show Project by Title
# -----------------------------
def show_project_by_title(title):
    project = projects_col1.find_one({"title": title}) or projects_col2.find_one({"title": title})
    if not project:
        print(f"No project found with title '{title}'")
        return

    participants = project.get("participants", [])
    print(f"\nTitle: {project.get('title')}")
    print("Participants:", ", ".join(participants))

    # Relationships (Neo4j)
    relations = {}
    with neo_driver.session() as session:
        for i, r1 in enumerate(participants):
            for r2 in participants[i+1:]:
                q = """
                MATCH (a:Researcher {name:$r1})-[rel:WORKED_ON]->(b:Researcher {name:$r2})
                RETURN type(rel) AS relation
                """
                result = session.run(q, r1=r1, r2=r2)
                for rec in result:
                    rel_type = rec['relation']
                    if rel_type not in relations:
                        relations[rel_type] = set()
                    relations[rel_type].update([r1, r2])

    print("\nRelationships in this project:")
    for rel_type, names in relations.items():
        print(f" {rel_type}: {', '.join(names)}")

# -----------------------------
# Option 6: Analytics (Top Researchers by Projects)
# -----------------------------
def show_analytics():
    start_time = time.perf_counter()
    cache_key = "top_researchers_projects"
    cached_data = r.get(cache_key)
    if cached_data:
        analytics = json.loads(cached_data)
        elapsed = time.perf_counter() - start_time
        print(f"✅ Analytics fetched from Redis in {elapsed:.6f} seconds")
    else:
        analytics = []
        with neo_driver.session() as session:
            query = """
            MATCH (r:Researcher)-[:WORKED_ON]->(p:Project)
            RETURN r.name AS name, count(DISTINCT p) AS projects
            ORDER BY projects DESC LIMIT 5
            """
            for rec in session.run(query):
                analytics.append({"name": rec["name"], "projects": rec["projects"]})
        r.set(cache_key, json.dumps(analytics), ex=60)
        elapsed = time.perf_counter() - start_time
        print(f"✅ Analytics computed from Neo4j and stored in Redis in {elapsed:.6f} seconds")

    print("\n--- Top Researchers by Projects ---")
    for r_data in analytics:
        print(f"{r_data['name']}: {r_data['projects']} projects")

# -----------------------------
# Add Researcher (both accounts)
# -----------------------------
def add_researcher(name, department, interests):
    for col in [researchers_col1, researchers_col2]:
        col.insert_one({"name": name,"department": department,"interests": interests})
    with neo_driver.session() as session:
        session.execute_write(lambda tx: tx.run("MERGE (r:Researcher {name:$name}) SET r.department=$dept", name=name, dept=department))
    print(f"Researcher '{name}' added successfully to both accounts!")

# -----------------------------
# Add Project (both accounts)
# -----------------------------
def add_project(title, description, participants, publications=[]):
    for col, pub_col in [(projects_col1, publications_col1), (projects_col2, publications_col2)]:
        col.insert_one({"title": title,"description": description,"participants": participants})
        for pub_title in publications:
            if not pub_col.find_one({"title": pub_title}):
                pub_col.insert_one({"title": pub_title, "project": title, "authors": participants})

    with neo_driver.session() as session:
        session.execute_write(lambda tx: tx.run("MERGE (p:Project {title:$title})", title=title))
        for r_name in participants:
            session.execute_write(lambda tx: tx.run("""
                MATCH (r:Researcher {name:$r_name})
                MATCH (p:Project {title:$title})
                MERGE (r)-[:WORKED_ON]->(p)
            """, r_name=r_name, title=title))

    print(f"Project '{title}' added successfully to both accounts!")

# -----------------------------
# Interactive Menu
# -----------------------------
def main_menu():
    while True:
        print("\n--- Research Collaboration System ---")
        print("1. Show All Researchers")
        print("2. Show All Projects")
        print("3. Show All Publications")
        print("4. Add Researcher")
        print("5. Add Project")
        print("6. Show Analytics (Neo4j + Redis)")
        print("7. Show Researcher by Name")
        print("8. Show Project by Title")
        print("0. Exit")
        choice = input("Select an option: ")

        if choice=="1":
            show_all_researchers()
        elif choice=="2":
            show_all_projects()
        elif choice=="3":
            show_all_publications()
        elif choice=="4":
            name = input("Researcher Name: ")
            dept = input("Department: ")
            interests = [i.strip() for i in input("Interests (comma separated): ").split(",")]
            add_researcher(name.strip(), dept.strip(), interests)
        elif choice=="5":
            title = input("Project Title: ")
            desc = input("Project Description: ")
            participants = [p.strip() for p in input("Participants (comma separated): ").split(",")]
            pubs = [p.strip() for p in input("Publications (comma separated, optional): ").split(",") if p.strip()]
            add_project(title.strip(), desc.strip(), participants, pubs)
        elif choice=="6":
            show_analytics()
        elif choice=="7":
            name = input("Enter Researcher Name: ")
            show_researcher_by_name(name.strip())
        elif choice=="8":
            title = input("Enter Project Title: ")
            show_project_by_title(title.strip())
        elif choice=="0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again!")

if __name__=="__main__":
    main_menu()
