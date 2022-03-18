import logging
import os
from time import sleep
import json

from gsy_myco_sdk.matchers import RedisBaseMatcher
from gsy_myco_sdk.matchers.base_matcher import BaseMatcher
from gsy_myco_sdk.matching_algorithms import BESTMatchingAlgorithm

if os.environ["MYCO_CLIENT_RUN_ON_REDIS"] == "true":
    base_matcher = RedisBaseMatcher
else:
    base_matcher = BaseMatcher

debug = True


class MycoMatcherBest(base_matcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.matched = False
        # At which slot completion is the matching triggered in percent
        self.match_slot_at = 80

    def on_market_cycle(self, data):
        self.matched = False

    def on_tick(self, data):
        if not self.matched and int(data.get("slot_completion")[:-1]) >= self.match_slot_at:
            self.request_offers_bids(filters={})
            self.matched = True

    def on_offers_bids_response(self, data):
        matching_data = data.get("bids_offers")
        if not matching_data:
            return
        recommendations = BESTMatchingAlgorithm.get_matches_recommendations(
            matching_data)
        if debug:
            print(json.dumps(matching_data, indent=2))
            print("\n")
            print(json.dumps(recommendations, indent=2))

        if recommendations:
            logging.info("Submitting %s recommendations.", len(recommendations))
            self.submit_matches(recommendations)

    def on_finish(self, data):
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        logging.debug("Recommendation response: %s", data)

    def on_event_or_response(self, data):
        logging.debug("Event arrived %s", data)


matcher = MycoMatcherBest()

while not matcher.is_finished:
    sleep(0.5)
