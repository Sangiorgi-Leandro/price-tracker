# Price Tracker

An asynchronous Python web scraper designed to monitor the price of the **Samsung Galaxy S23 256 GB** across multiple popular e-commerce sites: Amazon.it, Phoneclick.it, and Teknozone.it.

This project leverages modern Python features for efficient and robust web scraping. It executes parallel requests using `asyncio` and `aiohttp`, implements sophisticated retry and back-off strategies via `Tenacity`, and ensures accurate price parsing with `decimal.Decimal`. The collected data is outputted as both a current snapshot (JSON) and a continuous historical record (CSV).

---

## 🚀 Features

- **Asynchronous Scraping**: Efficiently scrapes multiple websites in parallel for faster data collection.
- **Resilient HTTP Client**: Utilizes a shared HTTP client with configurable retries and exponential back-off to handle temporary network issues and server responses gracefully.
- **Robust Price Parsing**: Employs advanced techniques, including regular expressions and `Decimal` normalization, to accurately extract and format prices from varied HTML structures.
- **Randomized Rate Limiting**: Implements random pauses between requests to mimic human behavior and reduce the likelihood of triggering anti-bot measures.
- **Structured Logging**: Provides comprehensive logging to both the console and a rotating file (`scraper.log`), aiding in monitoring and debugging.
- **Flexible Outputs**:
  - `data/latest_prices.json`: A snapshot of the most recently scraped prices.
  - `data/price_history.csv`: A continuously appended historical record of all collected prices.

---

## 📂 Project Structure
```
├── config.py             # Centralized configuration for URLs, headers, timeouts, and environment variable overrides.
├── logger.py             # Sets up application-wide logging with a RotatingFileHandler.
├── http_client.py        # A robust aiohttp.ClientSession wrapper with Tenacity for retries.
├── main.py               # The main orchestrator script: runs scrapers, saves data, and prints a summary report.
├── scraper/              # Directory containing individual scraper modules for each website.
│   ├── amazon.py         # Specific scraper logic for Amazon.it.
│   ├── phoneclick.py     # Specific scraper logic for Phoneclick.it.
│   └── teknozone.py      # Specific scraper logic for Teknozone.it.
├── data/                 # Output folder for generated JSON and CSV files (ignored by Git).
├── .gitignore            # Specifies files and directories that Git should ignore (e.g., virtual environments, data).
└── requirements.txt      # Lists all necessary Python dependencies for the project.
```


---

## ⚙️ Prerequisites

To run this project, you'll need:

- **Python 3.8 or newer**
- **`pip`** (Python package installer)

---

## 🛠️ Installation

Follow these steps to get the project up and running on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Sangiorgi-Leandro/price-tracker.git
cd price-tracker
    ```

2.  **(Recommended) Create and activate a virtual environment:**
    It's best practice to use a virtual environment to manage project dependencies isolation.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    This command will install all required Python libraries listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

---

## 🔧 Configuration

All project settings are defined in `config.py`. For maximum flexibility and to avoid hard-coding sensitive information (like specific URLs if you want to track different products), most settings can be easily overridden using **environment variables**.

| Environment Variable    | Default Value in `config.py` | Description                                                                    |
| :---------------------- | :--------------------------- | :----------------------------------------------------------------------------- |
| `SCRAPER_DATA_DIR`      | `data`                       | Output folder for JSON/CSV files.                                              |
| `SCRAPER_JSON_FILE`     | `latest_prices.json`         | Filename for the latest price snapshot (JSON).                                 |
| `SCRAPER_CSV_FILE`      | `price_history.csv`          | Filename for the continuous price history (CSV).                               |
| `SCRAPER_TIMEOUT`       | `15`                         | HTTP request timeout in seconds.                                               |
| `SCRAPER_RETRIES`       | `3`                          | Number of retry attempts for failed HTTP requests.                             |
| `SCRAPER_RATE_LIMIT`    | `1,3`                        | Comma-separated min and max seconds for random pause between requests (e.g., "1,5"). |
| `SCRAPER_USER_AGENT`    | _(Randomly chosen)_ | Forces a specific User-Agent string instead of a randomly selected one.        |
| `SCRAPER_AMAZON_URL`    | _See `config.py`_ | Full product URL for Amazon.it to scrape.                                      |
| `SCRAPER_PHONECLICK_URL`| _See `config.py`_ | Full product URL for Phoneclick.it to scrape.                                  |
| `SCRAPER_TEKNOZONE_URL` | _See `config.py`_ | Full product URL for Teknozone.it to scrape.                                   |
| `SCRAPER_ACCEPT_LANGUAGE`| `en-US,en;q=0.9,it;q=0.8`   | The `Accept-Language` header for HTTP requests.                              |

---

## ▶️ Usage

Once installed and configured, running the scraper is straightforward:
```
bash
python main.py
```


Upon completion of the scraping process:

    The data/latest_prices.json file will contain the most recent price snapshot.

    The data/price_history.csv file will be appended with new price entries, building a historical record.

    A human-readable summary of the current tracking results will be printed directly to your console.

    Detailed operational logs will be written to scraper.log.


## 🔭 Possible Extensions

This project provides a solid foundation for building an advanced price tracking system. Here are some ideas for potential enhancements:

- **Real-Time Notifications**  
  Integrate with messaging platforms such as Slack or Telegram to send automatic alerts when prices change or drop significantly.

- **Database Integration**  
  Store scraped data in a structured database for more efficient management (e.g., SQLite for simplicity, PostgreSQL for scalability, MongoDB for flexibility).

- **Web Dashboard**  
  Develop a user-friendly web interface using frameworks like Flask, Django, or Streamlit to visualize price trends and historical data interactively.

- **Automated Scheduling**  
  Schedule periodic scraping runs using tools like `cron` (Linux), **Task Scheduler** (Windows), **Airflow**, or **Celery**.

- **Containerization & CI/CD**  
  Package the application with **Docker** and implement Continuous Integration/Deployment pipelines for automated testing and deployment.


---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, feel free to contribute by following these steps:

1.  **Fork the repository**
    [🔗 Fork on GitHub](https://github.com/Sangiorgi-Leandro/price-tracker/fork)

2.  **Create a new branch**
    ```bash
    git checkout -b feature/your-feature-name
    ```

3.  **Make your changes**


4.  **Commit your changes**
    ```bash
    git commit -m "Add new feature"
    ```

5.  **Push to your branch**
    ```bash
    git push origin feature/your-feature-name
    ```

6.  **Open a Pull Request** and describe your changes clearly

Thank you for your contribution!

---

## 📜 License
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it for personal or commercial purposes.

