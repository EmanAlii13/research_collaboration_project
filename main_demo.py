# main_demo_fixed.py
# Research Collaboration Management System
# MongoDB + Neo4j + Redis

from pymongo import MongoClient
from neo4j import GraphDatabase
import redis
from dotenv import load_dotenv
import os
import json
from bson import ObjectId
import time

load_dotenv()

# -----------------------------
# Database configurations
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["research_db"]
researchers_col = mongo_db["researchers"]
projects_col = mongo_db["projects"]
publications_col = mongo_db["publications"]

NEO_URI = os.getenv("NEO4J_URI")
NEO_USER = os.getenv("NEO4J_USERNAME")
NEO_PASS = os.getenv("NEO4J_PASSWORD")
neo_driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASS = os.getenv("REDIS_PASSWORD")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)

# -----------------------------
# Redis caching function with timing
# -----------------------------
def cache_researcher(name):
    start_time = time.perf_counter()

    # Check in Redis first
    data = r.get(f"researcher:{name}")
    if data:
        elapsed = time.perf_counter() - start_time
        print(f"✅ Data fetched from Redis (Cache) in {elapsed:.6f} seconds")
        return json.loads(data)

    # Fetch from MongoDB
    researcher = researchers_col.find_one({"name": name})
    if not researcher:
        elapsed = time.perf_counter() - start_time
        print(f"No researcher found (MongoDB checked in {elapsed:.6f} seconds)")
        return None

    # Convert ObjectId to string for JSON
    if "_id" in researcher:
        researcher["_id"] = str(researcher["_id"])

    # Store in Redis for 60 seconds
    r.set(f"researcher:{name}", json.dumps(researcher), ex=60)
    elapsed = time.perf_counter() - start_time
    print(f"✅ Data fetched from MongoDB and stored in Redis in {elapsed:.6f} seconds")
    return researcher

# -----------------------------
# MongoDB functions
# -----------------------------
def show_researcher_by_name(name):
    r_data = cache_researcher(name)
    if not r_data:
        print(f"No researcher found with name '{name}'")
        return

    print(f"\nName: {r_data.get('name','')}, Department: {r_data.get('department','')}, Interests: {', '.join(r_data.get('interests',[]))}")
    
    # Projects of the researcher
    projects = projects_col.find({"participants": name})
    print("Projects:")
    for p in projects:
        print(f" - {p.get('title')}")

def show_project_by_title(title):
    p = projects_col.find_one({"title": title})
    if not p:
        print(f"No project found with title '{title}'")
        return

    print(f"\nTitle: {p.get('title')}, Description: {p.get('description','')}")
    participants = p.get('participants', [])
    print("Participants:")
    for r_name in participants:
        print(f" - {r_name}")

    # -----------------------------
    # جمع العلاقات لكل نوع مرة واحدة
    # -----------------------------
    relations_summary = {}  # relation_type -> set of researcher names
    with neo_driver.session() as session:
        for relation_type in ["CO_AUTHOR", "TEAMMATE"]:
            q = f"""
            MATCH (r:Researcher)-[rel:{relation_type}]->(b:Researcher)
            WHERE r.name IN $participants AND b.name IN $participants
            RETURN collect(DISTINCT r.name) + collect(DISTINCT b.name) AS names
            """
            result = session.run(q, participants=participants)
            for rec in result:
                names = set(rec["names"])
                if names:
                    relations_summary[relation_type] = names

    # -----------------------------
    # طباعة العلاقات المختصرة
    # -----------------------------
    if relations_summary:
        print("\nRelationships in this project:")
        for rel_type, names in relations_summary.items():
            print(f" {rel_type}: {', '.join(sorted(names))}")

# -----------------------------
# Add functions
# -----------------------------
def add_researcher(name, department, interests):
    researchers_col.insert_one({"name": name,"department": department,"interests": interests})
    with neo_driver.session() as session:
        session.write_transaction(lambda tx: tx.run(
            "MERGE (r:Researcher {name:$name}) SET r.department=$dept", name=name, dept=department))
    print(f"Researcher '{name}' added successfully!")

def add_project(title, description, participants):
    projects_col.insert_one({"title": title,"description": description,"participants": participants})
    with neo_driver.session() as session:
        session.write_transaction(lambda tx: tx.run("MERGE (p:Project {title:$title})", title=title))
        for r_name in participants:
            session.write_transaction(lambda tx: tx.run("""
                MATCH (r:Researcher {name:$r_name})
                MATCH (p:Project {title:$title})
                MERGE (r)-[:WORKS_ON]->(p)
            """, r_name=r_name, title=title))
    print(f"Project '{title}' added successfully!")

# -----------------------------
# Analytics functions
# -----------------------------
def show_analytics():
    cache_key = "analytics_top_researchers"
    cached = r.get(cache_key)
    if cached:
        print("\n✅ Analytics fetched from Redis cache:")
        print(json.loads(cached))
        return

    with neo_driver.session() as session:
        print("\n--- Top Researchers by Projects ---")
        query_projects = """
        MATCH (r:Researcher)-[:WORKS_ON]->(p:Project)
        RETURN r.name AS name, count(DISTINCT p) AS projects
        ORDER BY projects DESC LIMIT 5
        """
        top_proj = []
        for rec in session.run(query_projects):
            top_proj.append(f"{rec['name']}: {rec['projects']} projects")
        print("\n".join(top_proj))

        print("\n--- Top Researchers by Publications ---")
        query_pubs = """
        MATCH (r:Researcher)-[:AUTHORED]->(pub:Publication)
        RETURN r.name AS name, count(pub) AS publications
        ORDER BY publications DESC LIMIT 5
        """
        top_pub = []
        for rec in session.run(query_pubs):
            top_pub.append(f"{rec['name']}: {rec['publications']} publications")
        print("\n".join(top_pub))

        print("\n--- Most Collaborative Pairs (Co-Authors) ---")
        query_collab = """
        MATCH (a:Researcher)-[:CO_AUTHOR]->(b:Researcher)
        RETURN a.name AS researcher1, b.name AS researcher2, count(*) AS collaborations
        ORDER BY collaborations DESC LIMIT 5
        """
        top_collab = []
        for rec in session.run(query_collab):
            top_collab.append(f"{rec['researcher1']} & {rec['researcher2']}: {rec['collaborations']} collaborations")
        print("\n".join(top_collab))

        # Cache the analytics for 60 seconds
        r.set(cache_key, json.dumps({"TopProjects": top_proj, "TopPublications": top_pub, "TopCollaborations": top_collab}), ex=60)
        print("\n✅ Analytics stored in Redis cache for 60 seconds")

# -----------------------------
# Interactive menu
# -----------------------------
def main_menu():
    while True:
        print("\n--- Research Collaboration System ---")
        print("1. Show All Researchers")
        print("2. Show All Projects")
        print("3. Show All Publications")
        print("4. Add Researcher")
        print("5. Add Project")
        print("6. Show Analytics (Neo4j)")
        print("7. Show Researcher by Name")
        print("8. Show Project by Title")
        print("0. Exit")
        choice = input("Select an option: ")

        if choice=="1":
            for r in researchers_col.find():
                print(f"Name: {r.get('name')}, Dept: {r.get('department')}, Interests: {', '.join(r.get('interests',[]))}")
        elif choice=="2":
            for p in projects_col.find():
                print(f"Title: {p.get('title')}, Desc: {p.get('description','')}, Participants: {', '.join(p.get('participants',[]))}")
        elif choice=="3":
            for pub in publications_col.find():
                print(f"Title: {pub.get('title')}, Authors: {', '.join(pub.get('authors',[]))}, Project: {pub.get('project')}")
        elif choice=="4":
            name = input("Researcher Name: ")
            dept = input("Department: ")
            interests = input("Interests (comma separated): ").split(",")
            add_researcher(name.strip(), dept.strip(), [i.strip() for i in interests])
        elif choice=="5":
            title = input("Project Title: ")
            desc = input("Project Description: ")
            participants = input("Participants (comma separated names): ").split(",")
            add_project(title.strip(), desc.strip(), [p.strip() for p in participants])
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
