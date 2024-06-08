const HDWalletProvider = require('@truffle/hdwallet-provider');

// URL test networks
// Local besu implementation
var besu_testnet = 'http://localhost:8454' // replace with the local besu RPC
// Ethereum Sepolia testnet -> use your API-KEY
var eth_sepolia_testnetwork = 'https://eth-sepolia.g.alchemy.com/v2/<API-KEY>'
// Polygon Amoy testnet -> use your API-KEY
var polygon_amoy_testnetwork = 'https://polygon-amoy.g.alchemy.com/v2/<API-KEY>'
// Optimism Sepolia -> use your API-KEY
var optimism_sepolia_testnet = 'https://opt-sepolia.g.alchemy.com/v2/<API-KEY>'
// IOTA Shimmer
var shimmer_testnet = 'https://json-rpc.evm.testnet.shimmer.network/' // this testnet doesn't require an API-KEY


// The private keys should be stored in another way
// Put in the following arrey the private keys used for deployment or load them from environment
var besuKey = ['<Private Key for Besu chain>'];
var ethereumKey = ['<Private Key for Ethereum Sepolia>']
var optimismKey = ['<Private Key for Optimism Sepolia>']
var polygonKey = ['<Private Key for Polygon Amoy>']
var iotaKey = ['<Private Key for IOTA Shimmer>']

module.exports = {
  /**
   * Networks define how you connect to your ethereum client and let you set the
   * defaults web3 uses to send transactions. You can ask a truffle command to use a specific
   * network from the command line, e.g
   *
   * $ truffle test --network <network-name>
   */

    networks: {
        // List of networks configured for deployment
        // Specify the network while running truffle migrate (e.g truffle migrate --reset --network=eth_sepolia)
        besu: { // network-name: besu
            provider: () => new HDWalletProvider(besuKey, besu_testnet),
            from: '<Public address related to besuKey>',
            network_id: 112233,       // Put the ID of the local besu blockchain
            gas: "0x1ffffffffffffe",  // besu configured as gas free. Replace with gas limit for a classic configuration
            gasPrice: "0",            // 0 for gas free. Check the current gas or remove it for classic consiguration
            websocket:false,          // enable deploy via websocket connection
            skipDryRun: true          // Skip dry run before migrations? (default: false for public nets)
        },

        eth_sepolia: { // network-name: eth_sepolia
            provider: () => new HDWalletProvider(ethereumKey, eth_sepolia_testnetwork),
            from: '<Public address related to ethereumKey>', // Put here the public address of the ethereumKey
            network_id: 11155111, // Ethereum Sepolia chain id
            gas: 5000000,         // gas limit
            confirmations: 1,     // # of confs to wait between deployments. (default: 0)
            timeoutBlocks: 200,   // # of blocks before a deployment times out  (minimum/default: 50)
            skipDryRun: false     // Skip dry run before migrations? (default: false for public nets)
       },

       eth_optimism: { // network-name: eth_optimism
            provider:() => new HDWalletProvider(optimismKey, optimism_sepolia_testnet),
            from: '<Public address related to optimismKey>', // Put here the public address of the optimismKey
            network_id: 11155420, // Optimism Sepolia chain id
            gas: 5000000,         // gas limit
            confirmations: 1,     // # of confirmations to wait between deployments. (default: 0)
            timeoutBlocks: 200,   // # of blocks before a deployment times out  (minimum/default: 50)
            skipDryRun: false     // Skip dry run before migrations? (default: false for public nets)
       },

       amoy: { // network-name: amoy
            provider:() => new HDWalletProvider(polygonKey, polygon_amoy_testnetwork),
            from: '<Public address related to polygonKey>',
            network_id: 80002,    // Polygon Amoy chain id
            gas: 5000000,         // gas limit
            confirmations: 1,     // # of confirmations to wait between deployments. (default: 0)
            timeoutBlocks: 200,   // # of blocks before a deployment times out  (minimum/default: 50)
            skipDryRun: false     // Skip dry run before migrations? (default: false for public nets)
       },

       shimmer: { // network-name; shimmer
            provider:() => new HDWalletProvider(iotaKey, shimmer_testnet),
            from: '<Public address related to iotaKey>',
            network_id: 1073,   // IOTA Shimmer chain id
            gas: 5000000,       // gas limit
            confirmations: 1,   // # of confirmations to wait between deployments. (default: 0)
            timeoutBlocks: 200, // # of blocks before a deployment times out  (minimum/default: 50)
            skipDryRun: false   // Skip dry run before migrations? (default: false for public nets)
       }

  },

    // Configure your compiler
    compilers: {
        solc: {
            version: "0.8.19",      // Fetch exact version from solc-bin (default: truffle's version)
            // docker: true,        // enable docker if needed
            settings: {             // See the solidity docs for advice about optimisation and evmVersion
                optimizer: {
                    enabled: true,  // Optimiser enabled: mandatory to use EllipticCurveMaths.sol
                    runs: 1000
                },
            //  evmVersion: "byzantium"
            }
        }
    },

  plugins: [
    'truffle-contract-size'
  ]
};
