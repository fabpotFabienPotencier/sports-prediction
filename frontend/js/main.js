document.addEventListener('DOMContentLoaded', () => {
    let currentSport = 'soccer';
    const updateInterval = 60000; // 1 minute

    // Initialize the dashboard
    initializeDashboard();
    
    // Set up sport selection buttons
    document.querySelectorAll('.sport-btn').forEach(button => {
        button.addEventListener('click', () => {
            currentSport = button.dataset.sport;
            document.querySelectorAll('.sport-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            updateDashboard();
        });
    });

    async function initializeDashboard() {
        await updateDashboard();
        setInterval(updateDashboard, updateInterval);
    }

    async function updateDashboard() {
        try {
            const matches = await api.getLiveMatches(currentSport);
            updateMatchesDisplay(matches);
            updatePredictions(matches);
        } catch (error) {
            console.error('Error updating dashboard:', error);
            showError('Failed to update dashboard');
        }
    }

    function updateMatchesDisplay(matches) {
        const container = document.querySelector('.matches-container');
        container.innerHTML = matches.map(match => createMatchCard(match)).join('');
    }

    async function updatePredictions(matches) {
        const container = document.querySelector('.predictions-container');
        container.innerHTML = '';

        for (const match of matches) {
            try {
                const prediction = await api.getPrediction(
                    currentSport,
                    match.match_id,
                    'match_outcome'
                );
                container.appendChild(createPredictionCard(prediction));
            } catch (error) {
                console.error('Error updating prediction:', error);
            }
        }
    }

    function createMatchCard(match) {
        return `
            <div class="match-card">
                <div class="teams">
                    <span class="home-team">${match.home_team}</span>
                    <span class="score">${match.current_score}</span>
                    <span class="away-team">${match.away_team}</span>
                </div>
                <div class="match-time">${match.time}'</div>
            </div>
        `;
    }

    function createPredictionCard(prediction) {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        card.innerHTML = `
            <h3>${prediction.match_data.home_team} vs ${prediction.match_data.away_team}</h3>
            <p class="prediction">${prediction.prediction}</p>
            <p class="confidence">Confidence: ${(prediction.confidence * 100).toFixed(1)}%</p>
            <p class="timestamp">Updated: ${new Date(prediction.timestamp).toLocaleTimeString()}</p>
        `;
        return card;
    }

    function showError(message) {
        // Implement error display logic
        console.error(message);
    }
}); 