# TradeMe Feedback Scraper

A simple Python web scraper that retrieves listing details from a given user's feedback and outputs then as a csv.

## Getting Started

I reccomend using a virtualenv
```
python3 -m venv venv
./venv/scripts/activate
```

Install the required dependencies
```
pip install -r requirements.txt
```

Run the script with the desired parameters
```
python3 scraper.py -m <memberId> -o <outputFile> -l <limit> -p <page>
```