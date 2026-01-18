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

// Fonction utilitaire pour éviter le cache sur les CSV
function cacheBust(url) {
    const sep = url.includes('?') ? '&' : '?';
    return `${url}${sep}_=${Date.now()}`;
}

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
        const response = await fetch(cacheBust('data/processed/ol_match_score_final.csv'));
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
        const response = await fetch(cacheBust('data/processed/ol_key_players.csv'));
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

function parseLineupMatchKey(rawKey) {
    const value = (rawKey || '').trim();
    if (!value) return null;
    const firstSpace = value.indexOf(' ');
    if (firstSpace === -1) {
        return {
            rawKey: value,
            date: '',
            opponent: '',
            venue: '',
            lookupKey: null,
            label: value
        };
    }
    const prefix = value.slice(0, firstSpace);
    const rest = value.slice(firstSpace + 1);
    const prefixParts = prefix.split('_');
    const date = prefixParts.length > 1 ? prefixParts[1] : '';
    let opponent = '';
    let venue = '';
    if (rest.startsWith('Lyon-')) {
        opponent = rest.slice('Lyon-'.length);
        venue = 'Home';
    } else if (rest.endsWith('-Lyon')) {
        opponent = rest.slice(0, rest.length - '-Lyon'.length);
        venue = 'Away';
    } else {
        const hyphenIndex = rest.indexOf('-');
        if (hyphenIndex !== -1) {
            const firstTeam = rest.slice(0, hyphenIndex);
            const secondTeam = rest.slice(hyphenIndex + 1);
            if (firstTeam === 'Lyon') {
                opponent = secondTeam;
                venue = 'Home';
            } else if (secondTeam === 'Lyon') {
                opponent = firstTeam;
                venue = 'Away';
            }
        }
    }
    const lookupKey = date && opponent ? `${date}_${opponent}` : null;
    let label = value;
    if (date && opponent) {
        const formattedDate = formatDate(date);
        if (venue === 'Home') {
            label = `${formattedDate} • OL vs ${opponent}`;
        } else if (venue === 'Away') {
            label = `${formattedDate} • ${opponent} vs OL`;
        } else {
            label = `${formattedDate} • ${opponent}`;
        }
    }
    return {
        rawKey: value,
        date,
        opponent,
        venue,
        lookupKey,
        label
    };
}

function translatePositionFr(pos) {
    const p = (pos || '').toUpperCase();
    const primary = p.split(',')[0].trim();
    const map = {
        GK: 'G',
        RB: 'DD',
        LB: 'DG',
        CB: 'DC',
        RWB: 'DD',
        LWB: 'DG',
        WB: 'MG',
        RM: 'MD',
        LM: 'MG',
        DM: 'MDC',
        CDM: 'MDC',
        CM: 'MC',
        AM: 'MOC',
        CAM: 'MOC',
        RW: 'AD',
        LW: 'AG',
        FW: 'BU',
        ST: 'BU'
    };
    return map[primary] || primary || '-';
}

function buildLineupPitch(players) {
    const toPrimary = x => (x || '').toUpperCase().split(',')[0].trim();
    const data = players.map(p => ({
        name: p.name || '',
        pos: p.pos || '',
        primary: toPrimary(p.pos || ''),
        posFr: translatePositionFr(p.pos || '')
    }));
    const gk = data.filter(d => d.primary === 'GK');
    const defenders = data.filter(d => ['RB', 'LB', 'CB', 'RWB', 'LWB'].includes(d.primary));
    const midsDeep = data.filter(d => ['DM', 'CDM'].includes(d.primary));
    const midsCentral = data.filter(d => ['CM'].includes(d.primary));
    const midsAdvanced = data.filter(d => ['AM', 'CAM'].includes(d.primary));
    const attackers = data.filter(d => ['RW', 'LW', 'FW', 'ST'].includes(d.primary));
    function orderDef(defs) {
        const lefts = defs.filter(d => ['LB', 'LWB'].includes(d.primary));
        const rights = defs.filter(d => ['RB', 'RWB'].includes(d.primary));
        const centers = defs.filter(d => d.primary === 'CB');
        return [...lefts, ...centers, ...rights];
    }
    function orderAtt(atts) {
        const lefts = atts.filter(d => d.primary === 'LW');
        const centers = atts.filter(d => ['ST', 'FW'].includes(d.primary));
        const rights = atts.filter(d => d.primary === 'RW');
        return [...lefts, ...centers, ...rights];
    }
    function orderMid(mids) {
        const d = midsDeep.slice();
        const c = midsCentral.slice();
        const a = midsAdvanced.slice();
        return { deep: d, central: c, adv: a };
    }
    const defOrdered = orderDef(defenders);
    const attOrdered = orderAtt(attackers);
    const midGroups = orderMid(midsDeep.concat(midsCentral).concat(midsAdvanced));
    const midCount = midGroups.deep.length + midGroups.central.length + midGroups.adv.length;
    const formation = `${defOrdered.length}-${midCount}-${attOrdered.length}`;
    const yAttack = 16;
    const yMidAdv = 34;
    const yMidDeep = 52;
    const yDefense = 72;
    const yGk = 90;
    const marginX = 10;
    function spreadXs(n, bias = 0) {
        const step = (100 - marginX * 2) / (n + 1);
        const xs = [];
        for (let i = 1; i <= n; i++) {
            xs.push(marginX + step * i + bias);
        }
        return xs;
    }
    function nodesFrom(line, y, bias = 0) {
        const xs = spreadXs(line.length, bias);
        return line.map((p, i) => ({
            left: xs[i],
            top: y,
            name: p.name,
            posFr: p.posFr
        }));
    }
    const nodes = []
        .concat(nodesFrom(attOrdered, yAttack))
        .concat(nodesFrom(midGroups.adv, yMidAdv))
        .concat(nodesFrom(midGroups.central, (yMidAdv + yMidDeep) / 2, 2))
        .concat(nodesFrom(midGroups.deep, yMidDeep))
        .concat(nodesFrom(defOrdered, yDefense))
        .concat(nodesFrom(gk, yGk));
    let html = `
        <div class="pitch">
            <div class="pitch-markings">
                <div class="goal goal-top"></div>
                <div class="penalty-area penalty-top"></div>
                <div class="six-yard six-top"></div>
                <div class="center-circle"></div>
                <div class="goal goal-bottom"></div>
                <div class="penalty-area penalty-bottom"></div>
                <div class="six-yard six-bottom"></div>
            </div>
    `;
    nodes.forEach(n => {
        html += `
            <div class="player-node" style="left:${n.left}%; top:${n.top}%">
                <div class="player-dot"></div>
                <div class="player-name">${n.name}</div>
                <div class="player-pos">${n.posFr}</div>
            </div>
        `;
    });
    html += `</div>`;
    html += `<p class="formation-label"><strong>Formation estimée:</strong> ${formation}</p>`;
    return html;
}

function buildLineupPitchWithFormation(players, formationStr) {
    const sorted = players
        .slice()
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0))
        .slice(0, Math.min(players.length, 11));
    const toPrimary = x => (x || '').toUpperCase().split(',')[0].trim();
    const data = sorted.map(p => ({
        name: p.name || '',
        pos: p.pos || '',
        primary: toPrimary(p.pos || ''),
        posFr: translatePositionFr(p.pos || '')
    }));
    const nums = (formationStr || '').split('-').map(n => parseInt(n, 10)).filter(n => !Number.isNaN(n));
    const defCount = nums.length > 0 ? nums[0] : null;
    const attCount = nums.length > 0 ? nums[nums.length - 1] : null;
    const midCounts = nums.length > 2 ? nums.slice(1, nums.length - 1) : (nums.length === 2 ? [nums[1]] : []);
    const isThreeBack = defCount === 3;
    const gk = data.filter(d => d.primary === 'GK').sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    const defenders = data
        .filter(d => ['RB', 'LB', 'CB', 'RWB', 'LWB'].includes(d.primary))
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    const midsDeep = data
        .filter(d => ['DM', 'CDM'].includes(d.primary))
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    const midsCentral = data
        .filter(d => ['CM', 'LM', 'RM'].includes(d.primary))
        .concat(isThreeBack ? data.filter(d => ['LWB', 'RWB', 'WB'].includes(d.primary)) : [])
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    const midsAdvanced = data
        .filter(d => ['AM', 'CAM'].includes(d.primary))
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    const attackers = data
        .filter(d => ['RW', 'LW', 'FW', 'ST'].includes(d.primary))
        .sort((a, b) => (b.minutes || 0) - (a.minutes || 0));
    function orderDef(defs) {
        const lefts = defs.filter(d => ['LB', 'LWB'].includes(d.primary));
        const rights = defs.filter(d => ['RB', 'RWB'].includes(d.primary));
        const centers = defs.filter(d => d.primary === 'CB');
        return defCount === 4 ? [...lefts, ...centers, ...rights] : centers;
    }
    function orderAtt(atts) {
        const lefts = atts.filter(d => d.primary === 'LW');
        const centers = atts.filter(d => ['ST', 'FW'].includes(d.primary));
        const rights = atts.filter(d => d.primary === 'RW');
        return [...lefts, ...centers, ...rights];
    }
    const defOrdered = orderDef(defenders);
    const attOrdered = orderAtt(attackers);
    const midDeepOrdered = midsDeep;
    const midCentralOrdered = midsCentral;
    const midAdvOrdered = midsAdvanced;
    const wantMidMain = midCounts.length >= 1 ? midCounts[0] : (midCounts.length === 0 ? (midsDeep.length + midsCentral.length) : 0);
    const wantMidAdv = midCounts.length >= 2 ? midCounts[1] : 0;
    const selected = [];
    if (gk.length > 0) selected.push(gk[0]);
    defOrdered.slice(0, defCount || 4).forEach(p => selected.push(p));
    const takeDeep = Math.min(wantMidMain, midDeepOrdered.length);
    midDeepOrdered.slice(0, takeDeep).forEach(p => selected.push(p));
    const remainingMain = Math.max((wantMidMain || 0) - takeDeep, 0);
    midCentralOrdered.slice(0, remainingMain).forEach(p => selected.push(p));
    const takeAdv = Math.min(wantMidAdv, midAdvOrdered.length);
    midAdvOrdered.slice(0, takeAdv).forEach(p => selected.push(p));
    const fillAdvRemain = Math.max((wantMidAdv || 0) - takeAdv, 0);
    if (fillAdvRemain > 0) {
        midCentralOrdered.slice(remainingMain, remainingMain + fillAdvRemain).forEach(p => selected.push(p));
    }
    attOrdered.slice(0, attCount || 2).forEach(p => selected.push(p));
    if (selected.length < 11) {
        const pool = data.filter(d => !selected.some(s => s.name === d.name));
        pool.slice(0, 11 - selected.length).forEach(p => selected.push(p));
    }
    const formation = `${defOrdered.length}-${midDeepOrdered.length + midCentralOrdered.length + midAdvOrdered.length}-${attOrdered.length}`;
    const yAttack = 16;
    const yMidAdv = (wantMidAdv || 0) > 0 ? 32 : 36;
    const yMidCentral = 44;
    const yMidDeep = 56;
    const yDefense = 74;
    const yGk = 90;
    const marginX = 10;
    function spreadXs(n, bias = 0) {
        const step = (100 - marginX * 2) / (Math.max(n, 1) + 1);
        const xs = [];
        for (let i = 1; i <= Math.max(n, 1); i++) {
            xs.push(marginX + step * i + bias);
        }
        return xs.slice(0, n);
    }
    function nodesFrom(line, y, bias = 0) {
        const xs = spreadXs(line.length, bias);
        return line.map((p, i) => ({
            left: xs[i],
            top: y,
            name: p.name,
            posFr: p.posFr
        }));
    }
    const selNames = new Set(selected.map(s => s.name));
    const selGK = selected.filter(s => s.primary === 'GK');
    const selDef = selected.filter(s => ['RB', 'LB', 'CB', 'RWB', 'LWB'].includes(s.primary));
    const selMidDeep = selected.filter(s => ['DM', 'CDM'].includes(s.primary));
    const selMidCentral = selected.filter(s => ['CM', 'LM', 'RM'].includes(s.primary));
    const selMidAdv = selected.filter(s => ['AM', 'CAM'].includes(s.primary));
    const selAtt = selected.filter(s => ['RW', 'LW', 'FW', 'ST'].includes(s.primary));
    const nodes = []
        .concat(nodesFrom(selAtt, yAttack))
        .concat(nodesFrom(selMidAdv, yMidAdv))
        .concat(nodesFrom(selMidCentral, yMidCentral, 2))
        .concat(nodesFrom(selMidDeep, yMidDeep))
        .concat(nodesFrom(selDef, yDefense))
        .concat(nodesFrom(selGK, yGk));
    let html = `
        <div class="pitch">
            <div class="pitch-markings">
                <div class="goal goal-top"></div>
                <div class="penalty-area penalty-top"></div>
                <div class="six-yard six-top"></div>
                <div class="center-circle"></div>
                <div class="goal goal-bottom"></div>
                <div class="penalty-area penalty-bottom"></div>
                <div class="six-yard six-bottom"></div>
            </div>
    `;
    nodes.forEach(n => {
        html += `
            <div class="player-node" style="left:${n.left}%; top:${n.top}%">
                <div class="player-dot"></div>
                <div class="player-name">${n.name}</div>
                <div class="player-pos">${n.posFr}</div>
            </div>
        `;
    });
    html += `</div>`;
    html += `<p class="formation-label"><strong>Formation estimée:</strong> ${formation}</p>`;
    return html;
}
async function loadLineups() {
    try {
        const [lineupsResponse, lookupResponse, cleanResponse, minutesResponse, aggResponse] = await Promise.all([
            fetch(cacheBust('data/processed/ol_lineups_by_match.csv')),
            fetch(cacheBust('data/processed/match_lookup.csv')),
            fetch(cacheBust('data/processed/ol_matches_clean.csv')),
            fetch(cacheBust('data/processed/ol_player_minutes.csv')),
            fetch(cacheBust('data/processed/ol_match_lineups.csv'))
        ]);
        const lineupsText = await lineupsResponse.text();
        const lookupText = await lookupResponse.text();
        const cleanText = await cleanResponse.text();
        const minutesText = await minutesResponse.text();
        const aggText = await aggResponse.text();
        const lineups = parseCSV(lineupsText);
        const lookupRows = parseCSV(lookupText);
        const cleanRows = parseCSV(cleanText);
        const minutesRows = parseCSV(minutesText);
        const aggRows = parseCSV(aggText);
        const tbody = document.getElementById('lineups-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        const lookupMap = {};
        lookupRows.forEach(row => {
            const date = row.date || '';
            const opponent = row.opponent || '';
            if (!date || !opponent || opponent.toLowerCase() === 'lyon') {
                return;
            }
            const key = `${date}_${opponent}`;
            if (!lookupMap[key]) {
                lookupMap[key] = row;
            }
        });
        const cleanMap = {};
        cleanRows.forEach(row => {
            const date = row.date || '';
            const opponent = row.opponent || '';
            if (!date || !opponent || opponent.toLowerCase() === 'lyon') {
                return;
            }
            const key = `${date}_${opponent}`;
            if (!cleanMap[key]) {
                cleanMap[key] = row;
            }
        });
        const matchesMap = new Map();
        lineups.forEach(item => {
            const parsed = parseLineupMatchKey(item.match_key || '');
            const groupKey = parsed && parsed.lookupKey ? parsed.lookupKey : item.match_key || '';
            if (!groupKey) {
                return;
            }
            if (!matchesMap.has(groupKey)) {
                const meta = lookupMap[groupKey] || {};
                const clean = cleanMap[groupKey] || {};
                const date = parsed && parsed.date ? parsed.date : meta.date || '';
                const opponent = parsed && parsed.opponent ? parsed.opponent : meta.opponent || '';
                const venue = parsed && parsed.venue ? parsed.venue : meta.venue || '';
                const points = meta.points !== undefined && meta.points !== '' ? parseFloat(meta.points) : null;
                const scoreFinal = meta.score_final !== undefined && meta.score_final !== '' ? parseFloat(meta.score_final) : null;
                const formation = clean.Formation || '';
                const gf = clean.GF !== undefined && clean.GF !== '' ? parseFloat(clean.GF) : null;
                const ga = clean.GA !== undefined && clean.GA !== '' ? parseFloat(clean.GA) : null;
                const label = parsed && parsed.label ? parsed.label : groupKey;
                matchesMap.set(groupKey, {
                    key: groupKey,
                    date,
                    opponent,
                    venue,
                    points,
                    scoreFinal,
                    formation,
                    gf,
                    ga,
                    label,
                    players: []
                });
            }
            const match = matchesMap.get(groupKey);
            match.players.push({
                name: item.player || '',
                pos: item.pos || '',
                minutes: parseInt(item.minutes_played || 0, 10) || 0
            });
        });
        const minutesMap = {};
        minutesRows.forEach(r => {
            const gameStr = r.game || '';
            if (!gameStr) return;
            if (!minutesMap[gameStr]) minutesMap[gameStr] = [];
            minutesMap[gameStr].push({
                name: r.player || '',
                pos: r.pos || '',
                minutes: parseInt(r.minutes_played || 0, 10) || 0
            });
        });
        function parsePlayersList(str) {
            const s = (str || '').trim();
            if (!s.startsWith('[') || !s.endsWith(']')) return [];
            const inner = s.slice(1, -1);
            const parts = inner.split(',').map(x => x.trim()).filter(x => x.length > 0);
            return parts.map(p => {
                if (p.startsWith("'") && p.endsWith("'")) return p.slice(1, -1);
                if (p.startsWith('"') && p.endsWith('"')) return p.slice(1, -1);
                return p;
            });
        }
        const aggByDate = {};
        aggRows.forEach(r => {
            const mk = r.match_key || '';
            const idx = mk.indexOf('_');
            if (idx === -1) return;
            const date = mk.slice(0, idx);
            const players = parsePlayersList(r.players || '');
            if (date && players.length > 0) {
                aggByDate[date] = players;
            }
        });
        function lineupKeyToGameStr(rawKey) {
            const v = (rawKey || '').trim();
            if (!v) return null;
            const firstSpace = v.indexOf(' ');
            if (firstSpace === -1) return null;
            const prefix = v.slice(0, firstSpace);
            const rest = v.slice(firstSpace + 1);
            const parts = prefix.split('_');
            if (parts.length < 2) return null;
            const date = parts[1];
            if (!date || !rest) return null;
            return `${date} ${rest}`;
        }
        matchesMap.forEach((match, k) => {
            const anyRaw = Array.from(lineups)
                .find(it => {
                    const parsed = parseLineupMatchKey(it.match_key || '');
                    const gk = parsed && parsed.lookupKey ? parsed.lookupKey : it.match_key || '';
                    return gk && gk === k;
                });
            const gameStr = anyRaw ? lineupKeyToGameStr(anyRaw.match_key || '') : null;
            const minutesPlayers = gameStr && minutesMap[gameStr] ? minutesMap[gameStr] : [];
            const existingNames = new Set(match.players.map(p => p.name));
            minutesPlayers.forEach(mp => {
                if (!existingNames.has(mp.name)) {
                    match.players.push(mp);
                    existingNames.add(mp.name);
                } else {
                    const idx = match.players.findIndex(p => p.name === mp.name);
                    if (idx !== -1) {
                        if ((!match.players[idx].pos || match.players[idx].pos === '-') && mp.pos) {
                            match.players[idx].pos = mp.pos;
                        }
                        if ((match.players[idx].minutes || 0) === 0 && mp.minutes > 0) {
                            match.players[idx].minutes = mp.minutes;
                        }
                    }
                }
            });
            const dateKey = match.date || '';
            const aggPlayers = aggByDate[dateKey] || [];
            aggPlayers.forEach(name => {
                if (!existingNames.has(name)) {
                    match.players.push({
                        name,
                        pos: '-',
                        minutes: 0
                    });
                    existingNames.add(name);
                }
            });
        });
        const matches = Array.from(matchesMap.values()).sort((a, b) => {
            if (a.date && b.date) {
                return a.date.localeCompare(b.date);
            }
            return (a.label || '').localeCompare(b.label || '');
        });
        if (matches.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="error">Aucune donnée de composition disponible</td></tr>';
            return;
        }
        matches.forEach(match => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            let scoreText = '';
            const realScore = (match.gf !== null && match.ga !== null) ? `${Math.round(match.gf)} - ${Math.round(match.ga)}` : '';
            if (match.points !== null && match.points !== undefined) {
                scoreText = `${match.points} pts`;
            }
            if (match.scoreFinal !== null && match.scoreFinal !== undefined) {
                const ratingText = `note ${match.scoreFinal.toFixed(1)}`;
                scoreText = scoreText ? `${scoreText} • ${ratingText}` : ratingText;
            }
            if (realScore) {
                scoreText = scoreText ? `${realScore} • ${scoreText}` : realScore;
            }
            if (!scoreText) {
                scoreText = '-';
            }
            const playedCount = match.players.filter(p => (p.minutes || 0) > 0).length;
            const countBadge = playedCount > 0 ? `(${Math.min(playedCount, 11)}/11)` : '';
            const incomplete = playedCount < 11;
            row.innerHTML = `
                <td>${match.label}</td>
                <td>${match.opponent || ''}</td>
                <td>${scoreText}</td>
                <td><button class="btn btn-secondary btn-sm" data-match-key="${match.key}">Voir ${countBadge}</button></td>
            `;
            const button = row.querySelector('button');
            if (button) {
                button.addEventListener('click', event => {
                    event.stopPropagation();
                    const pitchHtml = buildLineupPitchWithFormation(match.players, match.formation || '');
                    const playersSorted = match.players.slice().sort((a, b) => b.minutes - a.minutes);
                    let listHtml = '<ul class="lineup-list">';
                    playersSorted.forEach(p => {
                        listHtml += `<li><strong>${p.name}</strong> (${translatePositionFr(p.pos || '-')}) — ${p.minutes} min</li>`;
                    });
                    listHtml += '</ul>';
                    const venueLabel = match.venue === 'Home' ? 'Domicile' : match.venue === 'Away' ? 'Extérieur' : '';
                    const headerHtml = `
                        <div class="lineup-header">
                            <p><strong>Date:</strong> ${match.date ? formatDate(match.date) : '-'}</p>
                            <p><strong>Adversaire:</strong> ${match.opponent || '-'}</p>
                            <p><strong>Lieu:</strong> ${venueLabel || '-'}</p>
                            <p><strong>Score:</strong> ${realScore || '-'}</p>
                            <p><strong>Score modèle:</strong> ${scoreText}</p>
                            <p><strong>Formation:</strong> ${match.formation || '-'}</p>
                            ${incomplete ? '<p style="color:#f87171"><strong>Attention:</strong> composition incomplète détectée</p>' : ''}
                        </div>
                    `;
                    const content = `
                        <div class="lineup-modal">
                            ${headerHtml}
                            ${pitchHtml}
                            <h3>Composition détaillée</h3>
                            ${listHtml}
                        </div>
                    `;
                    createModal(`Composition: ${match.label}`, content);
                });
            }
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
        const matchesResponse = await fetch(cacheBust('data/processed/ol_match_score_final.csv'));
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
            const combosResponse = await fetch(cacheBust('data/processed/ol_best_combos_ALL_3_to_11.csv'));
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
            const olStatsResponse = await fetch(cacheBust('data/ol_stats.csv'));
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
            const fbref = await fetch(cacheBust('data/ligue1_standings.csv'));
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

        const response = await fetch(cacheBust('data/processed/league1_standings_home_away.csv'));
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
    initMatchAnalysis();
    loadTeamStyles();
    loadHomeStats();
    loadPreviewMatches();
});

// --- Match Analysis Logic ---

async function initMatchAnalysis() {
    const btnAnalyze = document.getElementById('btn-analyze');
    if (!btnAnalyze) return;

    // Load data once
    let standingsData = [];
    let simulationData = [];
    let enginePredictions = [];

    // Charger en priorité les données existantes (classement + ancienne simulation)
    try {
        const [standingsResp, simResp] = await Promise.all([
            fetch(cacheBust('data/processed/league1_standings_home_away.csv')),
            fetch(cacheBust('data/processed/ol_next_match_simulation.csv'))
        ]);

        if (standingsResp.ok) {
            const text = await standingsResp.text();
            standingsData = parseCSV(text);
            populateOpponentDropdown(standingsData);
        }
        if (simResp.ok) {
            const text = await simResp.text();
            simulationData = parseCSV(text);
        }
    } catch (e) {
        console.error("Error loading core analysis data:", e);
    }

    // Charger ensuite les prédictions du nouveau moteur (optionnel, ne doit jamais casser le reste)
    try {
        const engineResp = await fetch(cacheBust('prediction_engine/data/match_predictions.csv'));
        if (engineResp.ok) {
            const text = await engineResp.text();
            enginePredictions = parseCSV(text);
        }
    } catch (e) {
        console.error("Error loading engine predictions:", e);
    }

    btnAnalyze.addEventListener('click', () => {
        const opponentName = document.getElementById('analysis-opponent').value;
        const location = document.getElementById('analysis-location').value;
        const resultsContainer = document.getElementById('analysis-results');
        
        if (resultsContainer) {
            resultsContainer.classList.remove('hidden');
            analyzeMatch(opponentName, location, standingsData, simulationData, enginePredictions);
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
}

function populateOpponentDropdown(data) {
    const select = document.getElementById('analysis-opponent');
    if (!select || !data || data.length === 0) return;
    
    // Sort teams alphabetically
    const teams = data
        .map(row => row.team)
        .filter(t => t && !t.includes('Lyon') && !t.includes('Olympique Lyonnais')) // Filter out OL
        .sort();
    
    // Keep existing options if needed, but rebuilding is cleaner
    // However, we want to keep the hardcoded ones as fallback or priority?
    // Let's clear and rebuild
    select.innerHTML = '';
    
    teams.forEach(team => {
        const option = document.createElement('option');
        option.value = team;
        option.textContent = team;
        if (team === 'Brest') option.selected = true;
        select.appendChild(option);
    });
}

function analyzeMatch(opponentName, location, data, simulationData, enginePredictions) {
    // Find OL and Opponent rows
    const olRow = data.find(row => row.team.includes('Lyon') || row.team.includes('Olympique Lyonnais'));
    const oppRow = data.find(row => row.team === opponentName);
    
    if (!olRow || !oppRow) {
        console.error("Teams not found");
        return;
    }

    const isOlHome = location === 'home';
    
    // Stats extraction helper
    const getStat = (row, homeKey, awayKey, generalKey) => {
        if (location === 'home') {
            // If OL is Home, we want OL Home stats
            // If Opponent is Home (OL Away), we want Opp Home stats
            // Wait, logic depends on who 'row' is.
            // But here we want:
            // OL Stats for THIS match condition (Home or Away)
            // Opp Stats for THIS match condition (Away or Home)
        }
        // Simpler: Just extract all 3 values and let logic decide
        return {
            home: parseFloat(row[homeKey]),
            away: parseFloat(row[awayKey]),
            general: parseFloat(row[generalKey])
        };
    };

    // Columns map (based on CSV header from previous Read)
    // rank,team,matches,wins,draws,losses,goals_for,goals_against,goal_difference,points,points_per_match,win_rate,goals_for_per_match,goals_against_per_match
    // home_... away_...
    
    // Extract Stats for current context
    // OL
    const olContext = isOlHome ? 'home' : 'away';
    const olAttack = parseFloat(olRow[`${olContext}_goals_for_per_match`]) || parseFloat(olRow.goals_for_per_match);
    const olDefense = parseFloat(olRow[`${olContext}_goals_against_per_match`]) || parseFloat(olRow.goals_against_per_match);
    const olPPM = parseFloat(olRow[`${olContext}_points_per_match`]) || parseFloat(olRow.points_per_match);
    const olRank = parseInt(olRow.rank);

    // Opponent (Opposite context)
    const oppContext = isOlHome ? 'away' : 'home';
    const oppAttack = parseFloat(oppRow[`${oppContext}_goals_for_per_match`]) || parseFloat(oppRow.goals_for_per_match);
    const oppDefense = parseFloat(oppRow[`${oppContext}_goals_against_per_match`]) || parseFloat(oppRow.goals_against_per_match);
    const oppPPM = parseFloat(oppRow[`${oppContext}_points_per_match`]) || parseFloat(oppRow.points_per_match);
    const oppRank = parseInt(oppRow.rank);

    // Update UI Header
    document.getElementById('ol-rank').textContent = `${olRank}${olRank === 1 ? 'er' : 'ème'} (Ligue 1)`;
    document.getElementById('opponent-name').textContent = opponentName;
    document.getElementById('opponent-rank').textContent = `${oppRank}${oppRank === 1 ? 'er' : 'ème'} (Ligue 1)`;

    // Prediction Logic
    let winProb = 50;
    let olScore = 0;
    let oppScore = 0;
    let h2hBonus = 0;
    let rivalryPenalty = 0;
    let injuryPenalty = 0;
    let hasSimulation = false;

    // Check if we have simulation data
    if (simulationData && simulationData.length > 0) {
        const venueTitle = location.charAt(0).toUpperCase() + location.slice(1);
        const simMatch = simulationData.find(m => m.opponent === opponentName && m.venue === venueTitle);
        
        if (simMatch) {
            hasSimulation = true;
            winProb = parseFloat(simMatch.proba_win);
            h2hBonus = parseFloat(simMatch.h2h_bonus || 0);
            rivalryPenalty = parseFloat(simMatch.rivalry_penalty || 0);
            injuryPenalty = parseFloat(simMatch.injury_penalty || 0);
            
            const olGf = parseFloat(simMatch.ol_gf || 0);
            const oppGf = parseFloat(simMatch.opp_gf || 0);
            
            olScore = Math.round(olGf);
            oppScore = Math.round(oppGf);
            
            const xgEl = document.getElementById('pred-xg');
            if (xgEl) xgEl.textContent = olGf.toFixed(2);
        }
    }

    if (!hasSimulation) {
        // Fallback to old logic
        const rankDiff = oppRank - olRank;
        winProb += rankDiff * 2;
        winProb += isOlHome ? 10 : -10;
        
        const ppmDiff = olPPM - oppPPM;
        winProb += ppmDiff * 20;
        winProb = Math.min(95, Math.max(5, Math.round(winProb)));
        
        const olExpectedGoals = (olAttack + oppDefense) / 2;
        const oppExpectedGoals = (oppAttack + olDefense) / 2;
        olScore = Math.round(olExpectedGoals);
        oppScore = Math.round(oppExpectedGoals);
        
        document.getElementById('pred-xg').textContent = olExpectedGoals.toFixed(2);
    }

    if (enginePredictions && enginePredictions.length > 0 && isOlHome) {
        const engineMatch = enginePredictions.find(m => {
            const homeTeam = (m.home_team || m.home || '').toLowerCase();
            const awayTeam = (m.away_team || m.away || '').toLowerCase();
            return homeTeam.includes('lyon') && awayTeam === opponentName.toLowerCase();
        });
        if (engineMatch) {
            const pHome = parseFloat(engineMatch.proba_home_win || engineMatch.home_win);
            if (!isNaN(pHome) && pHome > 0 && pHome <= 1.000001) {
                winProb = Math.round(pHome * 100);
            }
        }
    }
    
    // Update Win Prob UI
    document.getElementById('prob-win').textContent = `${winProb}%`;
    const probBar = document.getElementById('prob-bar');
    probBar.style.width = `${winProb}%`;
    probBar.className = `h-2 rounded-full ${winProb >= 50 ? 'bg-blue-500' : 'bg-red-500'}`;

    // Score Prediction
    document.getElementById('pred-score').textContent = `${olScore} - ${oppScore}`;
    
    // Form Icons
    const formContainer = document.getElementById('form-icons');
    formContainer.innerHTML = generateFormIcons(olPPM);

    // ADD H2H / Rivalry Info (Append)
    if (hasSimulation && (h2hBonus !== 0 || rivalryPenalty !== 0 || injuryPenalty !== 0)) {
        let contextHTML = '<div class="mt-2 pt-2 border-t border-gray-700 flex flex-col gap-1 text-center">';
        
        if (rivalryPenalty > 0) {
            contextHTML += '<div class="text-red-400 font-bold text-xs uppercase tracking-wider">⚠️ Match de Rivalité</div>';
        }
        
        if (h2hBonus > 0) {
            contextHTML += `<div class="text-green-400 text-xs">Historique Favorable (+${h2hBonus.toFixed(1)})</div>`;
        } else if (h2hBonus < 0) {
            contextHTML += `<div class="text-red-400 text-xs">Historique Défavorable (${h2hBonus.toFixed(1)})</div>`;
        }
        
        if (injuryPenalty > 0) {
             contextHTML += `<div class="text-orange-400 text-xs">Impact Blessures (-${injuryPenalty.toFixed(1)})</div>`;
        }
        
        contextHTML += '</div>';
        formContainer.innerHTML += contextHTML;
    }

    // Comparatives
    updateComparison('attack', olAttack, oppAttack);
    updateComparison('defense', olDefense, oppDefense, true);
    updateComparison('ppm', olPPM, oppPPM);
}

function updateComparison(type, val1, val2, lowerIsBetter = false) {
    const el1 = document.getElementById(`comp-ol-${type}`);
    const el2 = document.getElementById(`comp-opp-${type}`);
    
    if (el1) el1.textContent = val1.toFixed(2);
    if (el2) el2.textContent = val2.toFixed(2);
    
    const total = val1 + val2;
    const pct1 = total > 0 ? (val1 / total) * 100 : 50;
    const pct2 = total > 0 ? (val2 / total) * 100 : 50;
    
    const bar1 = document.getElementById(`bar-${type}-ol`);
    const bar2 = document.getElementById(`bar-${type}-opp`);
    
    if (bar1) bar1.style.width = `${pct1}%`;
    if (bar2) bar2.style.width = `${pct2}%`;
}

function generateFormIcons(ppm) {
    let html = '';
    // Generate 5 icons based on PPM
    // PPM 3.0 = W W W W W
    // PPM 1.0 = D L D L D
    // Use a probabilistic approach
    const winProb = ppm / 3;
    const drawProb = (3 - ppm) / 4; // Arbitrary
    
    for (let i = 0; i < 5; i++) {
        const r = Math.random();
        let badgeClass = 'badge-loss';
        let text = 'D';
        
        if (r < winProb) {
            badgeClass = 'badge-win';
            text = 'V';
        } else if (r < winProb + drawProb) {
            badgeClass = 'badge-draw';
            text = 'N';
        }
        
        html += `<span class="badge ${badgeClass} w-8 h-8 flex items-center justify-center rounded-full text-xs text-white font-bold" style="background-color: ${badgeClass === 'badge-win' ? '#10B981' : badgeClass === 'badge-draw' ? '#F59E0B' : '#EF4444'}">${text}</span>`;
    }
    return html;
}

function loadTeamStyles() {
    const select = document.getElementById('styles-context');
    const lowEl = document.getElementById('style-low-block');
    const compactEl = document.getElementById('style-compact');
    const highEl = document.getElementById('style-high-line');
    const spacesEl = document.getElementById('style-spaces');
    if (!select || !lowEl || !compactEl || !highEl || !spacesEl) return;
    let data = [];
    let adv = [];
    let hasAdvanced = false;
    fetch(cacheBust('data/processed/ligue1_team_advanced_stats.csv'))
        .then(r => {
            if (!r.ok) throw new Error();
            return r.text();
        })
        .then(t => {
            adv = parseCSV(t).filter(r => r.team && !/Lyon/i.test(r.team));
            hasAdvanced = adv && adv.length > 0;
        })
        .catch(() => {})
        .finally(() => {
            fetch(cacheBust('data/processed/league1_standings_home_away.csv'))
                .then(r => r.text())
                .then(t => {
                    data = parseCSV(t).filter(r => r.team && !/Lyon/i.test(r.team));
                    renderStyles();
                    select.addEventListener('change', renderStyles);
                })
                .catch(() => {});
        });
    function renderStyles() {
        const ctx = select.value;
        const getStd = (row) => {
            if (ctx === 'home') {
                return {
                    gf: parseFloat(row.home_goals_for_per_match),
                    ga: parseFloat(row.home_goals_against_per_match),
                    wr: parseFloat(row.home_win_rate)
                };
            } else if (ctx === 'away') {
                return {
                    gf: parseFloat(row.away_goals_for_per_match),
                    ga: parseFloat(row.away_goals_against_per_match),
                    wr: parseFloat(row.away_win_rate)
                };
            } else {
                return {
                    gf: parseFloat(row.goals_for_per_match),
                    ga: parseFloat(row.goals_against_per_match),
                    wr: parseFloat(row.win_rate)
                };
            }
        };
        const getAdv = (teamName) => {
            const row = adv.find(r => r.team === teamName);
            if (!row) return null;
            return {
                poss: parseFloat(row.possession_pct),
                sh90: parseFloat(row.shots_per90),
                xgpm: parseFloat(row.xg_per_match),
                xgapm: parseFloat(row.xga_per_match)
            };
        };
        const low = [];
        const compact = [];
        const high = [];
        const spaces = [];
        data.forEach(row => {
            const s = getStd(row);
            const name = row.team;
            if (!isFinite(s.gf) || !isFinite(s.ga)) return;
            let isLow = s.gf <= 1.3 && s.ga <= 1.1;
            let isCompact = s.ga <= 1.0 && s.gf > 1.3 && s.gf <= 1.6;
            let isHigh = s.gf >= 1.7 && (s.ga >= 1.2 || s.wr >= 65);
            let isSpaces = s.ga >= 1.5 || (ctx === 'away' && s.ga >= 1.7);
            if (hasAdvanced) {
                const a = getAdv(name);
                if (a) {
                    isLow = (a.poss <= 46 && a.xgapm <= 1.1) || isLow;
                    isCompact = (a.xgapm <= 1.0 && a.poss >= 46 && a.poss <= 53) || isCompact;
                    isHigh = (a.poss >= 54 && a.sh90 >= 14 && a.xgpm >= 1.6) || isHigh;
                    isSpaces = (a.xgapm >= 1.4) || isSpaces;
                }
            }
            if (isLow) low.push({name, s});
            else if (isCompact) compact.push({name, s});
            if (isHigh) high.push({name, s});
            if (isSpaces) spaces.push({name, s});
        });
        const sortFn = (a,b)=> (b.s.gf - a.s.gf) || (a.name.localeCompare(b.name));
        low.sort(sortFn);
        compact.sort(sortFn);
        high.sort(sortFn);
        spaces.sort((a,b)=> (b.s.ga - a.s.ga) || (a.name.localeCompare(b.name)));
        const renderList = (el, arr) => {
            el.innerHTML = arr.map(item => 
                `<li class="flex items-center justify-between bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2">
                    <span class="font-medium">${item.name}</span>
                    <span class="text-xs text-gray-400">GF/M ${item.s.gf.toFixed(2)} • GA/M ${item.s.ga.toFixed(2)}</span>
                </li>`
            ).join('');
        };
        renderList(lowEl, low.slice(0, 10));
        renderList(compactEl, compact.slice(0, 10));
        renderList(highEl, high.slice(0, 10));
        renderList(spacesEl, spaces.slice(0, 10));
    }
}

function loadHomeStats() {
    const setText = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    fetch(cacheBust('data/processed/league1_standings_home_away.csv'))
        .then(r => r.text())
        .then(t => {
            const rows = parseCSV(t);
            if (!rows || rows.length === 0) return;
            const leader = rows.reduce((acc, cur) => {
                const rk = parseInt(cur.rank);
                if (!acc || rk < parseInt(acc.rank)) return cur;
                return acc;
            }, null);
            const ol = rows.find(r => /Lyon|Olympique Lyonnais/i.test(r.team));
            if (leader) {
                setText('hero-rank-value', `${leader.team} ${parseInt(leader.rank)}${parseInt(leader.rank)===1?'er':'ème'}`);
                setText('hero-rank-label', 'Classement Ligue 1 (leader)');
            }
            if (ol) {
                setText('hero-rating-value', `${parseInt(ol.points)} pts`);
                setText('hero-ol-rank-value', `${parseInt(ol.rank)}${parseInt(ol.rank)===1?'er':'ème'}`);
            }
        })
        .catch(() => {});
    Promise.all([
        fetch(cacheBust('data/processed/ol_match_score_final.csv'))
            .then(r => r.text())
            .then(t => {
                const rows = parseCSV(t) || [];
                setText('hero-matches-value', `${rows.length}`);
            })
            .catch(() => {}),
        fetch(cacheBust('data/processed/ol_best_combos_2_players.csv'))
            .then(r => r.text())
            .then(t => {
                const rows = parseCSV(t) || [];
                setText('hero-combos-value', `${rows.length}`);
            })
            .catch(() => {})
    ]);
}

function loadPreviewMatches() {
    const tbody = document.getElementById('preview-matches-tbody');
    if (!tbody) return;
    fetch(cacheBust('data/processed/ol_match_score_final.csv'))
        .then(r => r.text())
        .then(t => {
            const rows = parseCSV(t) || [];
            rows.sort((a, b) => new Date(b.date) - new Date(a.date));
            const latest = rows.slice(0, 3);
            tbody.innerHTML = latest.map(m => {
                const badge = m.result === 'W' ? 'badge badge-win' : m.result === 'D' ? 'badge badge-draw' : 'badge badge-loss';
                const label = m.result === 'W' ? 'Victoire' : m.result === 'D' ? 'Nul' : 'Défaite';
                const rating = parseFloat(m.match_rating || 0).toFixed(1);
                return `<tr>
                    <td>${formatDate(m.date)}</td>
                    <td>${m.opponent || ''}</td>
                    <td><span class="${badge}">${label}</span></td>
                    <td>${rating}</td>
                </tr>`;
            }).join('');
        })
        .catch(() => {
            tbody.innerHTML = '<tr><td colspan="4" class="error">Erreur lors du chargement des données</td></tr>';
        });
}
