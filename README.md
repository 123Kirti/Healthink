# 🏥 Healthink - Government Health Scheme Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.0-363636.svg)](https://soliditylang.org/)
[![Web3](https://img.shields.io/badge/Web3.py-6.8.0-green.svg)](https://web3py.readthedocs.io/)

A comprehensive **full-stack health insurance scheme management system** that bridges the gap between citizens and government health schemes through secure, transparent, and accessible digital platforms.

## 🌟 Features

### 🔐 **Multi-Role Access Control**
- **Patient Portal**: Submit medical records, upload prescriptions, track claims
- **Hospital Portal**: Manage patient data, update profiles, view assigned records
- **Admin Portal**: Audit all records, monitor scheme usage, blockchain verification

### 🛡️ **Security & Privacy**
- **Data Encryption**: SHA-256 hashing for all medical records
- **Blockchain Integration**: Immutable audit trails using Ethereum smart contracts
- **Secure File Uploads**: Safe prescription image storage
- **Role-Based Authentication**: Granular access control

### 📊 **Comprehensive Management**
- **Health Scheme Database**: Pre-loaded with major Indian government schemes
- **Digital Records**: Complete medical history management
- **Real-time Monitoring**: Live dashboard for administrators
- **Transparent Auditing**: Blockchain-verified transaction history

### 🎨 **Modern User Experience**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Clean navbar with role-based sections
- **Interactive Dashboards**: Dynamic data visualization
- **File Upload Support**: Drag-and-drop prescription uploads

## 🚀 Tech Stack

### Backend
- **Python Flask** - RESTful API development
- **SQLite** - Lightweight database management
- **Web3.py** - Ethereum blockchain integration
- **Werkzeug** - Secure file handling

### Frontend
- **Vanilla JavaScript** - Interactive user interfaces
- **HTML5/CSS3** - Modern responsive design
- **Fetch API** - Asynchronous data communication

### Blockchain
- **Solidity** - Smart contract development
- **Truffle** - Contract compilation and deployment
- **Ganache** - Local blockchain development
- **Web3.js** - Frontend blockchain interaction

## 📋 Prerequisites

Before running Healthink, ensure you have:
- **Python 3.8+** with pip
- **Node.js 14+** and npm
- **Git** for version control
- **Ganache** (local blockchain) or access to testnet
- **MetaMask** browser extension (optional, for full blockchain features)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/123Kirti/Healthink.git
cd Healthink
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
```bash
# Initialize database schema
cd database
python init_db.py

# Seed with sample data
python seed_db.py
```

### 4. Blockchain Setup (Optional)
```bash
# Install Truffle globally
npm install -g truffle

# Start local blockchain (Ganache)
# Option A: GUI - Download from https://www.trufflesuite.com/ganache
# Option B: CLI
npm install -g ganache-cli
ganache-cli

# Deploy smart contract
cd ../blockchain
truffle migrate --network development
```

### 5. Start the Application

**Terminal 1 - Backend Server:**
```bash
cd backend
python app.py
```
Server runs at: `http://localhost:5000`

**Terminal 2 - Frontend Server:**
```bash
cd frontend
python -m http.server 3000
```
Frontend available at: `http://localhost:3000`

## 🎯 Usage

### For Patients
1. **Register/Login** as a patient
2. **Select Hospital** from available network
3. **Choose Health Scheme** (optional)
4. **Submit Medical Details** with prescription upload
5. **Track Records** in personal dashboard

### For Hospitals
1. **Update Profile** with hospital information
2. **Manage Camp Details** and services
3. **Review Patient Records** assigned to your hospital
4. **Process Claims** securely

### For Administrators
1. **Audit All Records** with blockchain verification
2. **Monitor System Usage** and statistics
3. **Verify Transactions** on the blockchain
4. **Manage Scheme Data**

## 📁 Project Structure

```
Healthink/
├── 📁 backend/                    # Flask REST API
│   ├── app.py                     # Main application server
│   ├── requirements.txt           # Python dependencies
│   └── 📁 database/              # Database management
│       ├── init_db.py            # Schema initialization
│       ├── seed_db.py            # Sample data seeding
│       └── healthink.db          # SQLite database
├── 📁 blockchain/                # Ethereum smart contracts
│   ├── 📁 contracts/             # Solidity source files
│   │   └── HealthScheme.sol      # Main smart contract
│   ├── 📁 migrations/            # Deployment scripts
│   ├── truffle-config.js         # Truffle configuration
│   └── 📁 build/                 # Compiled contracts
├── 📁 frontend/                  # Web interface
│   ├── index.html                # Main HTML page
│   ├── app.js                    # Frontend JavaScript
│   └── styles.css                # CSS styling
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User authentication
- `GET /api/logout` - User logout

### Schemes Management
- `GET /api/schemes` - List all health schemes
- `GET /api/schemes/<id>` - Get specific scheme details

### Patient Operations
- `POST /api/patient-data/submit` - Submit medical records
- `POST /api/patient-data` - Retrieve patient records

### Hospital Operations
- `POST /api/hospital-profile` - Update hospital profile
- `POST /api/hospital-data` - Get assigned patient records

### Admin Operations
- `POST /api/admin/records` - Audit all system records

### Blockchain Integration
- `POST /api/store_on_chain` - Store record hash on blockchain

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'pkg_resources'"**
```bash
# Install setuptools
pip install setuptools==69.0.0
```

**"Flask-CORS module not found"**
```bash
pip install -r backend/requirements.txt
```

**"Contract not deployed"**
```bash
cd blockchain
truffle migrate --network development
# Update CONTRACT_ADDRESS in frontend/app.js
```

**Database connection issues**
```bash
cd backend/database
python init_db.py
python seed_db.py
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Commit** your changes: `git commit -m 'Add feature'`
4. **Push** to the branch: `git push origin feature-name`
5. **Submit** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Test thoroughly before submitting PRs
- Update documentation for new features


## 🙏 Acknowledgments

- **Government of India** for inspiring health scheme digitization
- **Ethereum Community** for blockchain technology
- **Open Source Contributors** for amazing tools and libraries

---

**Made with ❤️ for better healthcare accessibility**