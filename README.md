# Scientific Calculator

A hybrid desktop/web calculator with scientific functions, implemented in Python.

## Features

- Basic arithmetic: `+`, `-`, `*`, `/`, `^` (exponentiation)
- Scientific functions:
  - Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
  - Logarithmic: `log` (base 10), `ln` (natural)
  - Exponential: `exp`
  - Other: `sqrt`, `pow` (power function)
- Constants: `π` (pi), `e` (Euler's number)
- Expression parsing with parentheses and operator precedence
- History tracking
- Dark/Light theme support
- Keyboard input support
- Responsive design

## Architecture

The calculator uses a hybrid approach:
- **Backend**: FastAPI server providing calculation API
- **Frontend**: HTML/CSS/JS user interface
- **Desktop Mode**: PyWebView wrapper for native desktop experience
- **Web Mode**: Can be run as a standard web application

## Project Structure

```
calculator/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── calculator.py    # Core calculator logic
│   └── models.py        # Pydantic data models
├── frontend/
│   ├── index.html       # Calculator UI
│   ├── style.css        # Styling
│   └── app.js           # Frontend logic
├── desktop/
│   └── run.py           # Desktop launcher (PyWebView)
├── tests/
│   └── calc_tests.py    # Unit tests
├── requirements.txt
└ README.md
```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### As Desktop Application
```bash
python desktop/run.py
```
This will start the backend server and open a native desktop window.

### As Web Application
1. Start the backend server:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. Open your browser to `http://localhost:8000`

## Running Tests

Unit tests for the calculator logic are available:
```bash
python -m unittest tests.calc_tests -v
```
or
```bash
pytest tests/calc_tests.py -v
```

## API Endpoints

The backend provides the following API endpoints:

- `POST /calculate`: Evaluate a mathematical expression
  - Body: `{ "expression": "2 + 3 * 4" }`
  - Response: `{ "result": 14, "expression": "2 + 3 * 4" }`

- `GET /functions`: List available scientific functions
- `GET /constants`: List available mathematical constants
- `GET /health`: Health check

## Development

### Backend
The core calculation logic is in `backend/calculator.py`. It implements a safe expression evaluator using the shunting-yard algorithm (no `eval`).

### Frontend
The UI is in `frontend/`:
- `index.html`: Structure
- `style.css`: Styling with dark/light theme support
- `app.js`: Application logic handling UI events and API communication

### Desktop Wrapper
`desktop/run.py` uses PyWebView to create a native window hosting the web frontend.

## Design Decisions

1. **Safe Expression Evaluation**: Uses tokenizer and shunting-yard algorithm instead of `eval()` for security.
2. **Hybrid Architecture**: Allows running as both desktop app and web app from same codebase.
3. **Extensible**: Adding new functions requires updating `FUNCTIONS` dict in `calculator.py` and frontend button definitions.
4. **Persistent History**: Uses localStorage to maintain calculation history between sessions.

## Future Enhancements

- Memory functions (store/recall)
- Unit conversion capabilities
- Graphing capabilities
- Improved error display in UI
- Configurable precision/rounding
- Additional scientific functions (hyperbolic, factorial, etc.)

## License

MIT License - feel free to modify and distribute as needed.