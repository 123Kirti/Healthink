module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",     // Ganache host
      port: 8545,            // Ganache GUI default port
      network_id: "*"     // Ganache network id
    }
  },

  mocha: {
    // timeout: 100000
  },

  compilers: {
    solc: {
      version: "0.8.21"
    }
  }
};
