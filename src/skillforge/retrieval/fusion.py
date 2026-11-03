"""Reciprocal Rank Fusion (RRF) for Multi-Channel Hybrid Retrieval."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple


class ReciprocalRankFusion:
    """Combines multiple independent ranked candidate lists using Reciprocal Rank Fusion.
    
    Formula: RRF(d) = SUM_c [ weight_c / (k + rank_c(d)) ]
    Default smoothing constant k = 60.0.
    """

    def __init__(self, k: float = 60.0, channel_weights: Optional[Dict[str, float]] = None):
        self.k = k
        self.weights = channel_weights or {
            "lexical": 1.0,
            "graph": 0.85,
            "technology": 0.75,
            "quality": 0.50,
            "feedback": 0.40
        }

    def fuse(
        self,
        channels: Dict[str, List[Tuple[str, float]]]
    ) -> List[Dict[str, Any]]:
        """Fuse candidate rankings from multiple channels into a single scored and ranked list.
        
        Args:
            channels: Dict mapping channel_name -> list of (skill_id, channel_score) tuples,
                      ordered from best to worst.
        
        Returns:
            List of fused dicts sorted by rrf_score descending.
        """
        fused_scores: Dict[str, float] = {}
        channel_ranks: Dict[str, Dict[str, int]] = {}
        channel_raw_scores: Dict[str, Dict[str, float]] = {}

        for ch_name, candidates in channels.items():
            ch_weight = self.weights.get(ch_name, 1.0)
            for rank_idx, (skill_id, raw_score) in enumerate(candidates, start=1):
                if skill_id not in fused_scores:
                    fused_scores[skill_id] = 0.0
                    channel_ranks[skill_id] = {}
                    channel_raw_scores[skill_id] = {}

                # Calculate RRF component
                rrf_component = ch_weight / (self.k + rank_idx)
                fused_scores[skill_id] += rrf_component
                channel_ranks[skill_id][ch_name] = rank_idx
                channel_raw_scores[skill_id][ch_name] = round(raw_score, 4)

        # Sort items by fused RRF score descending
        sorted_skills = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        # Normalize top score to 1.0 if any results exist
        max_score = sorted_skills[0][1] if sorted_skills else 1.0

        results = []
        for rank_idx, (skill_id, rrf_val) in enumerate(sorted_skills, start=1):
            normalized_score = round(rrf_val / max_score, 4) if max_score > 0 else 0.0
            
            # Generate signals
            signals = []
            ranks = channel_ranks[skill_id]
            if "lexical" in ranks:
                signals.append(f"Lexical rank #{ranks['lexical']}")
            if "graph" in ranks:
                signals.append(f"Graph cluster rank #{ranks['graph']}")
            if "technology" in ranks:
                signals.append(f"Tech stack match rank #{ranks['technology']}")
            if "feedback" in ranks:
                signals.append(f"Positive feedback boost rank #{ranks['feedback']}")

            results.append({
                "skill_id": skill_id,
                "final_rank": rank_idx,
                "rrf_score": round(rrf_val, 6),
                "normalized_score": normalized_score,
                "channel_ranks": ranks,
                "channel_raw_scores": channel_raw_scores[skill_id],
                "signals": signals
            })

        return results
