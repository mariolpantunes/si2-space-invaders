import { GameClient } from '/aigf/framework.js';

const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const livesEl = document.getElementById('lives');
const highScoreEl = document.getElementById('high_score');
const statusEl = document.getElementById('status');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');

const TILE_SIZE = 40;
let width = 11;
let height = 11;

// Nord Palette
const NORD = {
    nord0: "#2e3440",
    nord1: "#3b4252",
    nord2: "#434c5e",
    nord3: "#4c566a",
    nord4: "#d8dee9",
    nord5: "#e5e9f0",
    nord6: "#eceff4",
    nord7: "#8fbcbb",
    nord8: "#88c0d0", // player color alternative
    nord9: "#81a1c1",
    nord10: "#5e81ac",
    nord11: "#bf616a", // red (aliens)
    nord12: "#d08770", // orange (diving aliens)
    nord13: "#ebcb8b", // yellow (lasers)
    nord14: "#a3be8c", // green (player spaceship)
    nord15: "#b48ead"  // purple
};

// Initialize canvas size immediately
canvas.width = width * TILE_SIZE;
canvas.height = height * TILE_SIZE;

const client = new GameClient(8765);

client.onSetup = (data) => {
    width = data.width;
    height = data.height;
    canvas.width = width * TILE_SIZE;
    canvas.height = height * TILE_SIZE;
};

client.onUpdate = (data) => {
    scoreEl.innerText = data.score;
    livesEl.innerText = data.lives;
    highScoreEl.innerText = data.high_score;
    
    const state = data._framework.state;
    statusEl.innerText = state;
    statusEl.className = 'badge ' + (state === 'RUNNING' ? 'badge-running' : 'badge-lobby');
    
    draw(data);
};

startBtn.onclick = () => client.sendCommand('START');
resetBtn.onclick = () => client.sendCommand('RESET');

function draw(state) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid background dots (sleek arcade matrix style)
    ctx.fillStyle = NORD.nord2;
    for (let x = 0; x < width; x++) {
        for (let y = 0; y < height; y++) {
            ctx.beginPath();
            ctx.arc(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2, 1.5, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Draw lasers (yellow glowing vertical lines)
    if (state.lasers) {
        state.lasers.forEach(laser => {
            ctx.fillStyle = NORD.nord13;
            ctx.fillRect(
                laser.x * TILE_SIZE + TILE_SIZE / 2 - 2, 
                canvas.height - (laser.y + 1) * TILE_SIZE, 
                4, 
                15
            );
        });
    }

    // Draw Aliens (normal = red, diving = orange)
    if (state.aliens) {
        state.aliens.forEach(alien => {
            if (!alien.active) return;
            
            const ax = alien.x * TILE_SIZE + TILE_SIZE / 2;
            const ay = canvas.height - (alien.y + 1) * TILE_SIZE + TILE_SIZE / 2;
            
            // Outer warning ring for diving alien
            if (alien.is_diving) {
                ctx.strokeStyle = NORD.nord12;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(ax, ay, TILE_SIZE / 2 - 2, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Solid invader body
            ctx.fillStyle = alien.is_diving ? NORD.nord12 : NORD.nord11;
            ctx.beginPath();
            ctx.arc(ax, ay, TILE_SIZE / 2 - 6, 0, Math.PI * 2);
            ctx.fill();

            // Tiny eyes for fun invader detail
            ctx.fillStyle = NORD.nord6;
            ctx.fillRect(ax - 5, ay - 3, 2, 2);
            ctx.fillRect(ax + 3, ay - 3, 2, 2);
        });
    }

    // Draw Player Spaceship (North-pointing Green Triangle)
    ctx.fillStyle = NORD.nord14;
    ctx.beginPath();
    const px = state.player_x * TILE_SIZE + TILE_SIZE / 2;
    const py = canvas.height - (state.player_y + 1) * TILE_SIZE + TILE_SIZE / 2;
    ctx.moveTo(px, py - 14);
    ctx.lineTo(px - 14, py + 14);
    ctx.lineTo(px + 14, py + 14);
    ctx.closePath();
    ctx.fill();

    // Subtle thruster glow
    ctx.fillStyle = NORD.nord12;
    ctx.fillRect(px - 4, py + 14, 8, 4);

    // Draw Game Over Screen
    if (state.game_over) {
        ctx.fillStyle = 'rgba(46, 52, 64, 0.85)'; // Nord0 with opacity
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = NORD.nord11;
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 40);
        
        ctx.fillStyle = NORD.nord6;
        ctx.font = 'bold 24px Arial';
        ctx.fillText(`Final Score: ${state.score}`, canvas.width / 2, canvas.height / 2 + 10);
        ctx.fillText(`Max Score: ${state.high_score}`, canvas.width / 2, canvas.height / 2 + 50);
    }
}
