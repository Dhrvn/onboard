# company_manager.py
# Handles everything multi-company:
# - Creating new company instances
# - Loading company-specific docs
# - Managing isolated knowledge bases per company

import os
import json
import shutil
from search import load_and_chunk_docs, build_smart_context

# ============================================================
# COMPANY REGISTRY
# Tracks all companies using OnboardIQ.
# Stored in companies/registry.json
# ============================================================

COMPANIES_DIR = "companies"
REGISTRY_FILE = os.path.join(COMPANIES_DIR, "registry.json")

# In-memory cache of loaded company chunks
# Key = company_id, Value = (chunks, chunk_sources)
company_cache = {}


def load_registry():
    """Load the list of all registered companies."""
    if not os.path.exists(REGISTRY_FILE):
        # Create default registry with Nexus Labs
        default = {
            "nexus_labs": {
                "id": "nexus_labs",
                "name": "Nexus Labs",
                "description": "Fintech startup building real-time credit risk infrastructure",
                "color": "#6366f1",
                "roles": ["Software Engineer", "Data Analyst", "Business Analyst"],
                "docs_path": os.path.join(COMPANIES_DIR, "nexus_labs"),
                "created_at": "2026-04-22"
            }
        }
        save_registry(default)
        return default

    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)


def save_registry(registry):
    """Save the company registry."""
    os.makedirs(COMPANIES_DIR, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


def get_company(company_id):
    """Get a specific company's details."""
    registry = load_registry()
    return registry.get(company_id)


def list_companies():
    """List all registered companies."""
    registry = load_registry()
    return list(registry.values())


def create_company(company_id, name, description, color, roles):
    """
    Register a new company.
    Creates a folder for their docs.
    """
    registry = load_registry()

    # Create docs folder for this company
    docs_path = os.path.join(COMPANIES_DIR, company_id)
    os.makedirs(docs_path, exist_ok=True)

    # Add to registry
    registry[company_id] = {
        "id": company_id,
        "name": name,
        "description": description,
        "color": color,
        "roles": roles,
        "docs_path": docs_path,
        "created_at": __import__('datetime').datetime.now().strftime("%Y-%m-%d")
    }

    save_registry(registry)
    print(f"✅ Company registered: {name} ({company_id})")
    return registry[company_id]


def save_company_doc(company_id, filename, content):
    """
    Save an uploaded document for a company.
    """
    company = get_company(company_id)
    if not company:
        raise ValueError(f"Company {company_id} not found")

    docs_path = company["docs_path"]
    os.makedirs(docs_path, exist_ok=True)

    filepath = os.path.join(docs_path, filename)
    with open(filepath, "w") as f:
        f.write(content)

    print(f"📄 Saved doc: {filename} for {company_id}")

    # Clear cache so new docs are picked up
    if company_id in company_cache:
        del company_cache[company_id]

    return filepath


def get_company_chunks(company_id):
    """
    Load and cache chunks for a specific company.
    Uses in-memory cache so we don't reload on every request.
    """
    # Return cached version if available
    if company_id in company_cache:
        return company_cache[company_id]

    company = get_company(company_id)
    if not company:
        raise ValueError(f"Company {company_id} not found")

    docs_path = company["docs_path"]

    # Check if docs exist
    if not os.path.exists(docs_path) or not os.listdir(docs_path):
        print(f"⚠️  No docs found for {company_id}")
        return [], []

    # Load and chunk docs
    chunks, chunk_sources = load_and_chunk_docs(docs_path)
    company_cache[company_id] = (chunks, chunk_sources)

    print(f"✅ Loaded {len(chunks)} chunks for {company_id}")
    return chunks, chunk_sources


def get_company_context(company_id, question, top_k=6):
    """
    Get relevant context for a question from a specific company's docs.
    """
    chunks, chunk_sources = get_company_chunks(company_id)

    if not chunks:
        return "No company documentation available yet."

    return build_smart_context(question, chunks, chunk_sources, top_k)


def company_id_from_name(name):
    """
    Convert company name to a valid ID.
    e.g. "Nexus Labs" -> "nexus_labs"
    """
    return name.lower().replace(" ", "_").replace("-", "_")