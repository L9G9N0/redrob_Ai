#!/usr/bin/env python3
"""
Comprehensive test suite for the Redrob AI Ranking System.
Covers unit, integration, validation, and performance tests.
"""

import os
import csv
import json
import unittest
import tempfile
from datetime import datetime
import time

# Import functions directly from rank.py
from rank import check_honeypots, score_candidate, generate_reasoning, is_local, is_tier1
from validate_submission import validate_submission

class TestHoneypots(unittest.TestCase):
    """Unit tests for honeypot (impossible profile) detection logic."""

    def test_valid_candidate(self):
        candidate = {
            "candidate_id": "CAND_0000001",
            "profile": {"years_of_experience": 5.0},
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 36},
                {"name": "Embeddings", "proficiency": "advanced", "duration_months": 24}
            ],
            "career_history": [
                {"company": "Google", "duration_months": 36, "start_date": "2023-01-01"}
            ]
        }
        self.assertFalse(check_honeypots(candidate))

    def test_expert_zero_months_honeypot(self):
        # Candidate has 3 expert skills with 0 months used
        candidate = {
            "candidate_id": "CAND_0000002",
            "profile": {"years_of_experience": 6.0},
            "skills": [
                {"name": "Embeddings", "proficiency": "expert", "duration_months": 0},
                {"name": "Vector Search", "proficiency": "expert", "duration_months": 0},
                {"name": "RAG", "proficiency": "expert", "duration_months": 0}
            ]
        }
        self.assertTrue(check_honeypots(candidate))

    def test_startup_tenure_honeypot(self):
        # Sarvam AI founded in late 2023. Start date 2021 is impossible.
        candidate = {
            "candidate_id": "CAND_0000003",
            "profile": {"years_of_experience": 8.0},
            "skills": [],
            "career_history": [
                {"company": "Sarvam AI", "duration_months": 40, "start_date": "2021-06-15"}
            ]
        }
        self.assertTrue(check_honeypots(candidate))

    def test_job_duration_exceeds_experience_honeypot(self):
        # Worked for 120 months (10 years) but total experience is listed as 3 years (36 months)
        candidate = {
            "candidate_id": "CAND_0000004",
            "profile": {"years_of_experience": 3.0},
            "skills": [],
            "career_history": [
                {"company": "Infosys", "duration_months": 120}
            ]
        }
        self.assertTrue(check_honeypots(candidate))


class TestScoring(unittest.TestCase):
    """Unit tests for individual feature scoring and availability multipliers."""

    def test_location_checks(self):
        self.assertTrue(is_local("Pune, Maharashtra"))
        self.assertTrue(is_local("Noida Sector 62"))
        self.assertTrue(is_local("Delhi NCR"))
        self.assertTrue(is_tier1("Mumbai"))
        self.assertTrue(is_tier1("Hyderabad"))
        self.assertFalse(is_local("Toronto"))

    def test_scoring_weights(self):
        # Highly matching profile
        c_good = {
            "candidate_id": "CAND_0000010",
            "profile": {
                "years_of_experience": 7.0,
                "current_title": "Senior ML Engineer",
                "location": "Pune, India",
                "country": "india"
            },
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 60, "endorsements": 10},
                {"name": "Pinecone", "proficiency": "advanced", "duration_months": 36, "endorsements": 20},
                {"name": "RAG", "proficiency": "advanced", "duration_months": 24, "endorsements": 15}
            ],
            "career_history": [
                {"company": "Pied Piper", "title": "ML Engineer", "duration_months": 48},
                {"company": "Swiggy", "title": "Backend Developer", "duration_months": 36}
            ],
            "redrob_signals": {
                "notice_period_days": 15,
                "expected_salary_range_inr_lpa": {"min": 25.0, "max": 40.0},
                "last_active_date": "2026-06-15",
                "recruiter_response_rate": 0.9,
                "willing_to_relocate": True
            }
        }
        
        # Poorly matching profile (Operations manager at TCS, lives in Toronto, won't relocate, notice 120 days)
        c_poor = {
            "candidate_id": "CAND_0000011",
            "profile": {
                "years_of_experience": 15.0,
                "current_title": "Operations Manager",
                "location": "Toronto",
                "country": "canada"
            },
            "skills": [
                {"name": "Excel", "proficiency": "expert", "duration_months": 120}
            ],
            "career_history": [
                {"company": "TCS", "title": "Operations Lead", "duration_months": 180}
            ],
            "redrob_signals": {
                "notice_period_days": 120,
                "expected_salary_range_inr_lpa": {"min": 80.0, "max": 100.0},
                "last_active_date": "2024-01-01",
                "recruiter_response_rate": 0.05,
                "willing_to_relocate": False
            }
        }
        
        score_good, _ = score_candidate(c_good)
        score_poor, _ = score_candidate(c_poor)
        
        self.assertGreater(score_good, 0.3)
        self.assertLess(score_poor, 0.02)
        self.assertGreater(score_good, score_poor * 10)


class TestIntegration(unittest.TestCase):
    """Integration testing: end-to-end dataset pipeline mock check."""

    def test_pipeline_execution(self):
        # Create a mock jsonl dataset with 105 candidates
        temp_dir = tempfile.TemporaryDirectory()
        mock_jsonl_path = os.path.join(temp_dir.name, "mock_candidates.jsonl")
        mock_csv_path = os.path.join(temp_dir.name, "team_test.csv")
        
        candidates = []
        # Add 100 standard candidates
        for i in range(100):
            candidates.append({
                "candidate_id": f"CAND_{i:07d}",
                "profile": {
                    "years_of_experience": 6.0,
                    "current_title": "AI Engineer" if i % 2 == 0 else "Software Engineer",
                    "location": "Pune" if i % 3 == 0 else "Mumbai",
                    "country": "india"
                },
                "skills": [
                    {"name": "Python", "proficiency": "advanced", "duration_months": 48},
                    {"name": "Vector Search", "proficiency": "intermediate", "duration_months": 24}
                ],
                "career_history": [
                    {"company": "Pied Piper", "duration_months": 48}
                ],
                "redrob_signals": {
                    "notice_period_days": 30,
                    "expected_salary_range_inr_lpa": {"min": 20, "max": 35},
                    "last_active_date": "2026-06-20",
                    "recruiter_response_rate": 0.8,
                    "willing_to_relocate": True
                }
            })
            
        # Add 5 honeypots that must be filtered out
        for i in range(100, 105):
            candidates.append({
                "candidate_id": f"CAND_{i:07d}",
                "profile": {
                    "years_of_experience": 2.0
                },
                "skills": [
                    {"name": "Pinecone", "proficiency": "expert", "duration_months": 0},
                    {"name": "FAISS", "proficiency": "expert", "duration_months": 0},
                    {"name": "RAG", "proficiency": "expert", "duration_months": 0}
                ],
                "career_history": [],
                "redrob_signals": {
                    "notice_period_days": 30,
                    "expected_salary_range_inr_lpa": {"min": 20, "max": 35},
                    "last_active_date": "2026-06-20",
                    "recruiter_response_rate": 0.8,
                    "willing_to_relocate": True
                }
            })
            
        with open(mock_jsonl_path, "w", encoding="utf-8") as f:
            for c in candidates:
                f.write(json.dumps(c) + "\n")
                
        # Run ranking logic command
        cmd = f"python3 rank.py --candidates {mock_jsonl_path} --out {mock_csv_path}"
        ret = os.system(cmd)
        self.assertEqual(ret, 0, "rank.py failed to execute.")
        
        # Verify CSV format and contents
        errors = validate_submission(mock_csv_path)
        self.assertEqual(len(errors), 0, f"Submission validation failed: {errors}")
        
        # Ensure no honeypots are in the CSV
        with open(mock_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row["candidate_id"]
                cid_num = int(cid.split("_")[1])
                self.assertLess(cid_num, 100, f"Honeypot candidate {cid} made it to the ranking list!")
                
        temp_dir.cleanup()


class TestPerformance(unittest.TestCase):
    """Performance test to benchmark candidate scoring speed."""

    def test_run_speed(self):
        # We simulate scoring 1000 candidates to project full dataset latency
        c_template = {
            "candidate_id": "CAND_0000001",
            "profile": {
                "years_of_experience": 6.5,
                "current_title": "Senior AI Systems Engineer",
                "location": "Noida, NCR",
                "country": "india"
            },
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 48},
                {"name": "Vector Search", "proficiency": "advanced", "duration_months": 36},
                {"name": "Pinecone", "proficiency": "advanced", "duration_months": 24}
            ],
            "career_history": [
                {"company": "Initech", "duration_months": 36},
                {"company": "Wipro", "duration_months": 24}
            ],
            "redrob_signals": {
                "notice_period_days": 30,
                "expected_salary_range_inr_lpa": {"min": 25, "max": 40},
                "last_active_date": "2026-06-20",
                "recruiter_response_rate": 0.85,
                "willing_to_relocate": True
            }
        }
        
        start_time = time.time()
        for i in range(5000):
            _ = score_candidate(c_template)
            _ = check_honeypots(c_template)
        elapsed = time.time() - start_time
        
        # Projected time for 100K profiles based on 5K sample
        projected_100k = elapsed * 20
        print(f"\n[Performance Benchmark] Scored 5,000 mock candidates in {elapsed:.3f} seconds.")
        print(f"[Performance Benchmark] Projected runtime for 100,000 candidates: {projected_100k:.3f} seconds.")
        
        self.assertLess(projected_100k, 120.0, "The ranking computation latency is too high to fit the 5-minute budget safely.")


if __name__ == "__main__":
    unittest.main()
