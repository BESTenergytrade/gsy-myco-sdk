from typing import Dict, List
import json

from gsy_framework.data_classes import BidOfferMatch
from gsy_framework.matching_algorithms import BaseMatchingAlgorithm, PayAsBidMatchingAlgorithm
from market_wrapper import PayAsBidMatchingAlgorithm as PaB

debug = False
use_simply = True


class BESTMatchingAlgorithm(BaseMatchingAlgorithm):
    """Perform BEST specific bid offer matching using pay as clear algorithm.
    The algorithm aggregates related offers/bids based on cluster i.e. zone
    Aggregated lists will be matched across zones iteratively with the best algorithm.
    """

    @classmethod
    def get_matches_recommendations(
            cls, matching_data: Dict[str, Dict]) -> List[BidOfferMatch.serializable_dict]:
        gsy_match = []
        simply_match = []
        for market_id, time_slot_data in matching_data.items():
            for time_slot, data in time_slot_data.items():
                bids_mapping = {bid["id"]: bid for bid in data.get("bids") or []}
                offers_mapping = {offer["id"]: offer for offer in data.get("offers") or []}

                if not (bids_mapping and offers_mapping):
                    continue

                # own Pay as Bid
                simply_match.extend(PaB.get_matches_recommendations(
                    {market_id: {time_slot: {
                        "bids": bids_mapping.values(),
                        "offers": offers_mapping.values()}}})
                )

                if debug or not use_simply:
                    # GSY integrated Pay as Bid for comparison
                    gsy_match.extend(PayAsBidMatchingAlgorithm.get_matches_recommendations(
                        {market_id: {time_slot: {
                            "bids": bids_mapping.values(),
                            "offers": offers_mapping.values()}}})
                    )

                if debug:
                    with open(f'PaB_{time_slot}_gsy.json', 'w') as f:
                        json.dump(gsy_match, f, indent=2)
                    with open(f'PaB_{time_slot}_simply.json', 'w') as f:
                        json.dump(simply_match, f, indent=2)

        if use_simply:
            return simply_match
        else:
            return gsy_match
