from typing import Dict, List

from d3a_interface.data_classes import BidOfferMatch
from d3a_interface.matching_algorithms import BaseMatchingAlgorithm, PayAsBidMatchingAlgorithm


# TODO: Implement step 1 of the algorithm + add tests
class BESTMatchingAlgorithm(BaseMatchingAlgorithm):
    """Perform BEST specific bid offer matching using pay as clear algorithm.
    The algorithm aggregates related offers/bids based on cluster i.e. zone
    Aggregated lists will be matched across zones iteratively with the best algorithm.
    """

    @classmethod
    def get_matches_recommendations(
            cls, matching_data: Dict[str, Dict]) -> List[BidOfferMatch.serializable_dict]:
        recommendations = []
        for market_id, data in matching_data.items():
            bids_mapping = {bid["id"]: bid for bid in data.get("bids")}
            offers_mapping = {offer["id"]: offer for offer in data.get("offers")}

            if not (bids_mapping and offers_mapping):
                continue

            residual_recommendations = PayAsBidMatchingAlgorithm.get_matches_recommendations(
                    {market_id: {
                        "bids": list(bids_mapping.values()),
                        "offers": list(offers_mapping.values())}})
            recommendations.extend(residual_recommendations)

        return recommendations
