// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const target = document.querySelector(targetId);
        
        if (target) {
            // Mettre à jour l'onglet actif
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
            
            // Scroll avec offset pour le header fixe
            const headerOffset = 100;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    });
});

// Active navigation link on scroll
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

function highlightNav() {
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');

        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}

window.addEventListener('scroll', highlightNav);

// Animate stats on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.stat-card, .feature-card').forEach(card => {
    observer.observe(card);
});

// Add parallax effect to hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero-visual');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Create modal for details
function createModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.querySelector('.modal');
    if (existingModal) {
        existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <button class="modal-close">&times;</button>
            <h2 class="modal-title">${title}</h2>
            <div class="modal-body">${content}</div>
        </div>
    `;
    document.body.appendChild(modal);

    // Show modal with animation
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);

    // Close modal handlers
    const closeBtn = modal.querySelector('.modal-close');
    const overlay = modal.querySelector('.modal-overlay');
    
    const closeModal = () => {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    };

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);

    // Close on Escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

// Add click handlers to stat cards
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('click', function() {
        const label = this.querySelector('.stat-label').textContent;
        const value = this.querySelector('.stat-value').textContent;
        const icon = this.querySelector('.stat-icon').textContent;
        
        let content = '';
        switch(label) {
            case 'Classement Ligue 1':
                content = `
                    <p>L'Olympique Lyonnais occupe actuellement la <strong>1ère place</strong> du classement de la Ligue 1.</p>
                    <p>Cette position reflète les excellentes performances de l'équipe tout au long de la saison.</p>
                    <ul>
                        <li>Points totaux: 85</li>
                        <li>Matchs joués: 38</li>
                        <li>Victoires: 28</li>
                        <li>Nuls: 1</li>
                        <li>Défaites: 9</li>
                    </ul>
                `;
                break;
            case 'Matchs Analysés':
                content = `
                    <p>Un total de <strong>38 matchs</strong> ont été analysés en détail.</p>
                    <p>Chaque match a été examiné avec des métriques avancées incluant:</p>
                    <ul>
                        <li>Performance globale de l'équipe</li>
                        <li>Impact individuel des joueurs</li>
                        <li>Analyse tactique</li>
                        <li>Statistiques détaillées</li>
                    </ul>
                `;
                break;
            case 'Note Moyenne':
                content = `
                    <p>La note moyenne de <strong>4.8/5</strong> reflète la qualité constante des performances.</p>
                    <p>Cette note est calculée en fonction de:</p>
                    <ul>
                        <li>Résultat du match</li>
                        <li>Qualité du jeu</li>
                        <li>Performance individuelle</li>
                        <li>Impact tactique</li>
                    </ul>
                `;
                break;
            case 'Combos Optimales':
                content = `
                    <p><strong>15 combinaisons optimales</strong> de joueurs ont été identifiées.</p>
                    <p>Ces combos sont basées sur:</p>
                    <ul>
                        <li>Compatibilité entre joueurs</li>
                        <li>Résultats obtenus</li>
                        <li>Performance collective</li>
                        <li>Analyse statistique</li>
                    </ul>
                `;
                break;
            default:
                content = `<p>Détails pour: ${label}</p>`;
        }
        
        createModal(`${icon} ${label}`, content);
    });
});

// Add click handlers to feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function() {
        const title = this.querySelector('.feature-title').textContent;
        const description = this.querySelector('.feature-description').textContent;
        const icon = this.querySelector('.feature-icon').textContent;
        
        let content = `
            <p>${description}</p>
            <h3>Fonctionnalités détaillées:</h3>
        `;
        
        switch(title) {
            case 'Analyse de Performance':
                content += `
                    <ul>
                        <li>Métriques de performance en temps réel</li>
                        <li>Graphiques et visualisations interactives</li>
                        <li>Comparaison avec les matchs précédents</li>
                        <li>Analyse des tendances</li>
                        <li>Rapports détaillés par période</li>
                    </ul>
                `;
                break;
            case 'Impact des Joueurs':
                content += `
                    <ul>
                        <li>Score d'impact individuel pour chaque joueur</li>
                        <li>Contribution aux résultats de l'équipe</li>
                        <li>Analyse des performances clés</li>
                        <li>Comparaison entre joueurs</li>
                        <li>Statistiques détaillées par position</li>
                    </ul>
                `;
                break;
            case 'Combinaisons Optimales':
                content += `
                    <ul>
                        <li>Identification des meilleures combinaisons</li>
                        <li>Analyse de la compatibilité entre joueurs</li>
                        <li>Recommandations tactiques</li>
                        <li>Historique des performances par combo</li>
                        <li>Prédictions de succès</li>
                    </ul>
                `;
                break;
            case 'Gestion des Compositions':
                content += `
                    <ul>
                        <li>Analyse de l'impact des différentes compositions</li>
                        <li>Optimisation des choix tactiques</li>
                        <li>Comparaison des formations</li>
                        <li>Recommandations de composition</li>
                        <li>Historique des performances par formation</li>
                    </ul>
                `;
                break;
            case 'Statistiques Détaillées':
                content += `
                    <ul>
                        <li>Tableaux interactifs complets</li>
                        <li>Filtres et recherches avancées</li>
                        <li>Export des données</li>
                        <li>Comparaisons multi-critères</li>
                        <li>Visualisations personnalisables</li>
                    </ul>
                `;
                break;
            case 'Prédictions de Victoire':
                content += `
                    <ul>
                        <li>Modèles prédictifs basés sur l'historique</li>
                        <li>Probabilités de victoire calculées</li>
                        <li>Analyse des facteurs clés</li>
                        <li>Recommandations stratégiques</li>
                        <li>Suivi de la précision des prédictions</li>
                    </ul>
                `;
                break;
            default:
                content += `<p>Fonctionnalité en développement.</p>`;
        }
        
        createModal(`${icon} ${title}`, content);
    });
});

// Add click handlers to table rows
document.querySelectorAll('tbody tr').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function() {
        const cells = this.querySelectorAll('td');
        const date = cells[0].textContent;
        const opponent = cells[1].textContent;
        const result = cells[2].textContent;
        const rating = cells[3].textContent;
        
        const content = `
            <div class="match-details">
                <h3>Détails du Match</h3>
                <p><strong>Date:</strong> ${date}</p>
                <p><strong>Adversaire:</strong> ${opponent}</p>
                <p><strong>Résultat:</strong> ${result}</p>
                <p><strong>Note:</strong> ${rating}/5</p>
                <hr>
                <h4>Statistiques du Match</h4>
                <ul>
                    <li>Possession: 58%</li>
                    <li>Tirs: 15</li>
                    <li>Tirs cadrés: 8</li>
                    <li>Corners: 6</li>
                    <li>Fautes: 12</li>
                </ul>
                <h4>Joueurs Clés</h4>
                <ul>
                    <li>Meilleur joueur: À déterminer</li>
                    <li>Buts marqués: 2</li>
                    <li>Passe décisive: 1</li>
                </ul>
            </div>
        `;
        
        createModal(`Match: OL vs ${opponent}`, content);
    });
});

// ============================================
// CHARGEMENT DES DONNÉES CSV
// ============================================

// Fonction pour parser un CSV (gère les valeurs entre guillemets)
function parseCSV(text) {
    const lines = text.trim().split('\n');
    if (lines.length === 0) return [];
    
    function parseLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        result.push(current.trim());
        return result;
    }
    
    const headers = parseLine(lines[0]);
    const rows = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = parseLine(lines[i]);
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index] || '';
        });
        rows.push(row);
    }
    
    return rows;
}

// Fonction pour formater une date
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR');
}

// Fonction pour obtenir la classe badge selon le résultat
function getResultBadge(result) {
    if (result === 'W') return 'badge badge-win';
    if (result === 'D') return 'badge badge-draw';
    if (result === 'L') return 'badge badge-loss';
    return 'badge';
}

// Charger les matchs
async function loadMatches() {
    try {
        const response = await fetch('data/processed/ol_match_score_final.csv');
        const text = await response.text();
        const matches = parseCSV(text);
        
        const tbody = document.getElementById('matches-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        // Trier par date (plus récent en premier)
        matches.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        matches.forEach(match => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.innerHTML = `
                <td>${formatDate(match.date)}</td>
                <td>${match.opponent || ''}</td>
                <td>${match.venue === 'Home' ? 'Domicile' : 'Extérieur'}</td>
                <td><span class="${getResultBadge(match.result)}">
                    ${match.result === 'W' ? 'Victoire' : match.result === 'D' ? 'Nul' : 'Défaite'}
                </span></td>
                <td>${match.points || 0}</td>
                <td>${parseFloat(match.match_rating || 0).toFixed(1)}</td>
                <td>${match.score_final || ''}</td>
            `;
            
            row.addEventListener('click', () => {
                const content = `
                    <div class="match-details">
                        <h3>Détails du Match</h3>
                        <p><strong>Date:</strong> ${formatDate(match.date)}</p>
                        <p><strong>Adversaire:</strong> ${match.opponent || ''}</p>
                        <p><strong>Lieu:</strong> ${match.venue === 'Home' ? 'Domicile' : 'Extérieur'}</p>
                        <p><strong>Résultat:</strong> ${match.result === 'W' ? 'Victoire' : match.result === 'D' ? 'Nul' : 'Défaite'}</p>
                        <p><strong>Points:</strong> ${match.points || 0}</p>
                        <p><strong>Note:</strong> ${parseFloat(match.match_rating || 0).toFixed(1)}</p>
                        <p><strong>Score:</strong> ${match.score_final || ''}</p>
                    </div>
                `;
                createModal(`Match: OL vs ${match.opponent || ''}`, content);
            });
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des matchs:', error);
        const tbody = document.getElementById('matches-tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="error">Erreur lors du chargement des données</td></tr>';
        }
    }
}

// Charger les joueurs
async function loadPlayers() {
    try {
        const response = await fetch('data/processed/ol_key_players.csv');
        const text = await response.text();
        const players = parseCSV(text);
        
        const tbody = document.getElementById('players-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        // Trier par importance (plus important en premier)
        players.sort((a, b) => parseFloat(b.importance || 0) - parseFloat(a.importance || 0));
        
        players.forEach(player => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.innerHTML = `
                <td>${player.player || ''}</td>
                <td>${player.pos || ''}</td>
                <td>${parseInt(player['Playing Time_Min'] || 0).toLocaleString('fr-FR')}</td>
                <td>${parseFloat(player.rating || 0).toFixed(1)}</td>
                <td>${parseFloat(player.importance || 0).toFixed(2)}</td>
            `;
            
            row.addEventListener('click', () => {
                const content = `
                    <div class="player-details">
                        <h3>Détails du Joueur</h3>
                        <p><strong>Nom:</strong> ${player.player || ''}</p>
                        <p><strong>Position:</strong> ${player.pos || ''}</p>
                        <p><strong>Temps de Jeu:</strong> ${parseInt(player['Playing Time_Min'] || 0).toLocaleString('fr-FR')} minutes</p>
                        <p><strong>Note:</strong> ${parseFloat(player.rating || 0).toFixed(1)}</p>
                        <p><strong>Importance:</strong> ${parseFloat(player.importance || 0).toFixed(2)}</p>
                    </div>
                `;
                createModal(`Joueur: ${player.player || ''}`, content);
            });
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des joueurs:', error);
        const tbody = document.getElementById('players-tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" class="error">Erreur lors du chargement des données</td></tr>';
        }
    }
}

// Charger les compositions
async function loadLineups() {
    try {
        const response = await fetch('data/processed/ol_lineups_by_match.csv');
        const text = await response.text();
        const lineups = parseCSV(text);
        
        const tbody = document.getElementById('lineups-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        // Limiter à 100 lignes pour les performances
        const limitedLineups = lineups.slice(0, 100);
        
        limitedLineups.forEach(lineup => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            const matchKey = lineup.match_key || '';
            const matchDisplay = matchKey.split('_').slice(-2).join(' ') || matchKey;
            
            row.innerHTML = `
                <td>${matchDisplay}</td>
                <td>${lineup.player || ''}</td>
                <td>${lineup.pos || ''}</td>
                <td>${parseInt(lineup.minutes_played || 0)}</td>
            `;
            
            row.addEventListener('click', () => {
                const content = `
                    <div class="lineup-details">
                        <h3>Détails de la Composition</h3>
                        <p><strong>Match:</strong> ${matchDisplay}</p>
                        <p><strong>Joueur:</strong> ${lineup.player || ''}</p>
                        <p><strong>Position:</strong> ${lineup.pos || ''}</p>
                        <p><strong>Minutes Jouées:</strong> ${parseInt(lineup.minutes_played || 0)}</p>
                    </div>
                `;
                createModal(`Composition: ${matchDisplay}`, content);
            });
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des compositions:', error);
        const tbody = document.getElementById('lineups-tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4" class="error">Erreur lors du chargement des données</td></tr>';
        }
    }
}

// Charger les statistiques
async function loadStats() {
    try {
        // Charger les stats des matchs
        const matchesResponse = await fetch('data/processed/ol_match_score_final.csv');
        const matchesText = await matchesResponse.text();
        const matches = parseCSV(matchesText);
        
        const matchStatsDiv = document.getElementById('match-stats');
        if (matchStatsDiv) {
            const totalMatches = matches.length;
            const wins = matches.filter(m => m.result === 'W').length;
            const draws = matches.filter(m => m.result === 'D').length;
            const losses = matches.filter(m => m.result === 'L').length;
            const totalPoints = matches.reduce((sum, m) => sum + parseInt(m.points || 0), 0);
            const avgRating = matches.reduce((sum, m) => sum + parseFloat(m.match_rating || 0), 0) / totalMatches;
            
            matchStatsDiv.innerHTML = `
                <ul>
                    <li><strong>Total de matchs:</strong> ${totalMatches}</li>
                    <li><strong>Victoires:</strong> ${wins}</li>
                    <li><strong>Nuls:</strong> ${draws}</li>
                    <li><strong>Défaites:</strong> ${losses}</li>
                    <li><strong>Points totaux:</strong> ${totalPoints}</li>
                    <li><strong>Note moyenne:</strong> ${avgRating.toFixed(1)}</li>
                </ul>
            `;
        }
        
        try {
            const combosResponse = await fetch('data/processed/ol_best_combos_ALL_3_to_11.csv');
            const combosText = await combosResponse.text();
            const rawCombos = parseCSV(combosText);
            
            const comboStatsDiv = document.getElementById('combo-stats');
            if (comboStatsDiv && rawCombos.length > 0) {
                const combos = rawCombos
                    .map(c => ({
                        name: c.combo || c.players || '',
                        size: parseInt(c.size || c.combo_size || '0', 10) || 0,
                        matches: parseInt(c.matches || '0', 10) || 0,
                        avgPoints: parseFloat(c.avg_points || '0') || 0,
                        avgScore: parseFloat(c.avg_score_final || c.avg_score || '0') || 0
                    }))
                    .filter(c => c.name && c.size >= 2);

                const pickBestForSize = targetSize => {
                    const candidates = combos.filter(c => c.size === targetSize);
                    if (candidates.length === 0) {
                        return null;
                    }
                    return candidates.sort((a, b) => {
                        if (b.avgPoints !== a.avgPoints) {
                            return b.avgPoints - a.avgPoints;
                        }
                        return b.avgScore - a.avgScore;
                    })[0];
                };

                const bestBySize = [];
                for (let size = 2; size <= 11; size++) {
                    const best = pickBestForSize(size);
                    if (best) {
                        bestBySize.push({ size, best });
                    }
                }

                if (bestBySize.length === 0) {
                    comboStatsDiv.innerHTML = '<p>Données de combinaisons non disponibles</p>';
                } else {
                    let html = '<ul>';
                    bestBySize.forEach(entry => {
                        html += `<li><strong>${entry.size} joueurs:</strong> ${entry.best.name} — ${entry.best.avgPoints.toFixed(2)} pts/m (${entry.best.matches} matchs)</li>`;
                    });
                    html += '</ul>';
                    comboStatsDiv.innerHTML = html;
                }
            } else if (comboStatsDiv) {
                comboStatsDiv.innerHTML = '<p>Données de combinaisons non disponibles</p>';
            }
        } catch (comboError) {
            const comboStatsDiv = document.getElementById('combo-stats');
            if (comboStatsDiv) {
                comboStatsDiv.innerHTML = '<p>Données de combinaisons non disponibles</p>';
            }
        }

        try {
            const olStatsResponse = await fetch('data/ol_stats.csv');
            const olStatsText = await olStatsResponse.text();
            const olStatsRows = parseCSV(olStatsText);
            const olStatsDiv = document.getElementById('ol-fbref-stats');
            if (olStatsDiv && olStatsRows && olStatsRows.length > 0) {
                const olRow =
                    olStatsRows.find(r =>
                        (r.team || '').toLowerCase().includes('lyon')
                    ) || olStatsRows[0];

                const keys = Object.keys(olRow || {});

                const getNumber = candidates => {
                    for (const key of candidates) {
                        const foundKey = keys.find(
                            k => k.toLowerCase() === key.toLowerCase()
                        );
                        if (
                            foundKey &&
                            olRow[foundKey] !== undefined &&
                            olRow[foundKey] !== ''
                        ) {
                            const value = parseFloat(olRow[foundKey]);
                            if (!Number.isNaN(value)) {
                                return value;
                            }
                        }
                    }
                    return null;
                };

                const goalsFor = getNumber(['goals_for', 'gf', 'goals']);
                const goalsAgainst = getNumber(['goals_against', 'ga']);
                const xgFor = getNumber(['xg_for', 'xg']);
                const xgAgainst = getNumber(['xg_against', 'xga']);
                const shots = getNumber(['shots', 'shots_total']);
                const possession = getNumber(['possession']);

                let html = '<ul>';
                if (goalsFor !== null && goalsAgainst !== null) {
                    html += `<li><strong>Buts marqués / encaissés:</strong> ${goalsFor} / ${goalsAgainst}</li>`;
                }
                if (xgFor !== null && xgAgainst !== null) {
                    html += `<li><strong>xG pour / contre:</strong> ${xgFor.toFixed(2)} / ${xgAgainst.toFixed(2)}</li>`;
                }
                if (shots !== null) {
                    html += `<li><strong>Tirs totaux:</strong> ${shots.toFixed(0)}</li>`;
                }
                if (possession !== null) {
                    html += `<li><strong>Possession moyenne:</strong> ${possession.toFixed(1)}%</li>`;
                }
                html += '</ul>';

                olStatsDiv.innerHTML = html;
            } else if (olStatsDiv) {
                olStatsDiv.innerHTML = '<p>Données FBref non disponibles</p>';
            }
        } catch (olError) {
            const olStatsDiv = document.getElementById('ol-fbref-stats');
            if (olStatsDiv) {
                olStatsDiv.innerHTML = '<p>Données FBref non disponibles</p>';
            }
        }
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
        const matchStatsDiv = document.getElementById('match-stats');
        if (matchStatsDiv) {
            matchStatsDiv.innerHTML = '<p class="error">Erreur lors du chargement des données</p>';
        }
    }
}

// Charger les classements Ligue 1
async function loadStandings() {
    try {
        let fbrefOk = false;
        try {
            const fbref = await fetch('data/ligue1_standings.csv');
            if (fbref.ok) {
                const fbText = await fbref.text();
                const fbRows = parseCSV(fbText);
                const tbody = document.getElementById('standings-general-tbody');
                if (tbody && fbRows && fbRows.length > 0) {
                    const keys = Object.keys(fbRows[0] || {});
                    const getKey = (cands) => {
                        for (const k of cands) {
                            const hit = keys.find(x => x.toLowerCase() === k.toLowerCase());
                            if (hit) return hit;
                        }
                        return null;
                    };
                    const kTeam = getKey(['team', 'squad']);
                    const kMp = getKey(['mp', 'matches', 'played']);
                    const kPts = getKey(['pts', 'points']);
                    const kW = getKey(['wins', 'w']);
                    const kD = getKey(['draws', 'd']);
                    const kL = getKey(['losses', 'l']);
                    const kGf = getKey(['gf', 'goals_for']);
                    const kGa = getKey(['ga', 'goals_against']);

                    const rows = fbRows
                        .map(r => ({
                            team: r[kTeam] || '',
                            mp: parseFloat(r[kMp] || '0') || 0,
                            pts: parseFloat(r[kPts] || '0') || 0,
                            w: parseFloat(r[kW] || '0') || 0,
                            d: parseFloat(r[kD] || '0') || 0,
                            l: parseFloat(r[kL] || '0') || 0,
                            gf: parseFloat(r[kGf] || '0') || 0,
                            ga: parseFloat(r[kGa] || '0') || 0,
                        }))
                        .filter(r => r.team);

                    rows.sort((a, b) => {
                        if (b.pts !== a.pts) return b.pts - a.pts;
                        const gdA = a.gf - a.ga;
                        const gdB = b.gf - b.ga;
                        if (gdB !== gdA) return gdB - gdA;
                        return b.gf - a.gf;
                    });

                    tbody.innerHTML = '';
                    rows.forEach((team, idx) => {
                        const tr = document.createElement('tr');
                        const gd = team.gf - team.ga;
                        const ppm = team.mp > 0 ? team.pts / team.mp : 0;
                        const wr = team.mp > 0 ? (team.w / team.mp) * 100 : 0;
                        const gfpm = team.mp > 0 ? team.gf / team.mp : 0;
                        const gapm = team.mp > 0 ? team.ga / team.mp : 0;
                        tr.innerHTML = `
                            <td class="rank-cell">${idx + 1}</td>
                            <td class="team-cell"><strong>${team.team}</strong></td>
                            <td>${team.mp}</td>
                            <td>${team.w}</td>
                            <td>${team.d}</td>
                            <td>${team.l}</td>
                            <td>${team.gf}</td>
                            <td>${team.ga}</td>
                            <td class="${gd >= 0 ? 'positive' : 'negative'}">${gd >= 0 ? '+' : ''}${gd}</td>
                            <td class="points-cell"><strong>${team.pts}</strong></td>
                            <td>${ppm.toFixed(2)}</td>
                            <td>${wr.toFixed(1)}%</td>
                            <td>${gfpm.toFixed(2)}</td>
                            <td>${gapm.toFixed(2)}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    fbrefOk = true;
                }
            }
        } catch (e) {
            fbrefOk = false;
        }

        if (fbrefOk) {
            return;
        }

        const response = await fetch('data/processed/league1_standings_home_away.csv');
        const text = await response.text();
        const standings = parseCSV(text);
        
        if (!standings || standings.length === 0) {
            throw new Error('Aucune donnée de classement disponible');
        }

        const filteredStandings = standings.filter(team => {
            const teamName = (team.team || '').toLowerCase();
            return !teamName.includes('choc') && !teamName.includes('olympiques');
        });

        displayStandingsTable(filteredStandings, 'general', 'standings-general-tbody', {
            rank: 'rank',
            team: 'team',
            matches: 'matches',
            wins: 'wins',
            draws: 'draws',
            losses: 'losses',
            goals_for: 'goals_for',
            goals_against: 'goals_against',
            goal_difference: 'goal_difference',
            points: 'points',
            points_per_match: 'points_per_match',
            win_rate: 'win_rate',
            goals_for_per_match: 'goals_for_per_match',
            goals_against_per_match: 'goals_against_per_match'
        });

        displayStandingsTable(filteredStandings, 'home', 'standings-home-tbody', {
            rank: 'home_rank',
            team: 'team',
            matches: 'home_matches',
            wins: 'home_wins',
            draws: 'home_draws',
            losses: 'home_losses',
            goals_for: 'home_goals_for',
            goals_against: 'home_goals_against',
            goal_difference: 'home_goal_difference',
            points: 'home_points',
            points_per_match: 'home_points_per_match',
            win_rate: 'home_win_rate',
            goals_for_per_match: 'home_goals_for_per_match',
            goals_against_per_match: 'home_goals_against_per_match'
        });

        displayStandingsTable(filteredStandings, 'away', 'standings-away-tbody', {
            rank: 'away_rank',
            team: 'team',
            matches: 'away_matches',
            wins: 'away_wins',
            draws: 'away_draws',
            losses: 'away_losses',
            goals_for: 'away_goals_for',
            goals_against: 'away_goals_against',
            goal_difference: 'away_goal_difference',
            points: 'away_points',
            points_per_match: 'away_points_per_match',
            win_rate: 'away_win_rate',
            goals_for_per_match: 'away_goals_for_per_match',
            goals_against_per_match: 'away_goals_against_per_match'
        });

        // Les tableaux sont affichés directement à partir du CSV de classement.

    } catch (error) {
        console.error('Erreur lors du chargement des classements:', error);
        const tbodyGeneral = document.getElementById('standings-general-tbody');
        const tbodyHome = document.getElementById('standings-home-tbody');
        const tbodyAway = document.getElementById('standings-away-tbody');
        
        if (tbodyGeneral) {
            tbodyGeneral.innerHTML = '<tr><td colspan="13" class="error">Erreur lors du chargement des données</td></tr>';
        }
        if (tbodyHome) {
            tbodyHome.innerHTML = '<tr><td colspan="14" class="error">Erreur lors du chargement des données</td></tr>';
        }
        if (tbodyAway) {
            tbodyAway.innerHTML = '<tr><td colspan="14" class="error">Erreur lors du chargement des données</td></tr>';
        }
    }
}

// Fonction pour afficher un tableau de classement
function displayStandingsTable(standings, type, tbodyId, columnMap) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    tbody.innerHTML = '';

    // Trier par rang
    const sortedStandings = [...standings].sort((a, b) => {
        const rankA = parseFloat(a[columnMap.rank]) || 999;
        const rankB = parseFloat(b[columnMap.rank]) || 999;
        return rankA - rankB;
    });

    sortedStandings.forEach((team, index) => {
        const row = document.createElement('tr');
        
        // Style selon le rang (top 3, relégation, etc.)
        const rank = parseInt(team[columnMap.rank]) || index + 1;
        if (rank <= 3) {
            row.classList.add('top-three');
        } else if (rank >= 18) {
            row.classList.add('relegation');
        }

        const formatNumber = (value, decimals = 0) => {
            const num = parseFloat(value);
            if (isNaN(num)) return '0';
            return decimals > 0 ? num.toFixed(decimals) : Math.round(num).toString();
        };

        row.innerHTML = `
            <td class="rank-cell">${rank}</td>
            <td class="team-cell"><strong>${team[columnMap.team] || ''}</strong></td>
            <td>${formatNumber(team[columnMap.matches])}</td>
            <td>${formatNumber(team[columnMap.wins])}</td>
            <td>${formatNumber(team[columnMap.draws])}</td>
            <td>${formatNumber(team[columnMap.losses])}</td>
            <td>${formatNumber(team[columnMap.goals_for])}</td>
            <td>${formatNumber(team[columnMap.goals_against])}</td>
            <td class="${parseFloat(team[columnMap.goal_difference]) >= 0 ? 'positive' : 'negative'}">
                ${parseFloat(team[columnMap.goal_difference]) >= 0 ? '+' : ''}${formatNumber(team[columnMap.goal_difference])}
            </td>
            <td class="points-cell"><strong>${formatNumber(team[columnMap.points])}</strong></td>
            <td>${formatNumber(team[columnMap.points_per_match], 2)}</td>
            <td>${formatNumber(team[columnMap.win_rate], 1)}%</td>
            <td>${formatNumber(team[columnMap.goals_for_per_match], 2)}</td>
            <td>${formatNumber(team[columnMap.goals_against_per_match], 2)}</td>
        `;

        // Ajouter un effet au survol
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            const content = `
                <div class="team-details">
                    <h3>${team[columnMap.team] || ''}</h3>
                    <div class="team-stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Rang:</span>
                            <span class="stat-value">${rank}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Points:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.points])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Matchs:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.matches])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Victoires:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.wins])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Nuls:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.draws])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Défaites:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.losses])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Buts pour:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.goals_for])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Buts contre:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.goals_against])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Différence:</span>
                            <span class="stat-value">${parseFloat(team[columnMap.goal_difference]) >= 0 ? '+' : ''}${formatNumber(team[columnMap.goal_difference])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Points/Match:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.points_per_match], 2)}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">% Victoires:</span>
                            <span class="stat-value">${formatNumber(team[columnMap.win_rate], 1)}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Buts/Match (pour):</span>
                            <span class="stat-value">${formatNumber(team[columnMap.goals_for_per_match], 2)}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Buts/Match (contre):</span>
                            <span class="stat-value">${formatNumber(team[columnMap.goals_against_per_match], 2)}</span>
                        </div>
                    </div>
                </div>
            `;
            createModal(`Statistiques: ${team[columnMap.team]}`, content);
        });

        tbody.appendChild(row);
    });
}

// Gestion des onglets pour les classements
function initStandingsTabs() {
    const tabButtons = document.querySelectorAll('.standings-tabs .tab-btn');
    const tabContents = document.querySelectorAll('.standings-table-container');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Retirer la classe active de tous les boutons et contenus
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Ajouter la classe active au bouton cliqué
            button.classList.add('active');

            // Afficher le contenu correspondant
            const targetContent = document.getElementById(`standings-${targetTab}`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadLineups();
    loadStats();
    loadStandings();
    initStandingsTabs();
});
