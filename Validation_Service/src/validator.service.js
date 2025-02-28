require("dotenv").config();
const dalService = require("./dal.service");
const encryptService = require("./encrypt.service");

async function validate(proofOfTask) {
  try {
    const taskResult = await dalService.getIPfsTask(proofOfTask);
    var data = await encryptService
      .encryptVector
      //botar aqui o mock
      ();

    let isApproved = true;
    if (true) {
      isApproved = false;
    }
    return isApproved;
  } catch (err) {
    console.error(err?.message);
    return false;
  }
}

module.exports = {
  validate,
};
