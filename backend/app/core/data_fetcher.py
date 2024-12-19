from typing import Dict, Any, List
import aiohttp
from app.config import get_settings
from app.utils.logger import get_logger
from fastapi_cache.decorator import cache

settings = get_settings()
logger = get_logger(__name__)

class SportDataFetcher:
    def __init__(self):
        self.base_url = "http://site.api.espn.com/apis/site/v2/sports"

    @cache(expire=60)
    async def get_live_match_data(self, sport: str, match_id: str) -> Dict[str, Any]:
        try:
            sport_path = self._get_sport_path(sport)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/{sport_path}/scoreboard") as response:
                    if response.status != 200:
                        logger.error(f"ESPN API error: {response.status}")
                        return self._get_fallback_data()
                    
                    data = await response.json()
                    return self._process_espn_data(sport, data)
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return self._get_fallback_data()

    def _get_sport_path(self, sport: str) -> str:
        sport_paths = {
            "soccer": "soccer/all",
            "basketball": "basketball/nba",
            "tennis": "tennis"
        }
        return sport_paths.get(sport, "soccer/all")

    def _process_espn_data(self, sport: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not data.get('events'):
                return self._get_fallback_data()

            # Get first live event
            event = next((e for e in data['events'] if e['status']['type']['state'] == 'in'), None)
            if not event:
                return self._get_fallback_data()

            if sport == "soccer":
                return self._process_soccer_espn(event)
            elif sport == "basketball":
                return self._process_basketball_espn(event)
            elif sport == "tennis":
                return self._process_tennis_espn(event)

        except Exception as e:
            logger.error(f"Error processing ESPN data: {str(e)}")
            return self._get_fallback_data()

    def _process_soccer_espn(self, event: Dict[str, Any]) -> Dict[str, Any]:
        competitions = event['competitions'][0]
        competitors = competitions['competitors']
        
        return {
            'match_id': event['id'],
            'home_team': competitors[0]['team']['name'],
            'away_team': competitors[1]['team']['name'],
            'score': f"{competitors[0]['score']} - {competitors[1]['score']}",
            'time': event['status']['displayClock'],
            'possession': {'home': 50, 'away': 50},  # ESPN doesn't provide possession
            'shots_on_target': {
                'home': competitors[0].get('statistics', [{'shotsOnTarget': 0}])[0].get('shotsOnTarget', 0),
                'away': competitors[1].get('statistics', [{'shotsOnTarget': 0}])[0].get('shotsOnTarget', 0)
            }
        }

    def _process_basketball_espn(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process basketball data from ESPN"""
        competitions = event['competitions'][0]
        competitors = competitions['competitors']
        
        return {
            'match_id': event['id'],
            'home_team': competitors[0]['team']['name'],
            'away_team': competitors[1]['team']['name'],
            'score': f"{competitors[0]['score']} - {competitors[1]['score']}",
            'time': event['status']['displayClock'],
            'period': event['status']['period'],
            'statistics': {
                'home': {
                    'field_goals': competitors[0].get('statistics', [{'fieldGoalsMade': 0}])[0].get('fieldGoalsMade', 0),
                    'rebounds': competitors[0].get('statistics', [{'rebounds': 0}])[0].get('rebounds', 0),
                    'assists': competitors[0].get('statistics', [{'assists': 0}])[0].get('assists', 0)
                },
                'away': {
                    'field_goals': competitors[1].get('statistics', [{'fieldGoalsMade': 0}])[0].get('fieldGoalsMade', 0),
                    'rebounds': competitors[1].get('statistics', [{'rebounds': 0}])[0].get('rebounds', 0),
                    'assists': competitors[1].get('statistics', [{'assists': 0}])[0].get('assists', 0)
                }
            }
        }

    def _process_tennis_espn(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process tennis data from ESPN"""
        competitions = event['competitions'][0]
        competitors = competitions['competitors']
        
        return {
            'match_id': event['id'],
            'home_player': competitors[0]['athlete']['displayName'],
            'away_player': competitors[1]['athlete']['displayName'],
            'score': self._format_tennis_score(competitors),
            'time': event['status']['displayClock'],
            'set': event['status'].get('period', 1),
            'statistics': {
                'home': {
                    'aces': competitors[0].get('statistics', [{'aces': 0}])[0].get('aces', 0),
                    'double_faults': competitors[0].get('statistics', [{'doubleFaults': 0}])[0].get('doubleFaults', 0),
                    'first_serve_pct': competitors[0].get('statistics', [{'firstServePercent': 0}])[0].get('firstServePercent', 0)
                },
                'away': {
                    'aces': competitors[1].get('statistics', [{'aces': 0}])[0].get('aces', 0),
                    'double_faults': competitors[1].get('statistics', [{'doubleFaults': 0}])[0].get('doubleFaults', 0),
                    'first_serve_pct': competitors[1].get('statistics', [{'firstServePercent': 0}])[0].get('firstServePercent', 0)
                }
            }
        }

    def _format_tennis_score(self, competitors: List[Dict[str, Any]]) -> str:
        """Format tennis score from ESPN data"""
        try:
            home_score = competitors[0].get('score', '0')
            away_score = competitors[1].get('score', '0')
            
            # Get set scores
            home_sets = competitors[0].get('linescores', [])
            away_sets = competitors[1].get('linescores', [])
            
            set_scores = []
            for i in range(len(home_sets)):
                set_scores.append(f"{home_sets[i].get('value', '0')}-{away_sets[i].get('value', '0')}")
            
            return f"{home_score}-{away_score} ({', '.join(set_scores)})"
        except Exception as e:
            logger.error(f"Error formatting tennis score: {str(e)}")
            return "0-0"

    def _get_fallback_data(self) -> Dict[str, Any]:
        """Fallback data when API fails"""
        return {
            'match_id': 'test_match',
            'home_team': 'Test Home Team',
            'away_team': 'Test Away Team',
            'score': '2 - 1',
            'time': '65',
            'possession': {'home': 60, 'away': 40},
            'shots_on_target': {
                'home': 5,
                'away': 3
            }
        }

    def _process_match_data(self, sport: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and standardize raw API data based on sport
        """
        if sport == "soccer":
            return self._process_soccer_data(raw_data)
        elif sport == "basketball":
            return self._process_basketball_data(raw_data)
        elif sport == "tennis":
            return self._process_tennis_data(raw_data)
        else:
            raise ValueError(f"Unsupported sport: {sport}")
            
    def _process_soccer_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process soccer-specific data
        """
        match_data = raw_data['response'][0]
        return {
            'home_team': match_data['teams']['home']['name'],
            'away_team': match_data['teams']['away']['name'],
            'score': f"{match_data['goals']['home']} - {match_data['goals']['away']}",
            'time': match_data['fixture']['status']['elapsed'],
            'possession': match_data['statistics'][0]['possession'],
            'shots_on_target': {
                'home': match_data['statistics'][0]['shots']['on'],
                'away': match_data['statistics'][1]['shots']['on']
            }
        }

    # Similar methods for processing basketball and tennis data... 