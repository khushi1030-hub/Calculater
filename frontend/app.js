/**
 * Scientific Calculator Frontend
 *
 * This module handles:
 * - UI interactions (button clicks, keyboard)
 * - Expression building and display
 * - Communication with the backend API
 * - History management
 * - Theme toggling
 */

class CalculatorApp {
    constructor() {
        this.state = {
            expression: '',
            result: 0,
            history: [],
            theme: localStorage.getItem('theme') || 'dark',
            // Extract API base from URL (injected by desktop launcher or standalone deployment)
            apiBase: this.getApiBase()
        };

        this.elements = {
            expressionDisplay: document.getElementById('expressionDisplay'),
            resultDisplay: document.getElementById('resultDisplay'),
            historyList: document.getElementById('historyList'),
            historyPanel: document.getElementById('historyPanel'),
            themeToggle: document.getElementById('themeToggle')
        };

        this.bindEvents();
        this.applyTheme();
        this.loadHistory();
        this.updateDisplay();
    }

    // Extract API base URL from query parameter or use current origin
    getApiBase() {
        const urlParams = new URLSearchParams(window.location.search);
        // If the desktop launcher injects api_base parameter, use it
        const apiBase = urlParams.get('api_base') || window.location.origin;
        return apiBase;
    }

    bindEvents() {
        // Button clicks
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleButtonClick(btn));
        });

        // Keyboard support
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Theme toggle
        this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());

        // History panel toggle
        this.elements.resultDisplay.addEventListener('dblclick', () => {
            this.elements.historyPanel.style.display =
                this.elements.historyPanel.style.display === 'none' ? 'block' : 'none';
        });

        // Clear history on right-click of history header
        this.elements.historyPanel.querySelector('h3').addEventListener('contextmenu', (e) => {
            e.preventDefault();
            if (confirm('Clear history?')) {
                this.clearHistory();
            }
        });
    }

    handleButtonClick(button) {
        // Visual feedback
        button.classList.add('pressed');
        setTimeout(() => button.classList.remove('pressed'), 200);

        const action = button.dataset.action;
        const value = button.dataset.value;
        const func = button.dataset.func;
        const constValue = button.dataset.const;

        if (action) {
            this.handleAction(action);
        } else if (value !== undefined) {
            this.appendToExpression(value);
        } else if (func) {
            this.appendFunction(func);
        } else if (constValue) {
            this.appendConstant(constValue);
        }
    }

    handleAction(action) {
        switch (action) {
            case 'clear':
                this.clear();
                break;
            case 'backspace':
                this.backspace();
                break;
            case 'equals':
                this.calculate();
                break;
            default:
                console.warn(`Unknown action: ${action}`);
        }
    }

    appendToExpression(value) {
        // Prevent multiple decimal points in a number
        if (value === '.') {
            const lastNumber = this.getCurrentNumber();
            if (lastNumber.includes('.')) return;
        }

        this.state.expression += value;
        this.updateDisplay();
    }

    appendFunction(funcName) {
        // Auto-open parenthesis for functions
        this.state.expression += `${funcName}(`;
        this.updateDisplay();
    }

    appendConstant(constValue) {
        // Map for display symbols
        const displaySymbols = {
            'pi': 'π',
            'e': 'e'
        };
        const displaySymbol = displaySymbols[constValue] || constValue;

        // For calculation, we need the actual numeric value
        const evalValues = {
            'pi': Math.PI,
            'e': Math.E
        };
        const evalValue = evalValues[constValue] || constValue;

        // Append the actual numeric value to the expression for calculation
        this.state.expression += evalValue;
        this.updateDisplay();
    }

    clear() {
        this.state.expression = '';
        this.state.result = 0;
        this.updateDisplay();
    }

    backspace() {
        this.state.expression = this.state.expression.slice(0, -1);
        this.updateDisplay();
    }

    calculate() {
        if (!this.state.expression.trim()) return;

        // Show calculating state
        this.elements.resultDisplay.textContent = '=';
        this.elements.resultDisplay.style.opacity = '0.7';

        // Send request to backend
        fetch(`${this.state.apiBase}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expression: this.state.expression })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.detail || 'Calculation error'); });
            }
            return response.json();
        })
        .then(data => {
            this.state.result = data.result;
            this.addToHistory(this.state.expression, this.state.result);
            this.state.expression = data.result.toString(); // Show result as new expression
            this.updateDisplay();
            this.saveHistory();
        })
        .catch(error => {
            this.elements.resultDisplay.textContent = 'Error';
            setTimeout(() => {
                this.elements.resultDisplay.textContent = this.state.result || 0;
            }, 1500);
            console.error('Calculation error:', error);
        });
    }

    getCurrentNumber() {
        const match = this.state.expression.match(/[+\-*/^()]([^+\-*/^()]*)$/);
        return match ? match[1] : this.state.expression;
    }

    updateDisplay() {
        this.elements.expressionDisplay.textContent = this.state.expression || '';
        this.elements.resultDisplay.textContent = this.state.result !== undefined && this.state.result !== null
            ? `= ${this.state.result}`
            : '= 0';

        // Auto-scroll expression if too long
        if (this.state.expression.length > 20) {
            this.elements.expressionDisplay.scrollLeft =
                this.elements.expressionDisplay.scrollWidth;
        }
    }

    addToHistory(expression, result) {
        const entry = {
            expression: expression,
            result: result,
            timestamp: new Date().toISOString()
        };
        this.state.history.unshift(entry); // Most recent first
        this.renderHistory();
    }

    renderHistory() {
        this.elements.historyList.innerHTML = '';
        this.state.history.slice(0, 20).forEach((entry, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="expr">${escapeHtml(entry.expression)} = </span>
                <span class="result">${escapeHtml(String(entry.result))}</span>
                <small>${new Date(entry.timestamp).toLocaleTimeString()}</small>
            `;
            li.onclick = () => {
                this.state.expression = entry.expression;
                this.state.result = entry.result;
                this.updateDisplay();
                this.elements.historyPanel.style.display = 'none';
            };
            this.elements.historyList.appendChild(li);
        });
    }

    loadHistory() {
        const saved = localStorage.getItem('calcHistory');
        if (saved) {
            try {
                this.state.history = JSON.parse(saved);
            } catch (e) {
                console.warn('Failed to parse history from localStorage', e);
                this.state.history = [];
            }
        }
        this.renderHistory();
    }

    saveHistory() {
        localStorage.setItem('calcHistory', JSON.stringify(this.state.history));
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear the history?')) {
            this.state.history = [];
            this.renderHistory();
            this.saveHistory();
        }
    }

    toggleTheme() {
        const newTheme = this.state.theme === 'dark' ? 'light' : 'dark';
        this.state.theme = newTheme;
        localStorage.setItem('theme', newTheme);
        this.applyTheme();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.state.theme);
        const sunIcon = this.elements.themeToggle.querySelector('.sun-icon');
        const moonIcon = this.elements.themeToggle.querySelector('.moon-icon');
        if (sunIcon && moonIcon) {
            sunIcon.style.display = this.state.theme === 'dark' ? 'none' : 'block';
            moonIcon.style.display = this.state.theme === 'dark' ? 'block' : 'none';
        }
    }

    handleKeyPress(event) {
        const key = event.key;

        // Allow only certain keys to prevent interfering with browser shortcuts
        if (/[0-9+\-*/^().]/.test(key)) {
            event.preventDefault();
            this.appendToExpression(key);
        } else if (key === 'Enter' || key === '=') {
            event.preventDefault();
            this.calculate();
        } else if (key === 'Backspace') {
            event.preventDefault();
            this.backspace();
        } else if (key === 'Escape') {
            event.preventDefault();
            this.clear();
        } else if (key.toLowerCase() === 'c') {
            event.preventDefault();
            this.clear();
        }
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&',
        '<': '<',
        '>': '>',
        '"': '"',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.calculatorApp = new CalculatorApp();
});