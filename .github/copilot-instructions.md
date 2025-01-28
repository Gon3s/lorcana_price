# GitHub Copilot Instructions

## Project Overview
Lorcana Price Tracker: A tool for tracking card prices across different platforms (Cardmarket, Vinted, etc.)

## Code Structure
- `src/`
  - `main.py`: Entry point, argument parsing and main logic
  - `sheets.py`: Google Sheets integration and data management
  - `models/`: Data models using Pydantic
  - `scrapers/`: Price scrapers for different platforms
  - `utils/`: Shared utilities (logging, etc.)

## Conventions

### File Organization
- One scraper per platform in `src/scrapers/`
- Models in `src/models/`
- Shared utilities in `src/utils/`

### Coding Style
- Use Python type hints
- Document functions with docstrings
- Use Pydantic for data models
- Use logging instead of print statements
- Follow PEP 8 conventions

### Error Handling
- Use try/except blocks with specific exceptions
- Log errors with appropriate level (error, warning, info)
- Return Optional types for functions that might fail

### Google Sheets Integration
- Use column constants defined in sheets.py
- Follow existing patterns for sheet updates
- Maintain price history with minimum values

### Price Scraping
- Use SeleniumBase for web scraping
- Handle timeouts and retries
- Parse prices consistently (handle €, commas, etc.)
- Store minimum prices and update timestamps

### Commits
- Use gitmoji in commit messages
- Follow conventional commits format
- Keep commits focused and atomic

## Common Patterns

### Adding a New Price Source
1. Create scraper in `src/scrapers/`
2. Define price info model in `models/`
3. Add column constants in `sheets.py`
4. Update sheet structure documentation
5. Add source to CLI arguments

### Updating Prices
```python
try:
    # Fetch current min price
    current_min = get_current_min()
    
    # Update only if new price is lower
    new_min = min(current_min, new_price)
    
    # Store with timestamp
    update_price(new_min, datetime.now())
except Exception as e:
    logger.error(f"Error updating price: {e}")
```

### Handling Retries
```python
for attempt in range(max_retries):
    try:
        # Attempt operation
        break
    except Exception as e:
        if attempt < max_retries - 1:
            logger.warning(f"Attempt {attempt + 1} failed")
            time.sleep(delay)
        else:
            logger.error(f"All attempts failed: {e}")
```
