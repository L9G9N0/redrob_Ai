#!/usr/bin/env python3
"""
Redrob AI Hiring Challenge candidate ranker.
Parses candidates.jsonl, scores each candidate based on technical and behavioral fit,
filters out honeypots/impossible profiles, and outputs the top 100 to a CSV file.
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime

# ----------------------------------------------------------------------
# Constants & Rules Definitions
# ----------------------------------------------------------------------

# Tier-1 Indian Cities list (based on JD preferences)
TIER1_CITIES = {
    "hyderabad", "mumbai", "bangalore", "bengaluru", 
    "chennai", "kolkata", "ahmedabad"
}

# Local/Hybrid regions (highly preferred)
LOCAL_REGIONS = {
    "pune", "noida", "greater noida", "delhi", "delhi ncr", 
    "gurgaon", "gurugram", "ghaziabad", "faridabad"
}

# Consulting/Services companies to penalize
CONSULTING_COMPANIES = {
    "tcs", "tata consultancy services", "infosys", "wipro", 
    "accenture", "cognizant", "capgemini", "tech mahindra", 
    "genpact", "mphasis", "cognizant technology solutions"
}

# Core AI infrastructure skills from JD
CORE_AI_SKILLS = {
    "embeddings", "vector search", "semantic search", "hybrid search",
    "pinecone", "weaviate", "qdrant", "milvus", "faiss", "elasticsearch",
    "opensearch", "ndcg", "mrr", "map", "sentence-transformers", "bge", "e5",
    "rag", "retrieval-augmented generation", "fine-tuning llms", "llm fine-tuning",
    "lora", "qlora", "peft", "learning to rank", "learning-to-rank", "xgboost",
    "lightgbm", "pytorch", "transformers", "nlp", "information retrieval"
}

# Adjacent engineering skills
ADJACENT_SKILLS = {
    "python", "sql", "spark", "kafka", "airflow", "gcp", "aws", 
    "docker", "kubernetes", "git", "data pipelines", "backend", "analytics"
}

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def normalize_str(s):
    """Normalize strings for matching."""
    if not s:
        return ""
    return s.strip().lower()

def is_local(location):
    """Check if location is local to Noida/Pune/Delhi NCR."""
    loc = normalize_str(location)
    for reg in LOCAL_REGIONS:
        if reg in loc:
            return True
    return False

def is_tier1(location):
    """Check if location is a Tier-1 Indian city."""
    loc = normalize_str(location)
    for city in TIER1_CITIES:
        if city in loc:
            return True
    return False

def check_honeypots(candidate):
    """
    Detect impossible profiles (honeypots) to prevent disqualification.
    Returns True if the candidate is a honeypot (invalid).
    """
    cid = candidate.get("candidate_id")
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    years_exp = profile.get("years_of_experience", 0)

    # Honeypot Check 1: Expert proficiency in skills with 0 months used
    expert_zero = [s for s in skills if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
    if len(expert_zero) >= 3:
        return True

    # Honeypot Check 2: Startup founding year mismatch
    # Sarvam AI and Krutrim were founded in 2023. Anyone working there before 2023
    # or for more than 36 months (as of mid-2026) has an impossible profile.
    for job in history:
        comp = job.get("company")
        start = job.get("start_date")
        dur = job.get("duration_months", 0)
        if comp in ["Sarvam AI", "Krutrim"]:
            if dur > 36:
                return True
            if start:
                try:
                    s_yr = int(start.split("-")[0])
                    if s_yr < 2023:
                        return True
                except (ValueError, IndexError):
                    pass

    # Honeypot Check 3: Job duration exceeds years of experience (impossible tenure)
    for job in history:
        dur = job.get("duration_months", 0)
        if dur > (years_exp * 12 + 6):
            return True

    # Honeypot Check 4: Modern framework duration exceeds the framework's actual existence
    # Pinecone, LoRA, Fine-tuning LLMs, Weights & Biases, and RAG are post-2020/2021 tech.
    # Anyone claiming >60 months (5 years) of experience in these is a honeypot.
    modern_frameworks = {"Pinecone", "LoRA", "Fine-tuning LLMs", "Weights & Biases", "RAG"}
    for s in skills:
        name = s.get("name")
        dur = s.get("duration_months", 0)
        if name in modern_frameworks and dur > 60:
            return True

    # Basic check: invalid experience
    if years_exp < 0:
        return True

    return False

# ----------------------------------------------------------------------
# Scoring Pipeline
# ----------------------------------------------------------------------

def score_candidate(c):
    """
    Calculate candidate score based on technical quality and availability factors.
    Returns (score, reasoning_data)
    """
    # 1. First parse profile elements
    profile = c.get("profile", {})
    years_exp = profile.get("years_of_experience", 0)
    current_title = normalize_str(profile.get("current_title", ""))
    summary = normalize_str(profile.get("summary", ""))
    headline = normalize_str(profile.get("headline", ""))
    location = normalize_str(profile.get("location", ""))
    country = normalize_str(profile.get("country", ""))
    
    signals = c.get("redrob_signals", {})
    notice_days = signals.get("notice_period_days", 0)
    expected_sal = signals.get("expected_salary_range_inr_lpa", {})
    sal_max = expected_sal.get("max", 0)
    sal_min = expected_sal.get("min", 0)
    
    # Track matching skills for reasoning
    matching_core_skills = []
    matching_adj_skills = []
    
    # A. Experience Years Scoring (target: 5-9 years)
    if 5.0 <= years_exp <= 9.0:
        s_exp = 1.0
    elif 4.0 <= years_exp < 5.0 or 9.0 < years_exp <= 12.0:
        s_exp = 0.8
    elif 3.0 <= years_exp < 4.0 or 12.0 < years_exp <= 15.0:
        s_exp = 0.5
    else:
        s_exp = 0.15

    # B. Title Alignment Score
    # We prefer "AI Engineer", "ML Engineer", "Search/Retrieval Engineer"
    s_title = 0.15
    title_flag = ""
    
    core_title_pat = re.compile(r"\b(ai|ml|machine learning|nlp|retrieval|search|recommender|ranking|computer vision|speech|audio)\b")
    eng_title_pat = re.compile(r"\b(engineer|developer|scientist|specialist)\b")
    disq_title_pat = re.compile(r"\b(manager|operations|hr|recruiter|sales|marketing|civil|mechanical|accountant|writer)\b")
    
    # Check current title
    if core_title_pat.search(current_title) and eng_title_pat.search(current_title):
        s_title = 1.0
        title_flag = "core_current"
    elif eng_title_pat.search(current_title):
        s_title = 0.6
        title_flag = "adj_current"
    
    # Check history titles
    history = c.get("career_history", [])
    has_past_core = False
    for job in history:
        t = normalize_str(job.get("title", ""))
        if core_title_pat.search(t) and eng_title_pat.search(t):
            has_past_core = True
            break
            
    if has_past_core:
        if s_title < 0.8:
            s_title = 0.8
            title_flag = "core_past"
            
    # Apply severe penalty for disqualified titles if no core experience
    if disq_title_pat.search(current_title) and not has_past_core:
        s_title = 0.05
        title_flag = "disqualified"

    # C. Skills Fit Scoring
    # Calculate score based on Core AI skills and Adjacent engineering skills
    s_skills = 0.0
    skills_list = c.get("skills", [])
    
    skill_points = 0
    max_possible_points = 150.0  # reference normalization factor
    
    for s in skills_list:
        name = normalize_str(s.get("name", ""))
        proficiency = s.get("proficiency", "beginner")
        endorsements = s.get("endorsements", 0)
        dur = s.get("duration_months", 0)
        
        # Proficiency multiplier
        prof_mult = {"beginner": 1.0, "intermediate": 2.0, "advanced": 3.0, "expert": 4.0}[proficiency]
        trust_mult = 1.0 + min(endorsements, 50) / 20.0  # Up to 3.5x trust weight for high endorsements
        dur_years = max(dur, 0) / 12.0
        
        if name in CORE_AI_SKILLS:
            skill_points += 8.0 * prof_mult * trust_mult * min(dur_years, 5.0)
            matching_core_skills.append(s.get("name"))
        elif name in ADJACENT_SKILLS:
            skill_points += 2.0 * prof_mult * trust_mult * min(dur_years, 3.0)
            matching_adj_skills.append(s.get("name"))
            
    s_skills = min(skill_points / max_possible_points, 1.0)
    
    # D. Company profile (Startup vs Consulting Services)
    s_company = 1.0
    all_consulting = True
    has_consulting = False
    consulting_name = ""
    
    total_jobs = len(history)
    for job in history:
        comp = normalize_str(job.get("company", ""))
        is_cons = False
        for cc in CONSULTING_COMPANIES:
            if cc in comp:
                is_cons = True
                has_consulting = True
                consulting_name = job.get("company")
                break
        if not is_cons:
            all_consulting = False
            
    if total_jobs > 0 and all_consulting:
        s_company = 0.15  # Heavy penalty for candidates with ONLY service/consulting background
    elif has_consulting:
        s_company = 0.7  # Small penalty for mixed services/product background
        
    # Check for job hop stability (average tenure)
    # Average job duration < 18 months gets a small penalty for "job-hopping"
    avg_tenure = 0
    if total_jobs > 0:
        total_months = sum(job.get("duration_months", 0) for job in history)
        avg_tenure = total_months / total_jobs
        if avg_tenure < 18:
            s_company *= 0.8

    # E. Education Tier Score
    s_edu = 0.4
    edu_list = c.get("education", [])
    for e in edu_list:
        tier = e.get("tier", "unknown")
        t_score = {"tier_1": 1.0, "tier_2": 0.8, "tier_3": 0.6, "tier_4": 0.4, "unknown": 0.4}[tier]
        if t_score > s_edu:
            s_edu = t_score

    # F. Compute Core Technical Quality Score
    q_tech = (0.30 * s_exp + 0.25 * s_title + 0.35 * s_skills + 0.08 * s_company + 0.02 * s_edu)

    # G. Multiplicative Constraints (Availability/Feasibility)
    # 1. Location Fit
    if is_local(location):
        m_loc = 1.0
    elif signals.get("willing_to_relocate", False) and is_tier1(location):
        m_loc = 0.95
    elif signals.get("willing_to_relocate", False):
        m_loc = 0.8
    else:
        # Not willing to relocate, and lives elsewhere
        if country == "india":
            m_loc = 0.2
        else:
            m_loc = 0.05  # Severe penalty for international non-relocators
            
    # 2. Notice Period Fit
    if notice_days <= 30:
        m_notice = 1.0
    elif notice_days <= 60:
        m_notice = 0.85
    elif notice_days <= 90:
        m_notice = 0.55
    else:
        m_notice = 0.1  # Severe startup penalty for notice periods > 90 days

    # 3. Expected Salary Fit (Series A startup constraints)
    m_sal = 1.0
    if sal_max > 60.0:
        m_sal = 0.4
    elif sal_max > 45.0:
        m_sal = 0.75
    elif sal_min > 50.0:
        m_sal = 0.3

    # 4. Platform Engagement Fit
    m_eng = 1.0
    # Last active decay
    last_act = signals.get("last_active_date", "")
    if last_act:
        try:
            la_dt = datetime.strptime(last_act, "%Y-%m-%d")
            # Anchor current date as 2026-06-24 (local time of execution)
            ref_dt = datetime(2026, 6, 24)
            elapsed_days = (ref_dt - la_dt).days
            if elapsed_days <= 30:
                act_decay = 1.0
            elif elapsed_days <= 90:
                act_decay = 0.9
            elif elapsed_days <= 180:
                act_decay = 0.6
            else:
                act_decay = 0.2
        except ValueError:
            act_decay = 0.5
    else:
        act_decay = 0.5
        
    resp_rate = signals.get("recruiter_response_rate", 0.5)
    resp_mult = 0.3 + 0.7 * resp_rate  # responsive modifier
    
    m_eng = act_decay * resp_mult

    # ------------------------------------------------------------------
    # Combine Everything to Final Score
    # ------------------------------------------------------------------
    final_score = q_tech * m_loc * m_notice * m_sal * m_eng
    
    # Package reason details for description generator
    reason_info = {
        "years_exp": years_exp,
        "title_flag": title_flag,
        "current_title": profile.get("current_title", ""),
        "core_skills": matching_core_skills[:3],
        "adj_skills": matching_adj_skills[:2],
        "notice_days": notice_days,
        "is_local": is_local(location),
        "relocate": signals.get("willing_to_relocate", False),
        "has_consulting": has_consulting,
        "all_consulting": all_consulting,
        "consulting_name": consulting_name,
        "resp_rate": resp_rate,
        "avg_tenure": avg_tenure
    }
    
    return final_score, reason_info

# ----------------------------------------------------------------------
# Reasoning Generator
# ----------------------------------------------------------------------

def generate_reasoning(rank, score, info):
    """
    Synthesize natural language justification for the candidate match
    dynamically without rigid templates, avoiding empty brackets.
    """
    years = info["years_exp"]
    title = info["current_title"] if info["current_title"] else "ML Professional"
    
    # 1. Core Identity & Company Profile (Module A)
    # Vary the opener based on candidate parameters to avoid duplicate phrasing
    intro_hash = hash(str(years) + title + str(rank)) % 3
    if intro_hash == 0:
        intro = f"{title} offering {years:.1f} years of experience"
    elif intro_hash == 1:
        intro = f"{years:.1f}-year engineering professional currently working as {title}"
    else:
        intro = f"Senior {title} with a {years:.1f}-year professional track record"
        
    # Append company type contexts
    if info["all_consulting"]:
        intro += f", transitioning from service firms (specifically {info['consulting_name']})"
    elif info["has_consulting"]:
        intro += f", carrying a mixed background from consulting ({info['consulting_name']}) and product development"
    else:
        intro += ", offering strong software development background at product companies"

    # 2. Technical Alignment (Module B)
    # Safe checks to prevent empty parentheses '()'
    core_skills_str = ", ".join(info["core_skills"]) if info["core_skills"] else ""
    adj_skills_str = ", ".join(info["adj_skills"]) if info["adj_skills"] else ""
    
    skills_hash = hash(core_skills_str + adj_skills_str + str(rank)) % 3
    
    if core_skills_str and adj_skills_str:
        if skills_hash == 0:
            tech = f". Demonstrates hands-on knowledge in {core_skills_str}, backed by solid adjacent depth in {adj_skills_str}."
        elif skills_hash == 1:
            tech = f". Experienced in core competencies like {core_skills_str} alongside adjacent engineering skills including {adj_skills_str}."
        else:
            tech = f". Technical toolkit spans core ML architectures like {core_skills_str} and backend infra tools such as {adj_skills_str}."
    elif core_skills_str:
        if skills_hash == 0:
            tech = f". Aligns directly with JD core skills, specifically showing depth in {core_skills_str}."
        else:
            tech = f". Technical background indicates specialized experience with {core_skills_str}."
    elif adj_skills_str:
        if skills_hash == 0:
            tech = f". Displays general engineering foundations in {adj_skills_str}, though direct vector-database experience is limited."
        else:
            tech = f". Toolkit centers on adjacent engineering systems like {adj_skills_str}, providing a strong transition baseline."
    else:
        tech = ". Offers general software development skills, though direct ML infrastructure exposure is limited."

    # 3. Constraints & Availability (Module C)
    notice = info["notice_days"]
    reloc = info["relocate"]
    local = info["is_local"]
    resp = info["resp_rate"]
    
    behavior_clauses = []
    
    # Notice Period
    if notice > 60:
        behavior_clauses.append(f"notice period of {notice} days is a concern")
    elif notice <= 30:
        behavior_clauses.append("availability is ideal (notice period under 30 days)")
        
    # Location
    if local:
        behavior_clauses.append("based locally in Pune/Noida")
    elif reloc:
        behavior_clauses.append("willing to relocate to Pune/Noida")
        
    # Responsiveness
    if resp < 0.3:
        behavior_clauses.append(f"historical response rate ({resp:.0%}) is low")
    elif resp >= 0.8:
        behavior_clauses.append("highly responsive on the platform")
        
    if behavior_clauses:
        behavior_hash = hash(str(rank) + str(score)) % 2
        if behavior_hash == 0:
            behavior = f". Operational notes: {', '.join(behavior_clauses)}."
        else:
            behavior = f". In terms of feasibility: {', '.join(behavior_clauses)}."
    else:
        behavior = "."

    # 4. Assemble and clean spacing/punctuation
    reasoning = f"{intro}{tech}{behavior}"
    reasoning = reasoning.replace("..", ".").replace(" .", ".").replace(" ,", ",").replace("  ", " ").strip()
    
    # Add rank-specific context prefixes
    if rank <= 10:
        reasoning = f"Top-tier recommendation: {reasoning}"
    elif rank > 80:
        reasoning = f"Borderline select: {reasoning}"
        
    return reasoning

# ----------------------------------------------------------------------
# Main Execution Pipeline
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob AI Hiring Challenge.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl file")
    parser.add_argument("--out", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    print(f"Reading candidates from {args.candidates}...")
    candidates_scored = []
    honeypot_count = 0
    total_count = 0

    with open(args.candidates, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_count += 1
            c = json.loads(line)
            
            # Step 1: Honeypot Filter
            if check_honeypots(c):
                honeypot_count += 1
                continue
                
            # Step 2: Scoring
            score, info = score_candidate(c)
            candidates_scored.append((c["candidate_id"], score, info))

    print(f"Total parsed: {total_count}")
    print(f"Honeypots filtered: {honeypot_count}")
    print(f"Candidates remaining for ranking: {len(candidates_scored)}")

    # Step 3: Sorting
    # To strictly satisfy tie-break validation, we must round the score to 4 decimal places
    # BEFORE sorting, because the CSV outputs 4 decimal places. If we round after sorting,
    # floating-point differences that round to the same value can violate candidate_id order.
    candidates_scored.sort(key=lambda x: (-round(x[1], 4), x[0]))

    # Step 4: Reasoning Generation & CSV Writing
    top_100 = candidates_scored[:100]
    
    print(f"Writing top 100 candidates to {args.out}...")
    with open(args.out, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for i, (cid, score, info) in enumerate(top_100):
            rank = i + 1
            reasoning = generate_reasoning(rank, score, info)
            # Use rounded score consistently
            formatted_score = f"{round(score, 4):.4f}"
            writer.writerow([cid, rank, formatted_score, reasoning])

    print("Ranking pipeline completed successfully.")

if __name__ == "__main__":
    main()
