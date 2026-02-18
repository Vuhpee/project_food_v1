# Barcode-Based Macro Tracking System

A Python-based nutrition tracking application that retrieves product data via barcode input, scales nutritional values based on consumed portion size, and stores macro intake history in a relational database.

This project was developed as a final project for CS50.

---

## Project Overview

The application allows users to:

- Enter a product barcode
- Retrieve nutritional data (kcal, protein, carbs, fat per 100g) via API
- Input consumed portion size
- Automatically calculate scaled macronutrient intake
- Store consumption records in a relational SQLite database
- Aggregate total macro intake over time
- Export structured macro data for visualization

---

## Architecture

- **Python CLI application**
- External REST API integration (Open Food Facts)
- SQLite relational database (Brand → Product → Consumed)
- Portion-based macro scaling logic
- Aggregated macro calculations
- JavaScript data export for lightweight visualization

---

## Tech Stack

- Python
- REST API integration
- SQLite
- SQL queries
- Data modeling
- CLI interaction

---

## Key Features

- Barcode-based product lookup
- Macro scaling per gram consumed
- Insert-or-ignore + update logic for persistent tracking
- Per-product and total macro aggregation
- Data export for visualization

---

## Skills Demonstrated

- API consumption and JSON parsing
- Relational schema design
- SQL data persistence
- Data transformation and aggregation
- Backend application logic design
