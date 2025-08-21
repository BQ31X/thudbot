#!/usr/bin/env python3
"""
Dataset Validation Tests for Thudbot Hint System
Validates the revised dataset with new metadata fields and constraint compliance
"""

import pandas as pd
import os
from typing import Dict, List, Tuple, Set
from pathlib import Path
from app import run_hint_request

class DatasetValidator:
    """Validate dataset structure and content quality"""
    
    def __init__(self, csv_path: str = "data/Thudbot_Hint_Data_1.csv"):
        self.csv_path = csv_path
        self.df = None
        self.validation_results = {}
        
    def load_dataset(self) -> bool:
        """Load and validate dataset file"""
        try:
            if not Path(self.csv_path).exists():
                print(f"❌ Dataset file not found: {self.csv_path}")
                return False
                
            self.df = pd.read_csv(self.csv_path)
            print(f"✅ Loaded dataset: {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def validate_structure(self) -> Dict[str, bool]:
        """Validate dataset structure and required columns"""
        if self.df is None:
            return {"loaded": False}
        
        # Expected columns based on CSV structure
        required_columns = [
            "question_id", "puzzle_id", "category", "question", "hint_level", 
            "hint_text", "narrative_context", "planet", "location", "puzzle_name",
            "character", "response_must_mention", "response_must_not_mention", 
            "speaker", "tags", "tone", "answer_keywords"
        ]
        
        results = {}
        
        # Check required columns
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        results["all_required_columns"] = len(missing_columns) == 0
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
        
        # Check for data completeness
        results["no_empty_questions"] = self.df["question"].notna().all()
        results["no_empty_hints"] = self.df["hint_text"].notna().all()
        results["valid_hint_levels"] = self.df["hint_level"].isin([1, 2, 3, 4, 5]).all()
        
        # Check for duplicates
        results["no_duplicate_question_ids"] = not self.df["question_id"].duplicated().any()
        
        # Validate categorical data
        valid_categories = ["Meta", "Navigation", "Mechanics", "Inventory", "Character", "Puzzle"]
        results["valid_categories"] = self.df["category"].isin(valid_categories + [""]).all()
        
        self.validation_results.update(results)
        return results
    
    def validate_metadata_constraints(self) -> Dict[str, List[Dict]]:
        """Validate response_must_mention and response_must_not_mention constraints"""
        if self.df is None:
            return {}
        
        constraint_violations = []
        
        for idx, row in self.df.iterrows():
            question = row["question"]
            must_mention = str(row["response_must_mention"]) if pd.notna(row["response_must_mention"]) else ""
            must_not_mention = str(row["response_must_not_mention"]) if pd.notna(row["response_must_not_mention"]) else ""
            
            # Skip if no constraints
            if not must_mention and not must_not_mention:
                continue
            
            try:
                # Get actual response from system
                response = run_hint_request(question)
                response_lower = response.lower()
                
                violations = []
                
                # Check must_mention constraints
                if must_mention:
                    must_mention_terms = [term.strip().lower() for term in must_mention.split(",")]
                    for term in must_mention_terms:
                        if term and term not in response_lower:
                            violations.append(f"Missing required term: '{term}'")
                
                # Check must_not_mention constraints  
                if must_not_mention:
                    must_not_mention_terms = [term.strip().lower() for term in must_not_mention.split(",")]
                    for term in must_not_mention_terms:
                        if term and term in response_lower:
                            violations.append(f"Contains forbidden term: '{term}'")
                
                if violations:
                    constraint_violations.append({
                        "question_id": row["question_id"],
                        "question": question,
                        "violations": violations,
                        "response": response[:100] + "..." if len(response) > 100 else response
                    })
                    
            except Exception as e:
                constraint_violations.append({
                    "question_id": row["question_id"],
                    "question": question,
                    "violations": [f"Error testing constraints: {e}"],
                    "response": None
                })
        
        return {"constraint_violations": constraint_violations}
    
    def validate_hint_progression(self) -> Dict[str, List[Dict]]:
        """Validate that hint levels progress logically for same puzzle"""
        if self.df is None:
            return {}
        
        progression_issues = []
        
        # Group by puzzle_id to check progression
        for puzzle_id, group in self.df.groupby("puzzle_id"):
            if len(group) <= 1:
                continue  # Skip single-hint puzzles
            
            # Sort by hint level
            sorted_group = group.sort_values("hint_level")
            
            # Check that hint levels are sequential
            expected_levels = list(range(1, len(sorted_group) + 1))
            actual_levels = sorted_group["hint_level"].tolist()
            
            if actual_levels != expected_levels:
                progression_issues.append({
                    "puzzle_id": puzzle_id,
                    "expected_levels": expected_levels,
                    "actual_levels": actual_levels,
                    "questions": sorted_group["question"].tolist()
                })
        
        return {"progression_issues": progression_issues}
    
    def validate_content_quality(self) -> Dict[str, any]:
        """Validate content quality metrics"""
        if self.df is None:
            return {}
        
        quality_metrics = {}
        
        # Check hint text length distribution
        hint_lengths = self.df["hint_text"].str.len()
        quality_metrics["avg_hint_length"] = hint_lengths.mean()
        quality_metrics["min_hint_length"] = hint_lengths.min()
        quality_metrics["max_hint_length"] = hint_lengths.max()
        quality_metrics["short_hints"] = (hint_lengths < 20).sum()  # Very short hints
        quality_metrics["long_hints"] = (hint_lengths > 200).sum()  # Very long hints
        
        # Check question length distribution
        question_lengths = self.df["question"].str.len()
        quality_metrics["avg_question_length"] = question_lengths.mean()
        
        # Check for common quality issues
        quality_metrics["questions_with_typos"] = self.df["question"].str.contains(
            r"\b(teh|hte|adn|nad|taht|tha)\b", case=False, regex=True
        ).sum()
        
        # Check character distribution
        quality_metrics["character_distribution"] = self.df["character"].value_counts().to_dict()
        
        # Check category distribution
        quality_metrics["category_distribution"] = self.df["category"].value_counts().to_dict()
        
        return quality_metrics
    
    def run_full_validation(self) -> Dict[str, any]:
        """Run complete dataset validation"""
        print("🧪 DATASET VALIDATION TEST BATTERY")
        print("=" * 60)
        
        if not self.load_dataset():
            return {"success": False, "error": "Failed to load dataset"}
        
        print("\n🔧 Validating dataset structure...")
        structure_results = self.validate_structure()
        
        print("\n📋 Validating metadata constraints...")
        constraint_results = self.validate_metadata_constraints()
        
        print("\n📈 Validating hint progression...")
        progression_results = self.validate_hint_progression()
        
        print("\n✨ Validating content quality...")
        quality_results = self.validate_content_quality()
        
        # Combine all results
        full_results = {
            "structure": structure_results,
            "constraints": constraint_results,
            "progression": progression_results,
            "quality": quality_results,
            "dataset_stats": {
                "total_rows": len(self.df),
                "total_columns": len(self.df.columns),
                "unique_puzzles": self.df["puzzle_id"].nunique(),
                "unique_questions": self.df["question_id"].nunique()
            }
        }
        
        # Generate summary
        self._print_validation_summary(full_results)
        
        return full_results
    
    def _print_validation_summary(self, results: Dict[str, any]):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 DATASET VALIDATION SUMMARY")
        print("=" * 60)
        
        # Structure validation
        structure = results["structure"]
        structure_passed = sum(structure.values())
        structure_total = len(structure)
        print(f"📋 Structure: {structure_passed}/{structure_total} checks passed")
        
        for check, passed in structure.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        # Constraint validation
        constraint_violations = len(results["constraints"].get("constraint_violations", []))
        print(f"\n🔒 Constraints: {constraint_violations} violations found")
        
        if constraint_violations > 0:
            print("   ⚠️  Review constraint violations in detailed output")
        
        # Progression validation
        progression_issues = len(results["progression"].get("progression_issues", []))
        print(f"\n📈 Progression: {progression_issues} issues found")
        
        # Quality metrics
        quality = results["quality"]
        print(f"\n✨ Quality Metrics:")
        print(f"   Average hint length: {quality.get('avg_hint_length', 0):.1f} chars")
        print(f"   Short hints (<20 chars): {quality.get('short_hints', 0)}")
        print(f"   Long hints (>200 chars): {quality.get('long_hints', 0)}")
        print(f"   Potential typos: {quality.get('questions_with_typos', 0)}")
        
        # Dataset stats
        stats = results["dataset_stats"]
        print(f"\n📊 Dataset Stats:")
        print(f"   Total questions: {stats['total_rows']}")
        print(f"   Unique puzzles: {stats['unique_puzzles']}")
        print(f"   Unique question IDs: {stats['unique_questions']}")
        
        # Overall assessment
        critical_issues = (
            not all(structure.values()) or 
            constraint_violations > 10 or 
            progression_issues > 5
        )
        
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES FOUND - Review before Demo Day")
        else:
            print(f"\n✅ DATASET VALIDATION PASSED - Ready for progressive hints")

def run_dataset_validation():
    """Main function to run dataset validation"""
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found - constraint validation will be skipped")
        print("   (Structure and quality validation will still run)")
    
    validator = DatasetValidator()
    results = validator.run_full_validation()
    
    return results

if __name__ == "__main__":
    run_dataset_validation()
