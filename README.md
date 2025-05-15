# Digital Bee 🐝

A data collection and visualization system for bee hive monitoring with weather correlation.

![Project Banner](https://spudsmart.com/wp-content/uploads/2017/08/honey-bee-banner.jpg)

## Installation 🛠️
Choose between docker setup and self setup

### Docker Setup
```bash
#If Docker installed and started
docker compose up
```

### Self Setup
```bash
# Clone repository
git clone https://github.com/yourusername/digital-bee.git
cd digital-bee

# Create and configure environment file
cp .env.example .env

# Make init script executable
chmod +x init_script.sh

# Run initialization
./init_script.sh

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r dashboard/requirements.txt
pip install -r data_collector/equirements.txt

# Start data collection
python data_collector/data_collector.py

# Start dashboard
python dashboard/dashboard.py