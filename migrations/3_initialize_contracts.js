const path = require('path');
const fs = require('fs');

const SourceSmartContract = artifacts.require("SourceSmartContract");
const TargetSmartContract = artifacts.require("TargetSmartContract");
const VerifyThresholdECDSA = artifacts.require("VerifyThresholdECDSA");

module.exports = async function (deployer, network) {
  console.log("Initializing smart contracts...");

  let contractAddresses = getContractAddresses(network);

  for (key in contractAddresses) {
      if (key == 'SourceSmartContract'){
        let SourceSmartContractInstance = await SourceSmartContract.at(contractAddresses[key]);
        await SourceSmartContractInstance.setVerifierSC(contractAddresses["VerifyThreshold"]);
      }
      if (key == 'TargetSmartContract') {
        let TargetSmartContractInstance = await TargetSmartContract.at(contractAddresses[key]);
        await TargetSmartContractInstance.setVerifierSC(contractAddresses["VerifyThreshold"]);
      }
    }
}

function getContractAddresses(network) {
  let folderPath = path.resolve(__dirname, '..', 'contractAddresses', network);

  try {

    let addresses = fs.readFileSync(folderPath+'/addresses.json');
    let addressesJson = JSON.parse(addresses);

    return addressesJson;
  }
  catch(err) {
    console.log(err);
  }
}
