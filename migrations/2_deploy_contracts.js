const path = require('path');
const fs = require('fs');

const EllipticCurveMaths = artifacts.require("EllipticCurveMaths");
const VerifyThresholdECDSA = artifacts.require("VerifyThresholdECDSA");

//const CompareECC = artifacts.require("CompareECC")

module.exports = async function (deployer, network) {
  console.log('Make deploy on Network: ', network);

  let verifyAddressContract;
  let compareECCAddressContract;

  let deployTime = Date.now();
  console.log("Start time: ", deployTime);

  await deployer.deploy(EllipticCurveMaths);
  await deployer.link(EllipticCurveMaths, VerifyThresholdECDSA);
  await deployer.deploy(VerifyThresholdECDSA);

  //await deployer.link(EllipticCurveMaths, CompareECC);
  //await deployer.deploy(CompareECC);

  console.log('Total deploy time:');
  console.log(Date.now() - deployTime);

  // To deploy the CompareECC smart contract check the imports
  writeFile(network, VerifyThresholdECDSA.address, 'CompareECC_Address');
  //writeFile(network, VerifyThresholdECDSA.address, CompareECC.address);

}

function writeFile(network, verifyECDSAAddress, compareAddress) {
  let folderPath = path.resolve(__dirname, '..', 'contractAddresses', network);
  let content = {};
  try {
    if(!fs.existsSync(folderPath)){
      fs.mkdirSync(folderPath, {recursive:true});
    }
    if(!fs.existsSync(folderPath+'/addresses.json')) {
        fs.openSync(folderPath+'/addresses.json', 'w');
    }
    content["VerifyThreshold"] = verifyECDSAAddress;
    content["CompareECC"]= compareAddress;
    fs.writeFileSync(folderPath+'/addresses.json', JSON.stringify(content));
  }

  catch (err) {
    console.log(err);
  }
}
