const path = require('path');
const fs = require('fs');

const DataStroage = artifacts.require("DataStorage");
const SourceSmartContract = artifacts.require("SourceSmartContract");
const TargetSmartContract = artifacts.require("TargetSmartContract");
const EllipticCurveMaths = artifacts.require("EllipticCurveMaths");
const VerifyThresholdECDSA = artifacts.require("VerifyThresholdECDSA");
//const CompareECC = artifacts.require("CompareECC")

module.exports = async function (deployer, network) {
  console.log('Make deploy on Network: ', network);

  let deployTime = Date.now();
  console.log("Start time: ", deployTime);

  await deployer.deploy(DataStroage);
  await deployer.deploy(SourceSmartContract, DataStroage.address);
  await deployer.deploy(TargetSmartContract, DataStroage.address);
  await deployer.deploy(EllipticCurveMaths);
  await deployer.link(EllipticCurveMaths, VerifyThresholdECDSA);
  await deployer.deploy(VerifyThresholdECDSA, SourceSmartContract.address, TargetSmartContract.address);
  //await deployer.deploy(CompareECC);

  console.log('Total deploy time:');
  console.log(Date.now() - deployTime);

  //writeFile(network, VerifyThreshold.address, CompareECC.address);
  writeFile(network, VerifyThresholdECDSA.address, DataStroage.address, SourceSmartContract.address, TargetSmartContract.address, 'CompareECC.address');
}

function writeFile(network, verifyAddress, dataStroageAddress, sourceSmartContractAddress, targetSmartContractAddress, compareAddress) {
  let folderPath = path.resolve(__dirname, '..', 'contractAddresses', network);
  let content = {};
  try {
    if(!fs.existsSync(folderPath)){
      fs.mkdirSync(folderPath, {recursive:true});
    }
    if(!fs.existsSync(folderPath+'/addresses.json')) {
        fs.openSync(folderPath+'/addresses.json', 'w');
    }
    content["DataStorage"] = dataStroageAddress;
    content["SourceSmartContract"] = sourceSmartContractAddress;
    content["TargetSmartContract"] = targetSmartContractAddress;
    content["VerifyThreshold"] = verifyAddress;
    content["CompareECC"]= compareAddress;

    fs.writeFileSync(folderPath+'/addresses.json', JSON.stringify(content));
  }

  catch (err) {
    console.log(err);
  }
}
