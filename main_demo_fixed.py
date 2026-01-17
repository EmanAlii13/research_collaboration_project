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
client1 = MongoClient(os.getenv("MONGO_URI_1"))
db1 = client1["research_db"]
researchers_col1 = db1["researchers"]
projects_col1 = db1["projects"]
publications_col1 = db1["publications"]

# -----------------------------
# MongoDB Account 2
# -----------------------------
client2 = MongoClient(os.getenv("MONGO_URI_2"))
db2 = client2["research_db"]
researchers_col2 = db2["researchers"]
projects_col2 = db2["projects"]
publications_col2 = db2["publications"]

# -----------------------------
# Neo4j connection
# -----------------------------
neo_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# -----------------------------
# Redis connection
# -----------------------------
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# -----------------------------
# Choose Cluster
# -----------------------------
def choose_cluster_collections():
    while True:
        print("\nChoose storage option:")
        print("1. Cluster 1")
        print("2. Cluster 2")
        print("3. Replication (Both Clusters)")
        print("0. Cancel")

        choice = input("Select option: ").strip()
        if choice == "1":
            return [(researchers_col1, projects_col1, publications_col1)]
        elif choice == "2":
            return [(researchers_col2, projects_col2, publications_col2)]
        elif choice == "3":
            return [
                (researchers_col1, projects_col1, publications_col1),
                (researchers_col2, projects_col2, publications_col2)
            ]
        elif choice == "0":
            print("❌ Operation cancelled. Nothing was saved.")
            return None
        else:
            print("⚠️ Invalid choice. Please select a valid option.")

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

    researcher = researchers_col1.find_one({"name": name}) or \
                 researchers_col2.find_one({"name": name})

    if not researcher:
        elapsed = time.perf_counter() - start_time
        print(f"No researcher found (checked MongoDB in {elapsed:.6f} seconds)")
        return None

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
        print(f"{p['title']} - Participants: {', '.join(p.get('participants', []))}")

    print("\n--- Account 2 Projects ---")
    for p in projects_col2.find():
        print(f"{p['title']} - Participants: {', '.join(p.get('participants', []))}")

# -----------------------------
# Show All Publications
# -----------------------------
def show_all_publications():
    print("\n--- Account 1 Publications ---")
    for pub in publications_col1.find():
        print(f"{pub['title']} - Authors: {', '.join(pub.get('authors', []))} - Project: {pub.get('project')}")

    print("\n--- Account 2 Publications ---")
    for pub in publications_col2.find():
        print(f"{pub['title']} - Authors: {', '.join(pub.get('authors', []))} - Project: {pub.get('project')}")

# -----------------------------
# Show Researcher by Name
# -----------------------------
def show_researcher_by_name(name):
    r_data = cache_researcher(name)
    if not r_data:
        print(f"No researcher found with name '{name}'")
        return

    print(f"\nName: {r_data.get('name','')}, Department: {r_data.get('department','')}, Interests: {', '.join(r_data.get('interests', []))}")
    projects1 = projects_col1.find({"participants": name})
    projects2 = projects_col2.find({"participants": name})
    all_projects = list(projects1) + list(projects2)
    print("Projects:")
    for p in all_projects:
        print(f" - {p.get('title')}")

# -----------------------------
# Show Project by Title (Updated)
# -----------------------------
def show_project_by_title(title):
    project = projects_col1.find_one({"title": title}) or projects_col2.find_one({"title": title})
    if not project:
        print(f"No project found with title '{title}'")
        return

    participants = project.get("participants", [])
    print(f"\nTitle: {project.get('title')}")
    print("Participants:", ", ".join(participants))

    # Relationships (Neo4j) - Updated to handle TEAMMATE, CO_AUTHOR, AUTHORED
    relations = {}
    with neo_driver.session() as session:
        for i, r1 in enumerate(participants):
            for r2 in participants[i+1:]:
                q = """
                MATCH (a:Researcher {name:$r1})-[rel]->(b:Researcher {name:$r2})
                WHERE type(rel) IN ['WORKED_ON','TEAMMATE','CO_AUTHOR','AUTHORED']
                RETURN type(rel) AS relation
                """
                for rec in session.run(q, r1=r1, r2=r2):
                    rel_type = rec['relation']
                    relations.setdefault(rel_type, set()).update([r1, r2])

    print("\nRelationships in this project:")
    if relations:
        for rel_type, names in relations.items():
            print(f" {rel_type}: {', '.join(names)}")
    else:
        print(" No relationships found between participants.")

# -----------------------------
# Option 6: Analytics (Top Researchers by Projects + collaborators)
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
            MATCH (r:Researcher)-[:WORKED_ON]->(p:Project)<-[:WORKED_ON]-(co:Researcher)
            WHERE r <> co
            RETURN r.name AS name, count(DISTINCT p) AS projects, count(DISTINCT co) AS collaborators
            ORDER BY projects DESC LIMIT 5
            """
            for rec in session.run(query):
                analytics.append({
                    "name": rec["name"],
                    "projects": rec["projects"],
                    "collaborators": rec["collaborators"]
                })
        r.set(cache_key, json.dumps(analytics), ex=60)
        elapsed = time.perf_counter() - start_time
        print(f"✅ Analytics computed from Neo4j and stored in Redis in {elapsed:.6f} seconds")

    print("\n--- Top Researchers by Projects ---")
    for r_data in analytics:
        print(f"{r_data['name']}: {r_data['projects']} projects, {r_data['collaborators']} collaborators")

# -----------------------------
# Add Researcher
# -----------------------------
def add_researcher(name, department, interests):
    targets = choose_cluster_collections()
    if targets is None:
        return

    for r_col, _, _ in targets:
        r_col.insert_one({"name": name, "department": department, "interests": interests})

    # Neo4j once
    with neo_driver.session() as session:
        session.execute_write(
            lambda tx: tx.run("MERGE (r:Researcher {name:$name}) SET r.department=$dept", name=name, dept=department)
        )

    print(f"✅ Researcher '{name}' added successfully!")

# -----------------------------
# Add Project
# -----------------------------
def add_project(title, description, participants, publications=[]):
    targets = choose_cluster_collections()
    if targets is None:
        return

    for _, p_col, pub_col in targets:
        p_col.insert_one({"title": title, "description": description, "participants": participants})

        for pub_title in publications:
            if not pub_col.find_one({"title": pub_title}):
                pub_col.insert_one({"title": pub_title, "project": title, "authors": participants})

    # Neo4j once
    with neo_driver.session() as session:
        session.execute_write(lambda tx: tx.run("MERGE (p:Project {title:$title})", title=title))
        for r_name in participants:
            session.execute_write(
                lambda tx: tx.run("""
                    MATCH (r:Researcher {name:$r})
                    MATCH (p:Project {title:$t})
                    MERGE (r)-[:WORKED_ON]->(p)
                """, r=r_name, t=title)
            )

    print(f"✅ Project '{title}' added successfully!")

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

        choice = input("Select an option: ").strip()

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

