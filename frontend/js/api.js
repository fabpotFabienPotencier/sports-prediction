class SportsAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async getLiveMatches(sport) {
        try {
            const response = await fetch(`${this.baseUrl}/predict/${sport}/live`);
            if (!response.ok) throw new Error('Failed to fetch live matches');
            return await response.json();
        } catch (error) {
            console.error('Error fetching live matches:', error);
            throw error;
        }
    }

    async getPrediction(sport, matchId, predictionType) {
        try {
            const response = await fetch(`${this.baseUrl}/predict/${sport}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    match_id: matchId,
                    prediction_type: predictionType
                })
            });
            if (!response.ok) throw new Error('Failed to fetch prediction');
            return await response.json();
        } catch (error) {
            console.error('Error fetching prediction:', error);
            throw error;
        }
    }
}

const api = new SportsAPI(); 