# Healthink Project - Complete Setup Guide

## Project Architecture

**Healthink** is a full-stack health insurance scheme management system with three components:

1. **Backend (Flask)** - REST API for managing schemes
2. **Blockchain (Solidity)** - Smart contract for on-chain applications
3. **Frontend (JavaScript)** - Web interface for users

---

## Prerequisites

Before starting, ensure you have installed:
- **Node.js** (v14+) and **npm**
- **Python** (v3.8+)
- **Ganache CLI** or **Ganache GUI** (for local blockchain)
- **MetaMask** browser extension (for blockchain interaction)
- **Truffle** (for Solidity compilation and deployment)

---

## Step 1: Install Dependencies

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- Flask (Web framework)
- Flask-CORS (Cross-origin requests)
- Web3.py (Blockchain interaction)

### Blockchain Dependencies

```bash
cd blockchain
npm install -g truffle
npm install
```

---

## Step 2: Database Setup

Initialize and seed the database with health schemes:

```bash
cd backend/database
python init_db.py    # Creates the database
python seed_db.py    # Populates with schemes
```

This creates `healthink.db` with three schemes:
- Ayushman Bharat
- Jan Aushadhi
- Rashtriya Swasthya Bima Yojana

---

## Step 3: Start Ganache (Local Blockchain)

### Option A: Using Ganache GUI
1. Download from https://www.trufflesuite.com/ganache
2. Open the application
3. Create a new workspace (default settings work fine)
4. Ganache will run on `http://127.0.0.1:8545`

### Option B: Using Ganache CLI
```bash
npm install -g ganache-cli
ganache-cli
```

**Note:** Keep Ganache running in a separate terminal throughout the project!

---

## Step 4: Deploy Smart Contract

```bash
cd blockchain
truffle migrate --network development
```

**Output will show:**
- Deployment address of the `HealthScheme` contract (e.g., `0x5FbDB2315678afccb333f8a9c205eab7d4b3098C`)
- **IMPORTANT:** Copy this address and update it in `frontend/app.js` line 6:
  ```javascript
  const CONTRACT_ADDRESS = "0x5FbDB2315678afccb333f8a9c205eab7d4b3098C"; // Update here
  ```

---

## Step 5: Start the Backend Server

```bash
cd backend
python app.py
```

The Flask server will start at `http://localhost:5000`

**Available API Endpoints:**
- `GET /` - Health check
- `GET /api/health` - Health status
- `GET /api/schemes` - Get all schemes
- `GET /api/schemes/<id>` - Get specific scheme

---

## Step 6: Open Frontend in Browser

1. Open `frontend/index.html` in your browser
2. Or use a local HTTP server:
   ```bash
   cd frontend
   # Python 3
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

---

## Step 7: Complete the Workflow

### In Your Browser:

1. **Connect MetaMask**
   - Click "Connect Wallet" button
   - Select your Ganache account in MetaMask
   - Confirm the connection

2. **View Schemes**
   - The page displays all available health schemes
   - Each scheme shows ID, name, and details

3. **Apply for a Scheme**
   - Select a scheme from the dropdown
   - Click "Apply on Blockchain"
   - Confirm the transaction in MetaMask
   - Wait for confirmation

4. **View Your Application**
   - After applying, your application appears in "My Applications"
   - Shows scheme name, application date, and status

---

## Troubleshooting

### Issue: "Contract not initialized"
- **Solution:** Make sure the contract address in `frontend/app.js` line 6 matches your deployed contract address

### Issue: "MetaMask not connected"
- **Solution:** 
  1. Install MetaMask extension
  2. Click "Connect Wallet" button
  3. Add Ganache network to MetaMask (if not auto-detected)

### Issue: CORS errors
- **Solution:** Flask-CORS is already configured in `backend/app.py`

### Issue: "Failed to fetch schemes"
- **Solution:** 
  1. Ensure Flask backend is running on `http://localhost:5000`
  2. Check if database file exists: `backend/database/healthink.db`

### Issue: Transaction failed
- **Solution:**
  1. Check Ganache account balance (should have ETH)
  2. Ensure you're using a Ganache account in MetaMask
  3. Check browser console for detailed error

---

## Project Structure

```
Healthink/
├── backend/
│   ├── app.py                    # Flask API
│   ├── requirements.txt          # Python dependencies
│   └── database/
│       ├── init_db.py           # Database initialization
│       ├── seed_db.py           # Sample data
│       └── healthink.db         # SQLite database
├── blockchain/
│   ├── contracts/
│   │   └── HealthScheme.sol     # Smart contract
│   ├── migrations/
│   │   └── 1_deploy_health_scheme.js  # Deployment script
│   ├── truffle-config.js        # Truffle configuration
│   └── build/                    # Compiled contracts
├── frontend/
│   ├── index.html               # Web interface
│   ├── app.js                   # Frontend logic
│   └── styles.css               # Styling
└── README.md                    # Project documentation
```

---

## Next Steps / Enhancements

1. **Add more API endpoints:**
   - POST /api/applications - Submit application via backend
   - GET /api/applications/<user_address> - Fetch user applications
   - DELETE /api/applications/<id> - Cancel application

2. **Enhance smart contract:**
   - Add scheme cancellation
   - Add admin functions to manage schemes
   - Add approval workflow

3. **Improve frontend:**
   - Add authentication
   - Add user dashboard
   - Add transaction history

4. **Deploy to testnet:**
   - Use Sepolia or Mumbai testnet
   - Deploy contract to testnet
   - Update contract address

5. **Production deployment:**
   - Replace Flask with production WSGI server (Gunicorn)
   - Deploy frontend to static hosting (GitHub Pages, Vercel, etc.)
   - Deploy contract to mainnet

---

## Commands Summary

```bash
# Terminal 1: Ganache
ganache-cli

# Terminal 2: Deploy contract
cd blockchain
truffle migrate --network development

# Terminal 3: Backend server
cd backend
python app.py

# Terminal 4: Frontend server (optional)
cd frontend
python -m http.server 8000
```

Then open `index.html` in your browser!

---

## Support

For issues or questions, check:
1. Browser console (F12) for JavaScript errors
2. Terminal output for Python/backend errors
3. Ganache logs for blockchain issues
4. MetaMask extension for wallet issues
